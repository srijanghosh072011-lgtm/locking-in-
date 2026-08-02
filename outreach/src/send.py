"""SMTP delivery with the guardrails that keep a Gmail account alive.

Three things matter more than volume:
  * the warm-up ramp (a new account sending 50 cold emails on day one gets
    filtered, and filtered mail never recovers on its own),
  * pacing inside business hours rather than 50 messages in one burst,
  * stopping the sequence the instant someone replies.
"""

from __future__ import annotations

import datetime as dt
import os
import random
import re
import smtplib
import ssl
import time
from zoneinfo import ZoneInfo

import db


class SendBlocked(RuntimeError):
    """Raised when the schedule says we should not be sending right now."""


def daily_allowance(cfg: dict, con) -> int:
    """Where we are on the warm-up ramp, capped by daily_cap."""
    s = cfg["sending"]
    ramp = s.get("warmup") or []
    day = db.sending_day_index(con)  # days already sent on
    if day < len(ramp):
        return min(ramp[day], s["daily_cap"])
    return s["daily_cap"]


def within_window(cfg: dict, when: dt.datetime | None = None) -> tuple[bool, str]:
    s = cfg["sending"]
    tz = ZoneInfo(s["timezone"])
    now = (when or dt.datetime.now(tz)).astimezone(tz)
    if now.isoweekday() not in s["send_days"]:
        return False, f"{now:%A} is not a sending day (send_days={s['send_days']})"
    if not (s["send_window_start"] <= now.hour < s["send_window_end"]):
        return False, (
            f"{now:%H:%M} is outside the "
            f"{s['send_window_start']:02d}:00–{s['send_window_end']:02d}:00 window"
        )
    return True, ""


def connect(cfg: dict) -> smtplib.SMTP:
    password = re.sub(r"\s+", "", os.environ.get("GMAIL_APP_PASSWORD", ""))
    if not password:
        raise SendBlocked(
            "GMAIL_APP_PASSWORD is not set — copy .env.example to .env and fill it in"
        )
    m = cfg["smtp"]
    srv = smtplib.SMTP(m["host"], m["port"], timeout=30)
    srv.starttls(context=ssl.create_default_context())
    srv.login(m["user"], password)
    return srv


def deliver(srv: smtplib.SMTP | None, msg, dry_run: bool) -> str:
    if dry_run or srv is None:
        return "dry-run"
    srv.send_message(msg)
    return "sent"


def sleep_between(cfg: dict) -> int:
    s = cfg["sending"]
    gap = random.randint(s["min_gap_seconds"], s["max_gap_seconds"])
    time.sleep(gap)
    return gap
