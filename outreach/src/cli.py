"""Campaign CLI.

Daily loop once set up:

    python3 src/cli.py import leads.csv     # add prospects
    python3 src/cli.py audit                # score their current sites
    python3 src/cli.py mockups              # render a mockup per qualified lead
    python3 src/cli.py send --dry-run       # read the exact emails first
    python3 src/cli.py send                 # go
    python3 src/cli.py replies              # stop sequences for anyone who wrote back
    python3 src/cli.py status
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import email
import imaplib
import os
import pathlib
import re
import sys
import tomllib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import audit as audit_mod
import db
import render
import send as send_mod
from personalize import build_config, slugify

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DB_PATH = ROOT / "data" / "campaign.db"
TEMPLATES = ROOT / "templates"
MOCKUPS = ROOT / "mockups"


def load_cfg() -> dict:
    with open(CONFIG, "rb") as f:
        return tomllib.load(f)


def load_env() -> None:
    """Minimal .env reader so there's no python-dotenv dependency."""
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------- import ----
def cmd_import(args, cfg, con) -> int:
    added = skipped = 0
    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            e = (row.get("email") or "").strip().lower()
            if not e or "@" not in e:
                skipped += 1
                continue
            if db.is_suppressed(con, e):
                skipped += 1
                continue
            try:
                con.execute(
                    "INSERT INTO leads(business, contact_name, email, domain, phone,"
                    " city, province, review_count, created_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        (row.get("business") or "").strip(),
                        (row.get("contact_name") or "").strip(),
                        e,
                        (row.get("domain") or "").strip(),
                        (row.get("phone") or "").strip(),
                        (row.get("city") or "").strip(),
                        (row.get("province") or "").strip(),
                        int(row.get("review_count") or 0),
                        db.now(),
                    ),
                )
                added += 1
            except Exception:
                skipped += 1  # duplicate email
    con.commit()
    print(f"imported {added}, skipped {skipped}")
    return 0


# ----------------------------------------------------------------- audit ----
def cmd_audit(args, cfg, con) -> int:
    q = cfg["qualifying"]
    rows = con.execute(
        "SELECT * FROM leads WHERE audit_score IS NULL AND status='new'"
    ).fetchall()
    print(f"auditing {len(rows)} lead(s)…")
    for r in rows:
        res = audit_mod.audit(r["domain"])
        if not res["ok"]:
            continue
        qualifies = (
            res["score"] >= q["min_audit_score"]
            and r["review_count"] >= q["min_review_count"]
        )
        con.execute(
            "UPDATE leads SET audit_score=?, audit_flags=?, audit_line=?, status=?"
            " WHERE id=?",
            (
                res["score"],
                ",".join(res["flags"]),
                res["line"],
                "queued" if qualifies else "skipped",
                r["id"],
            ),
        )
        mark = "OK " if qualifies else "-- "
        print(f"  {mark}{r['business'][:34]:34} score={res['score']:3}"
              f" reviews={r['review_count']:4} {','.join(res['flags'])}")
    con.commit()
    n = con.execute("SELECT COUNT(*) c FROM leads WHERE status='queued'").fetchone()["c"]
    print(f"{n} lead(s) queued")
    return 0


# --------------------------------------------------------------- mockups ----
def cmd_mockups(args, cfg, con) -> int:
    from serve import serve
    from shoot import optimize_for_email, shoot

    rows = con.execute(
        "SELECT * FROM leads WHERE status='queued' AND (mockup='' OR mockup IS NULL)"
    ).fetchall()
    if not rows:
        print("no leads need a mockup")
        return 0

    MOCKUPS.mkdir(exist_ok=True)
    tpl = cfg["template"]
    tpl_dir = (ROOT / tpl["dir"]).resolve() if not pathlib.Path(tpl["dir"]).is_absolute() \
        else pathlib.Path(tpl["dir"])

    with serve(tpl_dir, tpl["base_path"]) as url:
        print(f"serving template from {tpl_dir}")
        for r in rows:
            out = MOCKUPS / f"{slugify(r['business'])}.png"
            try:
                shoot(
                    url,
                    out,
                    preset="desktop",
                    personalize_cfg=build_config(r["business"], r["city"], r["phone"]),
                )
                final = optimize_for_email(out, cfg["sending"]["max_image_kb"])
                con.execute(
                    "UPDATE leads SET mockup=? WHERE id=?", (str(final), r["id"])
                )
                print(f"  {final.name}  ({final.stat().st_size/1024:.0f} KB)")
            except Exception as e:
                print(f"  ! {r['business']}: {type(e).__name__}: {e}")
    con.commit()
    return 0


def cmd_daily(args, cfg, con) -> int:
    """One command for cron: score, draw, catch replies, then send.

    Replies are processed *before* sending so anyone who wrote back overnight
    drops out of the sequence instead of getting the next step anyway.
    """
    steps = [
        ("audit", cmd_audit),
        ("mockups", cmd_mockups),
        ("replies", cmd_replies),
        ("send", cmd_send),
    ]
    for name, fn in steps:
        print(f"\n=== {name} " + "=" * (60 - len(name)))
        try:
            rc = fn(args, cfg, con)
        except Exception as e:
            print(f"  ! {name} failed: {type(e).__name__}: {e}")
            # A screenshot or IMAP hiccup must not stop the send, but a failing
            # send is the whole job — stop there so the error is noticed.
            if name == "send":
                return 1
            continue
        if name == "send" and rc != 0:
            return rc
    return 0


# ------------------------------------------------------------------ send ----
def eligible(cfg, con) -> list[tuple[dict, int]]:
    """(lead, step) pairs due right now, respecting per-step delays."""
    steps = {s["n"]: s for s in cfg["sequence"]["steps"]}
    out = []
    rows = con.execute(
        "SELECT * FROM leads WHERE status IN ('queued','active') ORDER BY id"
    ).fetchall()
    now = dt.datetime.now(dt.timezone.utc)
    for r in rows:
        if db.is_suppressed(con, r["email"]):
            continue
        last = db.last_step(con, r["id"])
        nxt = 1 if last is None else last[0] + 1
        if nxt not in steps:
            con.execute("UPDATE leads SET status='done' WHERE id=?", (r["id"],))
            continue
        if last is not None:
            due = dt.datetime.fromisoformat(last[1]) + dt.timedelta(
                days=steps[nxt]["delay_days"]
            )
            if now < due:
                continue
        out.append((dict(r), nxt))
    con.commit()
    return out


def unfilled(cfg: dict) -> list[str]:
    """Config values still carrying a TODO placeholder.

    A placeholder mailing address is a CASL violation and a TODO phone number
    destroys the trust the email is trying to build, so a real send is blocked
    until these are filled. Dry runs still work, so the copy can be read first.
    """
    return [
        f"{section}.{k}"
        for section in ("sender", "template")
        for k, v in cfg.get(section, {}).items()
        if isinstance(v, str) and "TODO" in v
    ]


def cmd_send(args, cfg, con) -> int:
    steps = {s["n"]: s for s in cfg["sequence"]["steps"]}
    if not args.dry_run:
        todo = unfilled(cfg)
        if todo:
            print("not sending — config.toml still has placeholders:")
            for k in todo:
                print(f"  {k}")
            print("fill these in, or use --dry-run to preview the copy.")
            return 1
    ok, why = send_mod.within_window(cfg)
    if not ok and not args.ignore_window and not args.dry_run:
        print(f"not sending: {why}")
        print("(use --ignore-window to override, or --dry-run to preview)")
        return 1

    allowance = send_mod.daily_allowance(cfg, con)
    already = db.sent_today(con)
    budget = max(0, min(allowance, cfg["sending"]["daily_cap"]) - already)
    if args.limit:
        budget = min(budget, args.limit)

    queue = eligible(cfg, con)[:budget]
    print(
        f"ramp allowance {allowance}/day · already sent today {already} · "
        f"budget now {budget} · due {len(queue)}"
    )
    if not queue:
        return 0

    srv = None
    if not args.dry_run:
        srv = send_mod.connect(cfg)

    sent = 0
    try:
        for i, (lead, step) in enumerate(queue):
            tpl = TEMPLATES / f"{steps[step]['template']}.txt"
            img = None
            if step == 1 and cfg["sending"]["embed_image"] and lead.get("mockup"):
                p = pathlib.Path(lead["mockup"])
                if p.exists():
                    img = p
            try:
                msg = render.build(cfg, lead, tpl, img)
            except render.MissingToken as e:
                print(f"  ! skip {lead['email']}: {e}")
                db.log(con, lead["id"], "error", step, str(e))
                continue

            result = send_mod.deliver(srv, msg, args.dry_run)
            if args.dry_run:
                print("\n" + "=" * 68)
                print(f"To: {msg['To']}   (step {step})")
                print(f"Subject: {msg['Subject']}")
                if img:
                    print(f"[inline image: {img.name}]")
                print("-" * 68)
                print(msg.get_body(("plain",)).get_content().strip())
            else:
                db.log(con, lead["id"], "sent", step)
                con.execute(
                    "UPDATE leads SET status='active' WHERE id=?", (lead["id"],)
                )
                con.commit()
                print(f"  {result} step {step} -> {lead['email']}")
            sent += 1

            if not args.dry_run and i < len(queue) - 1:
                gap = send_mod.sleep_between(cfg)
                print(f"    …waiting {gap}s")
    finally:
        if srv:
            srv.quit()

    print(f"\n{'previewed' if args.dry_run else 'sent'} {sent}")
    return 0


# --------------------------------------------------------------- replies ----
def cmd_replies(args, cfg, con) -> int:
    """Mark anyone who wrote back as replied so the sequence stops."""
    load_env()
    pw = re.sub(r"\s+", "", os.environ.get("GMAIL_APP_PASSWORD", ""))
    if not pw:
        print("GMAIL_APP_PASSWORD not set")
        return 1
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(cfg["smtp"]["user"], pw)
    m.select("INBOX")
    since = (dt.date.today() - dt.timedelta(days=args.days)).strftime("%d-%b-%Y")
    _, data = m.search(None, f'(SINCE {since})')
    ids = data[0].split()
    known = {
        r["email"]: r["id"]
        for r in con.execute(
            "SELECT id, email FROM leads WHERE status IN ('active','queued')"
        )
    }
    hits = 0
    for i in ids:
        _, raw = m.fetch(i, "(RFC822.HEADER)")
        msg = email.message_from_bytes(raw[0][1])
        frm = email.utils.parseaddr(msg.get("From", ""))[1].lower()
        subj = (msg.get("Subject") or "").lower()
        if frm in known:
            lead_id = known[frm]
            if any(w in subj for w in ("unsubscribe", "stop", "remove")):
                db.suppress(con, frm, "requested via reply")
                db.log(con, lead_id, "unsubscribed", None, subj[:120])
                print(f"  unsubscribed {frm}")
            else:
                con.execute("UPDATE leads SET status='replied' WHERE id=?", (lead_id,))
                db.log(con, lead_id, "replied", None, subj[:120])
                print(f"  replied {frm}: {subj[:60]}")
            hits += 1
    con.commit()
    m.logout()
    print(f"{hits} reply event(s)")
    return 0


# ------------------------------------------------------- status / suppress ---
TEMPLATE_REPO = "https://github.com/srijanghosh072011-lgtm/plumbing-templates-"
TEMPLATE_BRANCH = "claude/site-replica-seo-aeo-phglx9"
VENDOR = ROOT / "vendor" / "plumbing-template"


def cmd_fetch_template(args, cfg, con) -> int:
    """Pull the built demo site locally so [template] dir needs no manual clone."""
    import shutil
    import subprocess

    if VENDOR.exists() and not args.force:
        print(f"already present: {VENDOR}  (use --force to re-fetch)")
        return 0
    if VENDOR.exists():
        shutil.rmtree(VENDOR)
    VENDOR.parent.mkdir(parents=True, exist_ok=True)

    print(f"fetching {TEMPLATE_BRANCH} …")
    r = subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", TEMPLATE_BRANCH,
         TEMPLATE_REPO, str(VENDOR)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr.strip()[-600:])
        return 1

    docs = VENDOR / "docs"
    if not (docs / "index.html").exists():
        print(f"! clone succeeded but no docs/index.html in {VENDOR}")
        return 1
    configured = pathlib.Path(cfg["template"]["dir"])
    if not configured.is_absolute():
        configured = (ROOT / configured).resolve()
    if configured == docs.resolve():
        print(f"ok — {docs} (already what config.toml points at)")
    else:
        print(f"ok — now set [template] dir = \"{docs}\" in config.toml")
    return 0


def _check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"  [{'ok' if ok else 'XX'}] {label}" + (f" — {detail}" if detail else ""))
    return ok


def cmd_doctor(args, cfg, con) -> int:
    """Check every prerequisite and say precisely what to fix.

    Exists because the failure modes here are all silent-ish: a missing browser,
    an app password with spaces in it, a stale template path. Better to find
    them on purpose than halfway through a send.
    """
    import shutil

    fails = 0
    print("dependencies")
    try:
        import playwright  # noqa: F401
        _check("playwright installed", True)
    except ImportError:
        fails += not _check("playwright installed", False, "pip install -r requirements.txt")
    try:
        from PIL import Image  # noqa: F401
        _check("pillow installed", True)
    except ImportError:
        fails += not _check("pillow installed", False, "pip install -r requirements.txt")

    browser_ok = False
    try:
        from shoot import CHROMIUM
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            launch = {"args": ["--no-sandbox"]}
            if pathlib.Path(CHROMIUM).exists():
                launch["executable_path"] = CHROMIUM
            b = p.chromium.launch(**launch)
            b.close()
        browser_ok = True
    except Exception as e:
        detail = f"{type(e).__name__} — run: playwright install chromium"
    fails += not _check("chromium launches", browser_ok,
                        "" if browser_ok else detail)

    print("\nconfig")
    todo = unfilled(cfg)
    fails += not _check("no TODO placeholders", not todo,
                        ", ".join(todo) if todo else "")

    tpl = pathlib.Path(cfg["template"]["dir"]).expanduser()
    if not tpl.is_absolute():
        tpl = (ROOT / tpl).resolve()
    ok = (tpl / "index.html").exists()
    fails += not _check("template site present", ok,
                        str(tpl) if ok else f"{tpl} has no index.html — try: "
                        "python3 src/cli.py fetch-template")

    print("\ncredentials")
    load_env()
    pw = re.sub(r"\s+", "", os.environ.get("GMAIL_APP_PASSWORD", ""))
    fails += not _check(".env has GMAIL_APP_PASSWORD", bool(pw),
                        "" if pw else "cp .env.example .env, then fill it in")
    if pw and len(pw) != 16:
        _check("app password looks like 16 chars", False,
               f"got {len(pw)} — that's probably your account password, not an "
               "App Password from myaccount.google.com/apppasswords")

    if pw and args.network:
        import smtplib
        import ssl
        try:
            s = smtplib.SMTP(cfg["smtp"]["host"], cfg["smtp"]["port"], timeout=20)
            s.starttls(context=ssl.create_default_context())
            s.login(cfg["smtp"]["user"], pw)
            s.quit()
            _check("SMTP login", True)
        except Exception as e:
            fails += not _check("SMTP login", False, f"{type(e).__name__}: {e}")

    print("\ncampaign")
    counts = {r["status"]: r["c"] for r in con.execute(
        "SELECT status, COUNT(*) c FROM leads GROUP BY status")}
    _check("leads imported", bool(counts), str(counts) if counts else
           "python3 src/cli.py import leads.csv")
    ok, why = send_mod.within_window(cfg)
    _check("send window open now", ok, "" if ok else why)
    print(f"\n{'all clear' if not fails else str(fails) + ' thing(s) to fix'}")
    return 1 if fails else 0


def cmd_status(args, cfg, con) -> int:
    print(f"allowance today : {send_mod.daily_allowance(cfg, con)}"
          f" (cap {cfg['sending']['daily_cap']})")
    print(f"sent today      : {db.sent_today(con)}")
    print(f"sending days    : {db.sending_day_index(con)}")
    ok, why = send_mod.within_window(cfg)
    print(f"window          : {'open' if ok else 'closed — ' + why}")
    print("\nleads by status:")
    for r in con.execute(
        "SELECT status, COUNT(*) c FROM leads GROUP BY status ORDER BY c DESC"
    ):
        print(f"  {r['status']:9} {r['c']}")
    print("\nevents:")
    for r in con.execute(
        "SELECT kind, COUNT(*) c FROM events GROUP BY kind ORDER BY c DESC"
    ):
        print(f"  {r['kind']:12} {r['c']}")
    n = con.execute("SELECT COUNT(*) c FROM suppression").fetchone()["c"]
    print(f"\nsuppressed: {n}")
    return 0


def cmd_suppress(args, cfg, con) -> int:
    db.suppress(con, args.email, args.reason)
    print(f"suppressed {args.email}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="outreach")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("import", help="load leads from CSV")
    p.add_argument("csv_path")
    p.set_defaults(fn=cmd_import)

    p = sub.add_parser("audit", help="score each lead's current site")
    p.set_defaults(fn=cmd_audit)

    p = sub.add_parser("mockups", help="render a personalized mockup per lead")
    p.set_defaults(fn=cmd_mockups)

    p = sub.add_parser("daily", help="audit + mockups + replies + send (for cron)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--ignore-window", action="store_true")
    p.add_argument("--days", type=int, default=14)
    p.set_defaults(fn=cmd_daily)

    p = sub.add_parser("send", help="send whatever is due")
    p.add_argument("--dry-run", action="store_true", help="print emails, send nothing")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--ignore-window", action="store_true")
    p.set_defaults(fn=cmd_send)

    p = sub.add_parser("replies", help="scan inbox and stop sequences")
    p.add_argument("--days", type=int, default=14)
    p.set_defaults(fn=cmd_replies)

    p = sub.add_parser("doctor", help="check everything and say what to fix")
    p.add_argument("--network", action="store_true",
                   help="also try a real SMTP login")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("fetch-template", help="download the demo site locally")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_fetch_template)

    p = sub.add_parser("status")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("suppress", help="never contact this address again")
    p.add_argument("email")
    p.add_argument("--reason", default="manual")
    p.set_defaults(fn=cmd_suppress)

    args = ap.parse_args()
    load_env()
    cfg = load_cfg()
    con = db.connect(DB_PATH)
    return args.fn(args, cfg, con)


if __name__ == "__main__":
    raise SystemExit(main())
