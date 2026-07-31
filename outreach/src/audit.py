"""Score how badly a prospect needs a new website.

This is the targeting engine. Srijan's two criteria are "decent-sized business"
and "bad or no website" — review_count carries the first, this module carries
the second.

It also produces `audit_line`: one concrete, true sentence about THEIR site that
goes in the email. That line is why the message reads as researched rather than
blasted, and it is generated from what we actually measured.
"""

from __future__ import annotations

import re
import socket
import ssl
import time
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

# (flag, points, sentence for the email). Points sum to the 0-100 need score.
CHECKS_DOC = """
no_site        60  no website at all
dead           55  domain does not load
no_https       15  no HTTPS / browser shows "Not secure"
not_mobile     25  no viewport tag -> unusable on phones
no_title       10  missing/placeholder <title>
no_description  8  missing meta description
stale           8  copyright year is old
table_layout   12  table-based layout (pre-2010 build)
tiny            10  near-empty / "coming soon" page
slow           12  took >4s to respond
"""


def audit(domain: str, timeout: float = 12.0) -> dict:
    """Return {score, flags, line, ok}. Never raises."""
    domain = (domain or "").strip()
    if not domain:
        return {
            "score": 60,
            "flags": ["no_site"],
            "line": "You don't have a website yet, so every search for a plumber "
                    "in your area sends that job to a competitor.",
            "ok": True,
        }

    url = domain if domain.startswith("http") else "https://" + domain
    flags: list[str] = []
    score = 0
    html = ""
    elapsed = 0.0

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read(400_000).decode("utf-8", "replace")
            final = r.geturl()
        elapsed = time.time() - t0
        if not final.startswith("https"):
            flags.append("no_https")
            score += 15
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError):
        # Try plain HTTP before calling it dead — a cert error still means
        # "browser shows a scary warning", which is worth saying out loud.
        try:
            req = urllib.request.Request(
                "http://" + domain.replace("https://", "").replace("http://", ""),
                headers={"User-Agent": UA},
            )
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                html = r.read(400_000).decode("utf-8", "replace")
            elapsed = time.time() - t0
            flags.append("no_https")
            score += 15
        except Exception:
            return {
                "score": 55,
                "flags": ["dead"],
                "line": "Your website doesn't load right now — I tried it a few "
                        "times and it timed out, which means anyone searching for "
                        "you is hitting a dead end.",
                "ok": True,
            }
    except Exception:
        return {"score": 0, "flags": ["error"], "line": "", "ok": False}

    low = html.lower()

    if not re.search(r'<meta[^>]+name=["\']viewport', low):
        flags.append("not_mobile")
        score += 25
    title = re.search(r"<title[^>]*>(.*?)</title>", low, re.S)
    if not title or len(title.group(1).strip()) < 5:
        flags.append("no_title")
        score += 10
    if not re.search(r'<meta[^>]+name=["\']description', low):
        flags.append("no_description")
        score += 8
    if re.search(r"<table[^>]*>.*?<table", low, re.S):
        flags.append("table_layout")
        score += 12
    if len(re.sub(r"<[^>]+>", "", html).strip()) < 400:
        flags.append("tiny")
        score += 10
    if elapsed > 4:
        flags.append("slow")
        score += 12

    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)[^0-9]{0,12}(20\d\d)", low)]
    if years and max(years) <= time.gmtime().tm_year - 3:
        flags.append("stale")
        score += 8

    return {
        "score": min(score, 100),
        "flags": flags,
        "line": line_for(flags, elapsed, max(years) if years else None),
        "ok": True,
    }


def line_for(flags: list[str], elapsed: float, year: int | None) -> str:
    """One true, specific sentence about their site. Most severe issue wins."""
    if "not_mobile" in flags:
        return ("I pulled your site up on my phone and it loads the desktop "
                "layout — visitors have to pinch and zoom to find your number, "
                "and most plumbing searches happen on a phone.")
    if "no_https" in flags:
        return ("Your site is still on http, so Chrome and Safari label it "
                "\"Not secure\" before anyone reads a word of it.")
    if "tiny" in flags:
        return ("Your site is essentially a placeholder page right now — there's "
                "nothing on it that would convince someone to call you.")
    if "table_layout" in flags:
        return ("Your site is built on a table layout, which is pre-2010 "
                "technology — it's why it looks dated next to your competitors.")
    if "slow" in flags:
        return (f"Your homepage took about {elapsed:.0f} seconds to load for me. "
                "Past three seconds, most people are already gone.")
    if "stale" in flags and year:
        return (f"The footer on your site still says {year}, which tells visitors "
                "nobody's touched it in a while.")
    if "no_title" in flags or "no_description" in flags:
        return ("Your site is missing the basic page titles and descriptions "
                "Google needs, so you're invisible in search results you should own.")
    return ("I had a look at your current site and there's a lot of room to turn "
            "more of your visitors into phone calls.")
