# BlueLine Plumbing — website

A high-quality, fast, accessible marketing website for a plumbing business.
Hand-built static HTML + a bespoke CSS design system (no framework, no AI-generated
images, **no gradients**) with a custom split-editorial hero, local-SEO city pages,
a blog, legal/compliance pages, and front-end booking/quote/pay flows.

> **Brand, phone, address, licence numbers and city list are placeholders**
> (`BlueLine Plumbing`, Greater Vancouver, `(604) 555-0188`). Search-and-replace
> them with the client's real details — see **[Customising](#customising)**.

---

## Quick start

```bash
# 1. Preview: open index.html directly in a browser, OR serve it:
python3 -m http.server 8000      # → http://localhost:8000
# (Paths are relative, so it works opened directly, on a subpath like
#  GitHub Pages /repo-name/, or at a domain root.)

# 2. After editing anything in /src or /partials, rebuild:
python3 build.py

# 3. (Optional) self-host the photos instead of using the Pexels CDN:
bash download-images.sh
```

There is **no build toolchain to install** — `build.py` uses only the Python
standard library.

---

## How it's organised

```
/                     ← built, deployable site (commit this)
  index.html, services.html, about.html, contact.html, pricing.html,
  book.html, pay.html, warranty.html, referral.html, reviews.html, areas.html
  services/*.html     ← 6 service pages (generated from data in build.py)
  locations/*.html    ← 6 local-SEO city pages (generated from data in build.py)
  blog/*.html         ← blog index + articles
  legal/*.html        ← privacy, terms, accessibility
  admin/dashboard.html← admin dashboard DEMO (sample data)
  sitemap.xml, robots.txt, site.webmanifest, 404.html
  _headers, netlify.toml, .htaccess   ← security headers per host

/src                  ← EDIT THESE: page content with simple front-matter
/partials             ← EDIT THESE: shared header.html + footer.html
/assets/css/styles.css← the design system (tokens + components)
/assets/js/main.js    ← nav, forms, FAQ, cookie consent, quote estimator
/assets/img/          ← favicon + CREDITS.md (photos via CDN by default)
build.py              ← assembles pages, generates city/service pages + sitemap
```

**One source of truth:** the header/footer live in `/partials`. Page `<head>`
(title, description, canonical, Open Graph) comes from each `/src` page's
front-matter. Run `python3 build.py` to propagate changes everywhere.

---

## Design system

| Token | Value |
|------|-------|
| Navy | `#0A2540` · Blue `#1E5BD6` · **Accent orange `#F97316`** |
| Fonts | **Oswald** (condensed display) + **Inter** (body) |
| Finish | Sharp editorial — tight radii, strong borders, flat fills, **no gradients** |
| Hero | Custom split-editorial: navy panel + real photo + floating ★ review card |

---

## Customising

- **Business details / phone / address** — edit `/partials/header.html`,
  `/partials/footer.html`, and the JSON-LD + front-matter in `/src/index.html`.
  (Tip: global find-and-replace `604) 555-0188`, `bluelineplumbing.ca`, `BlueLine`,
  and the Vancouver city list.)
- **Services** — edit the `SERVICES` dict in `build.py`.
- **Service-area cities** — edit the `CITIES` dict in `build.py`.
- **Colours / fonts** — edit the `:root` tokens at the top of `assets/css/styles.css`.
- **Real photos** — drop the client's own job photos into `assets/img/` and point
  the `<img>` tags at them (genuine photos beat stock for trust + local SEO).

---

## Images — real, licensed, not AI

Per the brief, **no AI-generated images**. The site uses real, commercially-licensed
photos from Pexels (Pexels License — free for commercial use). They're referenced
via the Pexels CDN so they render as soon as you open/deploy the site. Run
`bash download-images.sh` to self-host them for production. Full list in
`assets/img/CREDITS.md`.

> Note: this build environment blocks outbound image hosts, so the photos couldn't
> be downloaded into the repo here — that's why they load from the CDN by default
> and ship with a one-command self-host script.

---

## SEO built in

- Per-page `<title>`, meta description, canonical, Open Graph/Twitter cards.
- **JSON-LD schema** so Google can show ratings/area: `Plumber`/`LocalBusiness`
  with `aggregateRating`, plus `Service`, `FAQPage`, `Article` and per-city business
  markup.
- **A landing page for every city** served (local SEO), auto-generated.
- `sitemap.xml` (generated) + `robots.txt` + web manifest.
- Fast: no framework, system-font fallbacks, lazy-loaded images, sized to avoid layout shift.

---

## Deploy

Any static host. Recommended: **Netlify**, **Vercel**, or **Cloudflare Pages**
(free TLS + the security headers are picked up automatically).

1. Push this repo to GitHub.
2. Connect it to your host. Build command `python3 build.py`, publish dir `.`
   (or just deploy the pre-built files — they're committed).
3. Point the client's domain at it; TLS is automatic.
4. Verify headers at https://securityheaders.com.

Security headers ship in `_headers` (Netlify/Cloudflare), `netlify.toml`, and
`.htaccess` (Apache/cPanel). See **[SECURITY.md](SECURITY.md)**.

---

## What's done vs. what needs your accounts / a backend

You asked me to be straight about what I could and couldn't complete in one pass.
The **entire website and all front-end flows are done and working**. The items
below marked 🔌 are intentionally built as polished front-ends that need an
external service or backend wired in — none of which can be provisioned from this
build environment (they need *your* accounts, billing, and a server/database).

| Feature from the brief | Status |
|---|---|
| Hero, Services, Service detail, About, Contact, Pricing/Quotes | ✅ Done |
| Trust & social proof (reviews, badges, ratings, schema) | ✅ Done |
| Local SEO: a landing page per city | ✅ Done |
| Schema markup (rating/area in search) | ✅ Done |
| Blog + articles ("How to unclog a drain") | ✅ Done |
| Privacy Policy, Terms, Accessibility, Cookie consent | ✅ Done (lawyer review recommended) |
| Booking / quote / contact / referral / newsletter forms | ✅ Done — **live capture** on Netlify (zero-config) or any host via `data-endpoint` |
| Pay bills online | ✅ Front-end page only — payment integration intentionally **not** wired (per request) |
| Warranty / maintenance records portal | ✅ Front-end done · 🔌 needs auth + database |
| Google Business Profile integration | 🔌 Needs the client's Google account (link + reviews API) |
| Email list + seasonal offers (CASL-compliant) | ✅ Signup UI done · 🔌 connect Mailchimp/Resend |
| Abandoned-booking recovery | 🔌 Backend + email automation (hook noted in `book.html`) |
| Loyalty + referral programs | ✅ UI + rules copy done · 🔌 needs accounts/credits in a backend |
| Admin dashboard (bookings, revenue, schedules) | ✅ Demo UI done · 🔌 needs auth + live data API |
| CRM (track every lead/customer) | ✅ Demo table done · 🔌 use a CRM or build one |
| Automated post-job follow-up | 🔌 Backend + email/SMS automation |
| QuickBooks invoicing integration | 🔌 Needs QuickBooks account + OAuth + a backend |
| SSL certificate, reputable hosting, backups | 🔌 Provisioned at your host (config provided) |
| CAPTCHA | ✅ Honeypot first-layer done · 🔌 add hCaptcha/Cloudflare Turnstile key |

### The "5 reasons your app sucks" — addressed
1. **Button labels & tooltips** — every icon-only button has an `aria-label`; the dashboard's icon action has a tooltip (`.tip`). ✅
2. **Optimistic UI** — forms respond instantly (disable + "Sending…" + success toast) rather than freezing. ✅ (front-end)
3. **Pagination** — list/table views are designed to paginate; implement server-side paging when you add the backend. 🔌
4. **N+1 queries** — a backend concern; batch/`JOIN` your queries. 🔌
5. **Synchronous everything** — run email/QuickBooks/SMS work on async jobs/queues. 🔌

---

## Wiring the backend (pointers)

- **Forms** → already live: deploy to **Netlify** and the contact/booking/referral/
  newsletter forms capture submissions with **no config** (honeypot wired). On other
  hosts, set `data-endpoint="https://…"` (Formspree or your API). Validate server-side
  too — see SECURITY.md.
- **Payments** → Stripe Checkout or Square hosted payment links (no card data on-site).
- **Booking/CRM** → your scheduling tool or a small API + database.
- **Email** → Resend/Mailchimp with CASL consent (the consent checkboxes are wired).
- **QuickBooks** → QuickBooks Online API via OAuth, from your backend only.

See **[SECURITY.md](SECURITY.md)** for the full backend security checklist
(auth, rate limiting, secrets, idempotency, data isolation, audit logs, etc.).

---

## License

Code in this repo: use freely for the client's site. Photos: Pexels License
(see `assets/img/CREDITS.md`).
