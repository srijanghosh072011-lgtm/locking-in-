"""SQLite state for the campaign.

One file, no server. Tracks who we contacted, when, at which sequence step, and
who must never be contacted again. The suppression table is the important one:
getting that wrong is what turns cold outreach into a complaint.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
  id            INTEGER PRIMARY KEY,
  business      TEXT NOT NULL,
  contact_name  TEXT DEFAULT '',
  email         TEXT NOT NULL UNIQUE,
  domain        TEXT DEFAULT '',
  phone         TEXT DEFAULT '',
  city          TEXT DEFAULT '',
  province      TEXT DEFAULT '',
  review_count  INTEGER DEFAULT 0,
  audit_score   INTEGER,
  audit_flags   TEXT DEFAULT '',
  audit_line    TEXT DEFAULT '',
  mockup        TEXT DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'new',   -- new|queued|active|replied|done|skipped
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id       INTEGER PRIMARY KEY,
  lead_id  INTEGER NOT NULL REFERENCES leads(id),
  kind     TEXT NOT NULL,          -- sent|replied|bounced|unsubscribed|error
  step     INTEGER,
  at       TEXT NOT NULL,
  detail   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS suppression (
  email   TEXT PRIMARY KEY,
  reason  TEXT NOT NULL,
  at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_lead ON events(lead_id);
CREATE INDEX IF NOT EXISTS idx_events_at   ON events(at);
"""


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def connect(path: pathlib.Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def suppress(con: sqlite3.Connection, email: str, reason: str) -> None:
    con.execute(
        "INSERT OR REPLACE INTO suppression(email, reason, at) VALUES (?,?,?)",
        (email.strip().lower(), reason, now()),
    )
    con.execute(
        "UPDATE leads SET status='skipped' WHERE lower(email)=?", (email.strip().lower(),)
    )
    con.commit()


def is_suppressed(con: sqlite3.Connection, email: str) -> bool:
    r = con.execute(
        "SELECT 1 FROM suppression WHERE email=?", (email.strip().lower(),)
    ).fetchone()
    return r is not None


def log(con: sqlite3.Connection, lead_id: int, kind: str, step: int | None, detail: str = "") -> None:
    con.execute(
        "INSERT INTO events(lead_id, kind, step, at, detail) VALUES (?,?,?,?,?)",
        (lead_id, kind, step, now(), detail),
    )
    con.commit()


def sent_today(con: sqlite3.Connection) -> int:
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    r = con.execute(
        "SELECT COUNT(*) c FROM events WHERE kind='sent' AND at LIKE ?", (today + "%",)
    ).fetchone()
    return r["c"]


def sending_day_index(con: sqlite3.Connection) -> int:
    """How many distinct days we've sent on. Drives the warm-up ramp."""
    r = con.execute(
        "SELECT COUNT(DISTINCT substr(at,1,10)) d FROM events WHERE kind='sent'"
    ).fetchone()
    return r["d"]


def last_step(con: sqlite3.Connection, lead_id: int) -> tuple[int, str] | None:
    r = con.execute(
        "SELECT step, at FROM events WHERE lead_id=? AND kind='sent' "
        "ORDER BY at DESC LIMIT 1",
        (lead_id,),
    ).fetchone()
    return (r["step"], r["at"]) if r else None
