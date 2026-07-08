# Local-business starter kit

A tokenized static-site starter with the two footguns from the last build
**designed out**: (1) hardcoded domain in canonical/OG/sitemap, and (2) inline
`<head>` script forcing a weak CSP.

## Why it can't repeat the domain bug
Every environment-specific value lives once in **`site.config`**. `build.sh`
stamps it into `src/` and writes `dist/`, then **refuses to ship** if any
`{{TOKEN}}`, placeholder (`YOUR_`, `555-…`, `example.com`), or a URL whose host
doesn't match `SITE_URL` survives. Canonical, `og:url`, `sitemap.xml` and
`robots.txt` all derive from the same `SITE_URL`, so they can't drift apart.

## Use it
    cp -r starter-kit my-new-site && cd my-new-site
    # 1. edit site.config  (SITE_URL first — no trailing slash)
    ./build.sh             # stamps + gates -> dist/
    # 2. preview
    cd dist && python3 -m http.server 8000
    # 3. work through PRE-LAUNCH.md, then deploy the dist/ folder

## What's baked in (carried from the good parts of the last site)
- Static, semantic HTML — real content in source (great for SEO + AI crawlers).
- Valid JSON-LD: LocalBusiness + FAQPage, ISO times, **no fabricated ratings**.
- a11y: skip link, `aria-*`, keyboard nav, focus-visible, reduced-motion, JS-off
  fallback (`.reveal` is visible without JS).
- Full OG/Twitter/canonical/theme-color/geo + `referrer` meta (host-independent).
- Honeypot + validated forms with inline feedback; consent-gated cookie banner.
- `_headers` CSP with **no `script-src 'unsafe-inline'`** (zero inline scripts).

## Deploy target matters
`_headers` / `_redirects` work on **Cloudflare Pages / Netlify**. **GitHub Pages
ignores them** — deploy there and you get no CSP/HSTS. Pick the host that runs
the security you configured.

## Files
    site.config      # the only file you edit per project
    build.sh         # stamp + gate
    PRE-LAUNCH.md    # human checklist the build can't automate
    src/             # template (index, 404, css, js, _headers, robots, sitemap)
    dist/            # generated — deploy this (do not edit by hand)
