# Wascana Plumbing &amp; Drain — marketing website

A complete, high-converting marketing website for a (fictional) Regina,
Saskatchewan plumbing company. Hand-built static HTML/CSS/JS — no framework,
no build-time dependencies beyond Python's standard library — so it loads fast,
scores well on Lighthouse, and is trivial to host anywhere.

> **Brand:** *Wascana Plumbing &amp; Drain.* The name is built on **Wascana** —
> the creek and lake at the heart of Regina — so it reads as unmistakably local
> and established to anyone in the city, without being a generic "Pro/Mr."
> trade name.

---

## Quick start

```bash
# Preview the site (any static server works):
python3 -m http.server 8000
# open http://localhost:8000

# Edit content, then regenerate the HTML:
python3 build/build.py
```

The site uses **root-relative paths** (`/assets/...`, `/services/...`), so it
must be *served* (as above), not opened with `file://`.

---

## How it's built (tiny static site generator)

To keep the navigation, footer and `<head>` identical across every page without
copy-paste drift, pages are assembled from shared partials by a ~90-line Python
script:

```
build/
  build.py              # assembles pages + writes sitemap.xml
  partials/
    head.html           # <head>, top bar, nav (template tokens)
    foot.html           # footer, cookie banner, scripts
  src/
    *.page.html         # one file per page: <!--META-->, optional <!--HEAD-->, then <main>
```

Each `build/src/*.page.html` declares its metadata in a one-line `<!--META …-->`
JSON comment and (optionally) per-page JSON-LD in a `<!--HEAD … HEAD-->` block,
followed by the page's `<main>`. Running `build.py` writes the final, servable
`.html` files to the repo root and regenerates `sitemap.xml`.

**To change shared chrome** (nav links, footer, phone number) edit the partials.
**To change a page's content** edit its `build/src/*.page.html`. Then rebuild.

---

## Pages (19)

- **Home** — from-scratch hero (solid navy, real-photo background, two distinct
  CTAs, social proof), services overview, stats, about snippet, reviews,
  certifications, FAQ, CTA.
- **Services** — index + individual pages: Emergency, Drain &amp; Sewer, Water
  Heaters (scannable, visual, with transparent pricing tables).
- **About**, **Contact** (booking form + hours + map slot), **Pricing &amp;
  Quotes** (price tables + free-quote form).
- **Blog** — index + two full, genuinely useful SEO articles
  (*Preventing frozen pipes in a Regina winter*, *Regina's hard water*).
- **Local SEO landing pages** — Regina, White City, Emerald Park, Pilot Butte,
  each with unique localized content + `Plumber`/`areaServed` schema.
- **Legal** — Privacy (PIPEDA/CASL-aware), Terms, Accessibility statement.
- **404**.

---

## Design system

- **Colour:** deep navy `#0A1B2A` + crisp white + copper/rust `#BD5A22`.
  **No gradients** anywhere. Contrast meets WCAG AA (4.5:1+).
- **Type:** **Barlow Condensed** (display) + **Barlow** (body) — an industrial,
  signage-derived superfamily that feels like a real trade brand and avoids the
  generic Roboto/Open Sans look.
- **Logo:** original inline-SVG mark — a copper "W" with a water droplet at its
  peak in a navy badge. No clip art, no generic wrench.
- All tokens live at the top of `assets/css/styles.css`.

---

## What's complete vs. what's flagged

### ✅ Built and working
Responsive mobile-first layout · semantic, keyboard-accessible markup · skip
link · focus states · reduced-motion support · client-side form validation +
honeypot · cookie-consent banner (analytics off until accepted) · JSON-LD
(`Plumber`, `AggregateRating`, `FAQPage`, `Service`, `Article`, `BreadcrumbList`)
· Open Graph · `sitemap.xml` + `robots.txt` · security headers (`/_headers`) ·
graceful image fallbacks.

### 🔒 Privacy &amp; security non-negotiables

| Area | Status | Notes |
|---|---|---|
| HTTPS / SSL | ⚙️ Host-level | Enable on your host (Netlify/Cloudflare = automatic). HSTS header is set. |
| Form CAPTCHA + sanitisation | ◐ Front-end done | Honeypot + client validation included. **Server-side validation + CAPTCHA must be added** with the real endpoint (see below). |
| Reputable host + daily backups | ⚙️ Host-level | Choose a host that does this (recommended below). |
| Privacy Policy | ✅ Written | `legal/privacy.html` — have a lawyer review. |
| Cookie consent | ✅ Done | Accept/Decline banner; nothing non-essential loads until Accept. |
| Terms of Service | ✅ Written | `legal/terms.html` — have a lawyer review. |
| Accessibility | ✅ Done | Alt text, contrast, keyboard nav, statement page. |
| CASL compliance | ◐ Front-end done | Explicit opt-in checkbox + unsubscribe language. **Sending requires an ESP** with real unsubscribe handling. |
| Secure + limited data retention | ⚙️ Backend | Retention described in the policy; enforce it in whatever stores leads. |

### 🚧 Requires a backend / accounts (not buildable as static files)
These were **not** faked. The front-end is built correctly and documented; the
server side needs your accounts and secrets:

- **Customer portal** (pay bills, warranty/maintenance records, accounts)
- **Booking system with confirmation emails**
- **Marketing automation** (seasonal offers, abandoned-booking recovery,
  loyalty/referral, post-job follow-up)
- **Admin dashboard, CRM, QuickBooks integration, technician portal**
- **Live Google reviews feed** (needs a Google Places API key — must stay
  server-side; the site shows a schema-marked static reviews section instead)

> **Sandbox limitation (flagged per the brief):** stock photos could not be
> embedded/verified from the build environment because its network policy blocks
> all image hosts. Real photos are wired as graceful slots — see
> [`assets/img/README.md`](assets/img/README.md) for the exact photo to drop in
> each slot.

---

## Backend contract for the forms

The contact/booking/quote forms validate on the client and then run a demo
success state. To go live, point each `form[data-validate]` at a **secured
endpoint** that:

1. **Re-validates and sanitises every field** server-side (never trust the
   client). Reject the submission if the `company` honeypot field is non-empty.
2. **Verifies a CAPTCHA** (e.g. Cloudflare Turnstile or hCaptcha — privacy
   friendly).
3. **Rate-limits** by IP to stop brute-force/spam.
4. **Stores the lead** (or emails it) over a server-side secret — **never put an
   API key in this front-end code.**
5. Honours the CASL `optin` flag and records consent (timestamp + source).

A serverless function (Netlify/Cloudflare Functions) is the simplest fit; a
redirect stub is sketched in `netlify.toml`. Replace the demo block in
`assets/js/main.js` (clearly commented) with a `fetch()` to your endpoint.

---

## Deployment

Recommended: **Netlify** or **Cloudflare Pages** — free tier, automatic HTTPS,
daily-ish backups via git history, and both read `/_headers` directly.

```
Publish directory: .            (repo root — it's already built)
Build command:     python3 build/build.py
```

For **Nginx/Apache**, serve the repo root and translate `/_headers` into your
server config (CSP, HSTS, X-Frame-Options, etc.).

**Before launch:** work through [`CUSTOMIZE.md`](CUSTOMIZE.md) — phone, email,
address, real ratings, prices, and legal review.

---

## Performance &amp; SEO notes

- Zero JS framework; one small stylesheet and one small deferred script.
- Fonts are preconnected and `display=swap`; images are lazy-loaded with
  intrinsic `width`/`height` to avoid layout shift; hero image is
  `fetchpriority="high"`.
- Every page has a unique title, meta description, canonical, OG tags and
  appropriate structured data, targeting Regina-local keywords.
