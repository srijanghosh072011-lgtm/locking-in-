"""Stamp a prospect's business into the demo template, then screenshot it.

A generic demo gets "nice template, not interested". The same mockup with the
prospect's own name in the nav and their city in the headline gets replies,
because it reads as work already done rather than a brochure.

Substitution happens in the live DOM *after* the page hydrates, not by rewriting
index.html. Rewriting the static export desyncs React's hydration and the app
blanks the page — the personalized markup renders to an empty white screenshot.
Editing the settled DOM sidesteps hydration entirely.
"""

from __future__ import annotations

import re
import unicodedata

DEMO_BRAND_FULL = "Coldsnap Plumbing & Heating"
DEMO_BRAND = "Coldsnap"
DEMO_CITY = "Regina"
DEMO_PHONE = "(306) 555-0142"

# Runs against the settled DOM. Text nodes plus the attributes that surface as
# visible text (alt/aria-label/title) and the click-to-call links.
PERSONALIZE_JS = """
(cfg) => {
  // The banner declares the demo business fictional. Once the mockup carries a
  // real prospect's name that sentence is simply wrong, so it goes. Honesty
  // about this being a concept lives in the email copy instead.
  // Match ONLY the banner element. A broader selector (e.g. .no-print) also
  // matches the <header> that wraps it, whose textContent contains the banner
  // text too — removing that takes the whole nav out of the shot.
  document.querySelectorAll('[role="note"]').forEach(el => {
    if (/Demo site/i.test(el.textContent || '')) el.remove();
  });

  const apply = (s) => {
    if (!s) return s;
    for (const [from, to] of cfg.pairs) s = s.split(from).join(to);
    return s;
  };

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    const next = apply(n.nodeValue);
    if (next !== n.nodeValue) n.nodeValue = next;
  }

  for (const attr of ['alt', 'aria-label', 'title']) {
    document.querySelectorAll('[' + attr + ']').forEach(el => {
      el.setAttribute(attr, apply(el.getAttribute(attr)));
    });
  }

  if (cfg.phoneDigits) {
    document.querySelectorAll('a[href^="tel:"]').forEach(a => {
      a.setAttribute('href', 'tel:+1' + cfg.phoneDigits);
    });
  }
  return nodes.length;
}
"""


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "lead"


def short_name(business: str) -> str:
    """'Fraser Valley Plumbing & Heating Ltd.' -> 'Fraser Valley'.

    The nav logo slot is narrow; a full legal name overflows it.
    """
    s = re.sub(
        r"\b(plumbing|heating|hvac|mechanical|services?|"
        r"ltd\.?|inc\.?|corp\.?|co\.?|limited|and)\b|&",
        " ",
        business,
        flags=re.I,
    )
    s = re.sub(r"\s+", " ", s).strip(" .,-&")
    return s or business.split()[0]


def build_config(business: str, city: str, phone: str = "") -> dict:
    """Replacement pairs, longest source first so no partial match survives."""
    pairs = [
        [DEMO_BRAND_FULL, business],
        [DEMO_BRAND, short_name(business)],
        [DEMO_CITY, city],
    ]
    digits = re.sub(r"\D", "", phone)
    if phone:
        pairs.append([DEMO_PHONE, phone])
    return {"pairs": pairs, "phoneDigits": digits[-10:] if digits else ""}
