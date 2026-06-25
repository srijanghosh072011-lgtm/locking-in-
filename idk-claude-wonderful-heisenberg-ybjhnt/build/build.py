#!/usr/bin/env python3
"""
Wascana Plumbing & Drain — tiny static-site builder.

Assembles shared partials (head/header + footer/cookie/scripts) around each
page's <main> content so the navigation, footer and <head> stay identical and
consistent across every page. Output is plain, servable HTML at the repo root.

Usage:   python3 build/build.py
Then:    python3 -m http.server   (and open http://localhost:8000)

Each source file lives in build/src/ and looks like:

    <!--META {"title": "...", "description": "...", "out": "services/index.html"} -->
    <!--HEAD
       ...optional raw HTML injected before </head> (JSON-LD, extra meta)...
    HEAD-->
    <main id="main"> ... page content ... </main>
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "src")
PARTIALS = os.path.join(ROOT, "build", "partials")
BASE_URL = "https://www.wascanaplumbing.ca/"

META_RE = re.compile(r"<!--META\s*(\{.*?\})\s*-->", re.DOTALL)
HEAD_RE = re.compile(r"<!--HEAD\s*(.*?)\s*HEAD-->", re.DOTALL)

# Root-absolute links in href/src/action/poster attributes. We rewrite the
# leading "/" to a page-relative prefix so the site works mounted at any path
# (a domain root, OR a GitHub Pages project subpath like /idk/) without a build
# step on the host. Protocol-relative (//), absolute (https:), tel:, mailto:
# and #anchors all start with something other than "/" and are left untouched.
ASSET_ATTR_RE = re.compile(r'(\b(?:href|src|action|poster)=")/(?!/)')


def rel_prefix_for(out):
    # Depth of the output file below the site root -> how far back to climb.
    # "index.html" -> "./", "services/index.html" -> "../", etc.
    depth = out.count("/")
    return "../" * depth if depth else "./"


def relativize(html, prefix):
    return ASSET_ATTR_RE.sub(lambda m: m.group(1) + prefix, html)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def canonical_for(out):
    # out is like "index.html", "services/index.html", "about.html"
    url = out
    if url.endswith("index.html"):
        url = url[: -len("index.html")]
    return BASE_URL + url


def build_page(src_path, head_tpl, foot_tpl):
    raw = read(src_path)

    m = META_RE.search(raw)
    if not m:
        raise SystemExit(f"Missing <!--META--> block in {src_path}")
    meta = json.loads(m.group(1))
    raw = raw[m.end():]

    head_extra = ""
    h = HEAD_RE.search(raw)
    if h:
        head_extra = h.group(1).strip()
        raw = raw[: h.start()] + raw[h.end():]

    body = raw.strip()
    out = meta["out"]
    canonical = meta.get("canonical") or canonical_for(out)

    html = (
        head_tpl.replace("{{TITLE}}", meta["title"])
        .replace("{{DESCRIPTION}}", meta["description"])
        .replace("{{CANONICAL}}", canonical)
        .replace("{{HEAD_EXTRA}}", head_extra)
    )
    html += "\n" + body + "\n\n" + foot_tpl
    html = relativize(html, rel_prefix_for(out))

    dest = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out


def main():
    head_tpl = read(os.path.join(PARTIALS, "head.html"))
    foot_tpl = read(os.path.join(PARTIALS, "foot.html"))

    if not os.path.isdir(SRC):
        raise SystemExit("No build/src directory found.")

    built = []
    for name in sorted(os.listdir(SRC)):
        if name.endswith(".page.html"):
            built.append(build_page(os.path.join(SRC, name), head_tpl, foot_tpl))

    print(f"Built {len(built)} page(s):")
    for b in built:
        print("  -", b)

    write_sitemap(built)
    print("Wrote sitemap.xml")


# Pages we don't want in the sitemap, plus per-path priority hints.
SITEMAP_EXCLUDE = {"404.html"}
PRIORITY = {
    "index.html": "1.0",
    "services/index.html": "0.9",
    "services/emergency-plumbing.html": "0.9",
    "areas/regina.html": "0.9",
    "contact.html": "0.8",
    "pricing.html": "0.8",
}


def write_sitemap(built):
    from datetime import date
    today = date.today().isoformat()
    rows = []
    for out in sorted(built):
        if out in SITEMAP_EXCLUDE:
            continue
        loc = canonical_for(out)
        prio = PRIORITY.get(out, "0.6")
        rows.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{prio}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)


if __name__ == "__main__":
    sys.exit(main())
