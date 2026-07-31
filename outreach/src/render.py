"""Turn a template + a lead into a ready-to-send MIME message.

Templates are plain text with a `Subject:` line, a `---` separator, and a body.
The HTML part is generated from that same text so the two never drift apart.

Deliberately plain: no tracking pixel, no link shorteners, no image-only email.
Those are the three things that most reliably put cold mail in spam, and an open
rate is worth less than landing in the inbox.
"""

from __future__ import annotations

import html
import pathlib
import re
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

TOKEN = re.compile(r"\{\{(\w+)\}\}")


class MissingToken(KeyError):
    """Raised rather than sending an email containing a literal {{token}}."""


def parse_template(path: pathlib.Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")
    subject, _, body = raw.partition("\n---\n")
    if not body:
        raise ValueError(f"{path.name}: expected a '---' line after Subject:")
    subject = subject.strip()
    if not subject.lower().startswith("subject:"):
        raise ValueError(f"{path.name}: first line must start with 'Subject:'")
    return subject[len("subject:"):].strip(), body.strip("\n")


def fill(text: str, ctx: dict[str, str]) -> str:
    missing: list[str] = []

    def sub(m: re.Match) -> str:
        k = m.group(1)
        v = ctx.get(k)
        if v is None or str(v).strip() == "":
            missing.append(k)
            return m.group(0)
        return str(v)

    out = TOKEN.sub(sub, text)
    if missing:
        raise MissingToken(
            f"unresolved token(s): {', '.join(sorted(set(missing)))}"
        )
    return out


def casl_footer(cfg: dict, unsubscribe_mailto: str) -> str:
    """Canada's anti-spam law requires sender identity, a mailing address and a
    working unsubscribe in every commercial message. Not optional, and it costs
    nothing — see README 'Legal'."""
    s = cfg["sender"]
    return (
        f"{s['company']} — {s['mailing_address']}\n"
        f"You received this at your business address. "
        f"Reply STOP or email {unsubscribe_mailto} and I'll remove you immediately."
    )


def to_html(body: str, footer: str, image_cid: str | None) -> str:
    def hard(p: str) -> str:
        return html.escape(p).replace("\n", "<br>")

    def esc_para(p: str) -> str:
        """Reflow prose, but keep real line breaks.

        Templates are hard-wrapped at ~78 chars for the plain-text part. Turning
        every one of those newlines into <br> freezes desktop line lengths into
        the HTML, which reads badly on a phone. Blocks whose lines are all short
        (signatures, addresses, numbered lists) are intentional breaks and keep
        them; anything else is wrapped prose and gets joined back together.
        """
        lines = [ln.strip() for ln in p.split("\n")]
        intentional = all(len(ln) < 45 for ln in lines) or any(
            ln.lstrip().startswith(("1.", "2.", "3.", "-", "*", "•"))
            for ln in p.split("\n")
        )
        return hard(p) if intentional else html.escape(" ".join(lines))

    blocks = []
    if image_cid:
        blocks.append(
            f'<img src="cid:{image_cid}" alt="Homepage concept" '
            'style="width:100%;max-width:560px;height:auto;'
            'border-radius:8px;border:1px solid #e5e5e5;margin:0 0 20px">'
        )
    for para in re.split(r"\n\s*\n", body.strip()):
        blocks.append(f'<p style="margin:0 0 16px">{esc_para(para)}</p>')
    blocks.append(
        '<hr style="border:none;border-top:1px solid #e5e5e5;margin:24px 0 12px">'
        f'<p style="margin:0;color:#777;font-size:12px;line-height:1.5">'
        f'{hard(footer)}</p>'
    )
    return (
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;'
        'font-size:15px;line-height:1.6;color:#222;max-width:560px">'
        + "".join(blocks)
        + "</div>"
    )


def build(
    cfg: dict,
    lead: dict,
    template_path: pathlib.Path,
    image: pathlib.Path | None = None,
) -> EmailMessage:
    s = cfg["sender"]
    unsub = s.get("reply_to") or s["email"]

    ctx = {
        "business": lead["business"],
        "first_name": lead.get("contact_name") or "there",
        "city": lead.get("city", ""),
        "audit_line": lead.get("audit_line", ""),
        "sender_name": s["name"],
        "sender_city": s["city"],
        "sender_province": s.get("province", ""),
        "sender_phone": s.get("phone", ""),
        "demo_link": s.get("demo_link", ""),
        "company": s["company"],
        "website": s["website"],
        "booking_link": s["booking_link"],
    }

    subject, body = parse_template(template_path)
    subject = fill(subject, ctx)
    body = fill(body, ctx)
    footer = casl_footer(cfg, unsub)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((f"{s['name']} — {s['company']}", s["email"]))
    msg["To"] = lead["email"]
    if s.get("reply_to"):
        msg["Reply-To"] = s["reply_to"]
    # One-click unsubscribe signals. Gmail weighs these; they also keep an
    # annoyed recipient from reaching for the spam button instead.
    msg["List-Unsubscribe"] = f"<mailto:{unsub}?subject=unsubscribe>"
    msg["Message-ID"] = make_msgid(domain=s["email"].split("@")[-1])

    msg.set_content(body + "\n\n--\n" + footer)

    cid = None
    if image and image.exists():
        # Same domain as the sender: a Content-ID of @localhost looks synthetic
        # to filters.
        cid = make_msgid(domain=s["email"].split("@")[-1])[1:-1]
    msg.add_alternative(to_html(body, footer, cid), subtype="html")

    if cid:
        subtype = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png"}.get(
            image.suffix.lower(), "png"
        )
        html_part = msg.get_payload()[-1]
        html_part.add_related(
            image.read_bytes(), "image", subtype, cid=f"<{cid}>", filename=image.name
        )

    return msg
