# Master build prompt — "BlueLine Plumbing" website + admin

> Paste this into a new chat to rebuild (or re-imagine) the whole project. It combines the original brief with every design decision and feature we settled on.

---

You are an expert web designer and full-stack engineer. Build a **super high-quality website for a plumbing business**. The bar: it must look **bespoke and premium** — someone lands on it and instantly trusts it and wants to buy. **It must NOT look like generic AI slop.**

## Business context
- **Name:** BlueLine Plumbing *(placeholder — make it trivial to rename)*.
- **Market:** Greater Vancouver / the Lower Mainland, British Columbia, **Canada**. This drives: **PIPEDA** privacy law, **CASL** email rules, **CAD** currency, en-CA spelling, and `(604)` phone format.
- **Phone, email, address, licence #, reviews = clearly-marked placeholders** (e.g. `(604) 555-0188`, `hello@bluelineplumbing.ca`).
- **Positioning:** licensed & insured, genuine 24/7 emergency service, upfront fixed pricing, 25-year workmanship guarantee, 4.9★ from 612 reviews, 60-minute emergency response.

## Design system — follow exactly
- **No gradients anywhere.** Flat fills, solid colors, borders.
- **Colors:** deep navy `#0A2540`, blue `#1E5BD6`, **electric orange `#F97316`** for accents/CTAs, near-white surface `#F7F9FC`, ink `#0E1726`.
- **Fonts:** **Instrument Serif** for headlines (Google Fonts; it only ships a 400 weight, so set headings to 400, use sentence case, and `font-synthesis: style` so the browser never fakes a bold) + **Inter** for body/UI.
- **Finish:** "sharp editorial" for content — tight corner radii, strong 1–2px borders and rules, structured grids, crisp shadows used sparingly.
- **Buttons:** tinted **liquid-glass pills** site-wide — translucent fill + backdrop-blur + a bright rim + inner top highlight + soft shadow. **Primary = orange glass; secondary = blue-tinted frosted glass** that switches to a light frosted glass on dark/photo backgrounds.
- **Images: REAL licensed photos only — absolutely NO AI-generated images.** Use Pexels (free commercial license); self-host them via a download script and reference the CDN as a fallback. Ship an image CREDITS file. Photo subjects: **a happy family in a bright modern kitchen for the hero** (friendly lifestyle, NOT someone mid-repair); kitchen sink, boiler/hot-water, pipe repair, blue gas flame, dripping tap, finished bathroom for the services; a smiling technician; customer handshakes.
- **Layout reference (everything EXCEPT the hero):** clean, high-converting plumbing sites like **bigblueplumbing.au** — sticky header with phone + "Book Online", a 24/7 trust bar, service cards, suburb/city landing pages, star-rated testimonials, a blog.

## The hero (the showpiece — "do your own thing"; it must stand out)
- **One full-bleed FRIENDLY photo** (happy homeowner/family in a bright kitchen).
- The **headline hovers directly on the photo**; the area behind the words is **softly blurred and slightly darkened** for legibility — **NOT a glass card, NOT a gradient scrim** (use backdrop-blur + a flat dark tint + a soft alpha mask).
- Sentence-case serif headline **"Fixed fast. Done right."** (accent word in orange), a short subhead, two **liquid-glass CTAs** (Book a plumber / click-to-call), and a one-line trust strip (★4.9 · 612 reviews · licensed & insured · 24/7).

## Marketing pages
- **Home:** hero → trust bar → services grid (cards each with a real photo + icon badge) → "why us" → 4-step process → stats band → featured service → testimonials → service-area chips → FAQ → CTA band → footer.
- **Services overview** + **6 service detail landing pages**: Blocked Drains, Hot Water Systems, 24/7 Emergency, Gas Fitting, Leak Detection, Bathroom Renovations. Each detail page = a **photo hero** (service photo + headline hovering) + "What's included" with a **second photo** + service-specific FAQs + an **"Other services" grid of image cards** + CTA. Make the copy genuinely useful (word-heavy where it helps).
- **About**, **Contact** (validated form), **Pricing** (tiers + an **instant quote estimator** + a typical-price table), **Book online** (booking form + estimate), **Pay my bill** (PCI-safe: hand off to a hosted checkout, no card data on-site), **Warranty & maintenance records** customer portal (sign-in + records table), **Reviews**, **Service Areas**, **Refer-a-friend + loyalty** program.
- **Local SEO:** a dedicated landing page for **every city served** (Vancouver, Burnaby, Richmond, Surrey, Coquitlam, North Vancouver), generated from data, each with local copy + schema.
- **Blog:** index + articles, including "How to unclog a drain" and a seasonal "Spring plumbing checklist" (ties to email marketing).
- **Legal:** Privacy Policy (PIPEDA + CASL), Terms of Service, Accessibility statement. **Cookie-consent banner** (GDPR/Canada — set no non-essential cookies until accepted).
- **404.**

## Admin / staff area (must be auth-gated in production)
- **Staff login** page (work email + password, remember me, forgot password, branded) — linked clearly from the **top bar** and the **footer**.
- A **shared admin shell**: left sidebar nav + a "demo" banner + sign-out, with active-state highlighting.
- **Pages:** Dashboard (KPIs, revenue chart, today's technician schedule, recent leads), **Bookings**, **Customers (CRM)**, **Schedule** (technician dispatch — today's jobs + who's on shift), **Team** (employee roster + an **"Add employee" form** with access levels Technician/Office/Admin that map to what each person sees after login), **Invoices** (with a QuickBooks-sync note), **Settings** (business details + notification toggles + integrations).
- Exclude `/admin/*` from `sitemap.xml` and `robots.txt`.

## SEO
- Per-page `<title>`, meta description, canonical, Open Graph/Twitter. **JSON-LD schema:** `Plumber`/`LocalBusiness` with `aggregateRating`, plus `Service`, `FAQPage`, `Article`, and per-city business markup. `sitemap.xml`, `robots.txt`, web manifest, favicon. Fast: lazy-loaded images with width/height to avoid layout shift.

## Security & privacy (secure-by-default; document the rest)
- No secrets in the frontend; don't ship source maps that leak internals. **Strict CSP** + security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, HSTS) provided for the major hosts (`_headers`, `netlify.toml`, `.htaccess`); force HTTPS.
- Forms: client **and** server validation, a **honeypot** anti-bot field, **CASL consent** checkboxes with unsubscribe. Payments via a **hosted** provider (Stripe/Square) so card data never touches the site.
- Ship a **SECURITY.md** documenting the backend checklist: idempotency, injection prevention, authentication/authorization with row-level access (no IDOR), sessions + token expiry, secrets management, rate limiting + abuse prevention, dependency scanning, multi-tenancy/data isolation, PII handling + retention/deletion, regulatory compliance (PIPEDA/CASL/PCI), audit logging, testing (unit/integration/regression/load), and a disaster-recovery plan.
- Address the common "vibe-coded" gaps: every icon-only button has an `aria-label` + tooltip; forms use **optimistic UI**; lists are **pagination-ready**; avoid N+1 queries (backend); run heavy work **async/queued** (backend).

## UX quality bar
- **WCAG 2.1 AA:** ≥4.5:1 contrast, visible focus rings, full keyboard nav, skip-to-content link, descriptive alt text, labelled form fields, ≥44px touch targets, respect `prefers-reduced-motion`. Responsive at 375 / 768 / 1024 / 1440. No horizontal scroll. SVG icons only (no emoji icons). `cursor-pointer` on interactive elements, 150–300ms transitions.

## Tech approach (what worked well — adapt freely)
- **Static HTML + a hand-built CSS design system (no framework)** for a bespoke, fast, no-slop result.
- A small **Python build script** that: injects shared header/footer partials, **data-generates** the city pages and service pages and the sitemap, and **inlines the CSS + JS into every page** so each file is fully self-contained and renders correctly opened directly (`file://`), on a subpath (e.g. GitHub Pages `/repo/`), or at a domain root — keep all internal links **relative**.
- Vanilla JS for: mobile nav, sticky header, FAQ accordion, accessible form validation + honeypot, quote estimator, cookie consent, optimistic submit + toasts, and the login redirect.
- Forms wired for **live capture on Netlify (zero-config)** or any host via a `data-endpoint`, with a graceful demo fallback.
- Deliverables: the committed static site + build script + a **README with a "done vs needs-backend" matrix** + SECURITY.md + image CREDITS + a self-host image script.

## Still to build — backend (currently front-end/demo only)
Make these live with a real backend (this single layer unlocks most of them): **authentication** (hashed passwords, sessions, rate-limiting) so the dashboard is actually locked; **live data** for the dashboard/CRM/schedule/bookings; **employee persistence + real sign-in invites**; **online payments** (Stripe/Square); **QuickBooks** invoicing (OAuth); **email/marketing automation** — seasonal offers, abandoned-booking recovery, loyalty + referral credits, automated post-job follow-up; **Google Business Profile** integration; a **CAPTCHA** key (hCaptcha/Cloudflare Turnstile); reputable **hosting with TLS + backups**.

---

**Start by proposing the design direction and asking me any clarifying questions about look & feel before building.**
