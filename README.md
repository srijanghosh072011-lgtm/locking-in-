# BlueLine Plumbing — premium static site

A bespoke, high-converting website for a plumbing business serving Greater
Vancouver / the Lower Mainland, BC. Static HTML + a hand-built CSS design
system (no framework) + a small Python build that data-generates the city and
service pages, injects shared header/footer partials, and **inlines CSS + JS
into every page** so each file is fully self-contained — it renders correctly
opened directly (`file://`), on a subpath (GitHub Pages `/repo/`), or at a
domain root. All internal links are relative.

> Placeholder business details — phone `(604) 555-0188`, `hello@bluelineplumbing.ca`,
> licence `#PL-000000`, address, and reviews are clearly marked and easy to swap.

## Quick start

```bash
python3 build.py                  # generates ./dist/  (39 pages + SEO files)
python3 scripts/fetch_images.py   # self-host the Pexels photos into dist/images/
# then open dist/index.html, or serve:
python3 -m http.server -d dist 8000
```

No dependencies — standard-library Python 3 only.

## Rename the business

Edit the `BIZ` dict at the top of `build.py` (name, phone, email, address,
licence, rating, reviews, region) and re-run `python3 build.py`. That's it —
the name propagates to every page, title, footer, and schema.

## What's in the box

- **Home** showpiece hero (full-bleed friendly photo, backdrop-blur + flat dark
  tint behind the headline — no glass card, no gradient), trust bar, services
  grid, why-us, 4-step process, stats band, featured service, testimonials,
  service-area chips, FAQ, CTA band.
- **Services** overview + **6 detail landing pages** (Blocked Drains, Hot Water,
  24/7 Emergency, Gas Fitting, Leak Detection, Bathroom Renovations).
- **6 city landing pages** (Vancouver, Burnaby, Richmond, Surrey, Coquitlam,
  North Vancouver) data-generated with local copy + schema.
- **Marketing:** About, Contact (validated), Pricing (tiers + estimator + price
  table), Book online, Pay my bill, Warranty portal + records, Reviews, Service
  Areas, Refer-a-friend.
- **Blog** index + 2 articles ("How to unclog a drain", "Spring plumbing checklist").
- **Legal:** Privacy (PIPEDA + CASL), Terms, Accessibility + cookie-consent banner.
- **404**.
- **Admin** (demo): branded login, sidebar shell with demo banner + active-state,
  Dashboard (KPIs, revenue chart, schedule, leads), Bookings, Customers, Schedule,
  Team (+ add-employee with access levels), Invoices (QuickBooks note), Settings.
- **SEO:** per-page title/meta/canonical/Open Graph; JSON-LD Plumber/LocalBusiness
  with aggregateRating + Service + FAQPage + Article + per-city markup;
  `sitemap.xml`, `robots.txt`, `site.webmanifest`, SVG favicon; lazy, sized images.
- **Security:** `_headers`, `netlify.toml`, `.htaccess` (CSP + headers + HTTPS),
  honeypot + CASL consent, hosted-checkout payment posture. See `SECURITY.md`.

## Design system

- **No gradients** — flat fills, solid colours, 1–2px borders.
- Colours: navy `#0A2540`, blue `#1E5BD6`, orange `#F97316`, surface `#F7F9FC`, ink `#0E1726`.
- Fonts: **Instrument Serif** (400 only, sentence case, `font-synthesis: style`)
  for headings + **Inter** for body/UI.
- Buttons: tinted **liquid-glass** pills (translucent + backdrop-blur + bright
  rim + inner highlight + soft shadow); orange primary, frosted-blue secondary.
- WCAG 2.1 AA: skip link, focus rings, keyboard nav, ≥44px targets, alt text,
  labelled fields, `prefers-reduced-motion`. Responsive 375 / 768 / 1024 / 1440.

## Forms — live capture

Forms work three ways:
1. **Netlify** — add the `netlify` attribute (zero-config capture).
2. **Any host** — set `data-endpoint="https://…"` on the `<form>`.
3. **Demo fallback** — validates, shows a success toast, resets (current default).

## Done vs needs-backend

| Capability | Status |
|------------|--------|
| All marketing, service, city, blog, legal pages | ✅ Done (static) |
| SEO: meta, OG, JSON-LD, sitemap, robots, manifest, favicon | ✅ Done |
| Security headers / CSP / HTTPS config | ✅ Done (config shipped) |
| Form validation + honeypot + CASL consent (client) | ✅ Done |
| Quote estimator, FAQ, cookie consent, toasts, mobile nav | ✅ Done |
| Admin UI (dashboard, CRM, schedule, team, invoices, settings) | ✅ Done (demo UI) |
| Self-host image pipeline + CDN fallback | ✅ Done |
| **Auth** (hashed passwords, sessions, rate-limiting) to lock the dashboard | ⏳ Backend |
| **Live data** for dashboard / CRM / schedule / bookings | ⏳ Backend |
| **Employee persistence** + real sign-in invites | ⏳ Backend |
| **Online payments** (Stripe / Square hosted checkout) | ⏳ Backend |
| **QuickBooks** invoicing (OAuth) | ⏳ Backend |
| **Email / marketing automation** (offers, recovery, loyalty, follow-up) | ⏳ Backend |
| **Google Business Profile** integration | ⏳ Backend |
| **CAPTCHA** key (hCaptcha / Turnstile) | ⏳ Backend |
| **Hosting** with TLS + backups | ⏳ Ops |
| Server-side form validation | ⏳ Backend |

See `SECURITY.md` for the full backend security checklist.

## Project layout

```
build.py                 # data + partials + page templates + generator
site/assets/styles.css   # design system (inlined into every page at build)
site/assets/app.js       # nav, FAQ, validation, estimator, cookies, toasts, login
scripts/fetch_images.py  # self-host Pexels photos (CDN fallback in markup)
_headers netlify.toml .htaccess   # security headers + HTTPS for major hosts
IMAGE_CREDITS.md  SECURITY.md
dist/                    # build output (generated)
```
