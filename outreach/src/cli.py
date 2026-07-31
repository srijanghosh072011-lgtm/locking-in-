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
    from shoot import optimize_for_email, shoot

    rows = con.execute(
        "SELECT * FROM leads WHERE status='queued' AND (mockup='' OR mockup IS NULL)"
    ).fetchall()
    if not rows:
        print("no leads need a mockup")
        return 0

    MOCKUPS.mkdir(exist_ok=True)
    for r in rows:
        out = MOCKUPS / f"{slugify(r['business'])}.png"
        try:
            shoot(
                args.template_url,
                out,
                preset="desktop",
                personalize_cfg=build_config(r["business"], r["city"], r["phone"]),
            )
            final = optimize_for_email(out, cfg["sending"]["max_image_kb"])
            con.execute("UPDATE leads SET mockup=? WHERE id=?", (str(final), r["id"]))
            print(f"  {final.name}  ({final.stat().st_size/1024:.0f} KB)")
        except Exception as e:
            print(f"  ! {r['business']}: {type(e).__name__}: {e}")
    con.commit()
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


def cmd_send(args, cfg, con) -> int:
    steps = {s["n"]: s for s in cfg["sequence"]["steps"]}
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
    pw = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
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
    p.add_argument(
        "--template-url",
        default="http://127.0.0.1:8899/plumbing-Templates-/",
        help="URL of the demo template to personalize",
    )
    p.set_defaults(fn=cmd_mockups)

    p = sub.add_parser("send", help="send whatever is due")
    p.add_argument("--dry-run", action="store_true", help="print emails, send nothing")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--ignore-window", action="store_true")
    p.set_defaults(fn=cmd_send)

    p = sub.add_parser("replies", help="scan inbox and stop sequences")
    p.add_argument("--days", type=int, default=14)
    p.set_defaults(fn=cmd_replies)

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
