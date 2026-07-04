# Plumbo — Plumbing Website (Regina, SK)

A complete, dependency-free static website for a Regina plumbing company: 18 pages of pure
HTML/CSS/vanilla JS. No build step, no framework — upload the folder to any host and it works.

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Homepage: hero + booking form, services carousel, process, testimonials, 24/7 emergency, expert tips, map |
| `about.html` | Company story, stats, values, service area |
| `services.html` | All-services overview |
| `services/plumbing-repair.html` | Local-SEO landing page — "plumbing repair Regina" |
| `services/drain-cleaning.html` | Landing page — "drain cleaning Regina" |
| `services/water-heater.html` | Landing page — "water heater repair Regina" |
| `services/emergency-plumbing.html` | Landing page — "emergency plumber Regina" |
| `services/pipe-installation.html` | Landing page — "repiping Regina" |
| `services/faucets-fixtures.html` | Landing page — "faucet installation Regina" |
| `services/sump-pump.html` | Landing page — "sump pump Regina" (rebate angle) |
| `reviews.html` | Trust & social proof |
| `tips/*.html` (×3) | Expert articles (frozen pipes, water heater signs, tankless) |
| `contact.html`, `privacy-policy.html`, `terms.html`, `404.html` | Support pages |
| `robots.txt`, `sitemap.xml`, `llms.txt` | Search + AI-search plumbing |

## ⚠️ Placeholders you MUST replace before launch

Search-and-replace these across all `.html` files plus `sitemap.xml`, `robots.txt`, `llms.txt`:

| Placeholder | Where it appears |
|---|---|
| `(306) 555-0142` / `+13065550142` | Phone everywhere (555 = fictional) |
| `2310 Albert Street, Regina, SK S4P 2V7` | Address (made up) |
| `hello@plumboregina.ca` | Email |
| `https://www.plumboregina.ca` | Canonical URLs, sitemap, llms.txt — set to the real domain |
| `facebook/instagram/youtube.com/plumboregina` | Social links |
| Business name "Plumbo Plumbing & Heating" | Swap for the client's real name if different |
| Stats (12,000+ jobs, 4.9★, 300+ reviews) and testimonials | **Must be true** — replace with the client's real numbers/reviews or delete. Fake reviews violate Canadian competition law. |
| Map | `index.html` + `contact.html` use an OpenStreetMap embed centred on downtown Regina — update coordinates to the real office |

Photos: see [`IMAGES.md`](IMAGES.md) — real Unsplash photos are hotlinked with an automatic
styled fallback if any link dies. Replace with real photos of the client's crew ASAP (real
crew photos outperform stock for local trust AND local SEO).

## Making the forms actually send

Forms currently validate client-side (with a spam honeypot) and show a demo confirmation.
Pick one (all have free tiers, no backend needed):

1. **Netlify Forms** — if hosting on Netlify, add `data-netlify="true"` to each `<form>` and set `action=""`.
2. **Formspree / Web3Forms** — set `action="https://formspree.io/f/YOUR_ID"` and `method="POST"`.
3. Add **Cloudflare Turnstile** (free CAPTCHA) once a real endpoint is wired — the honeypot handles casual bots only.

## Deploying

Any static host works: GitHub Pages, Netlify, Cloudflare Pages, Vercel. All of them give you
**HTTPS automatically** (required item from the compliance checklist). For security headers
(CSP, X-Frame-Options, etc.) add a `_headers` file (Netlify/Cloudflare) or configure your host.

## Built-in SEO & AI-search (GEO) features

- **Schema.org JSON-LD** on every page: `Plumber` local-business (NAP, geo, hours, service area), `Service`, `FAQPage`, `Article`, `BreadcrumbList`
- **Answer-first content**: every landing page opens with a self-contained "Quick answer" block — the format AI engines quote
- **Question-phrased headings + FAQ sections** on every service page and article
- **`robots.txt` explicitly allows AI crawlers**: GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, meta-externalagent, CCBot
- **`llms.txt`** — a crib sheet for AI answer engines
- Canonical URLs, OG/Twitter cards, geo meta tags, `sitemap.xml`, semantic HTML, alt text everywhere

### Off-site checklist (this is where local + AI rankings are actually won)

1. **Google Business Profile** — claim it, exact same name/address/phone (NAP) as the site, add photos, collect reviews weekly. #1 factor for "plumber near me" and AI Overviews.
2. **Bing Places** — Copilot/ChatGPT lean on Bing's index.
3. **Citations**: Yelp, YellowPages.ca, HomeStars, BBB, 411.ca — identical NAP everywhere.
4. **Reviews with keywords** — ask happy customers to mention the service + neighbourhood ("water heater install in Lakeview"). AI engines quote these.
5. **Freshness** — AI engines favour recently-updated content; touch the tips articles and add one new one every month or two.
6. Submit `sitemap.xml` in Google Search Console + Bing Webmaster Tools on day one.

## What's deliberately NOT here (and the lazy-correct way to add it)

The brief mentioned an admin dashboard, CRM, automated follow-ups and QuickBooks invoicing.
Building those custom is a five-figure liability (auth, multi-tenancy, PIPEDA data retention,
backups — see the security checklist). A trades business gets all of it, done properly, from
**Jobber or Housecall Pro** (~$40–70 CAD/mo): booking, CRM, "rate your experience" follow-ups,
technician scheduling and native QuickBooks sync. Embed their booking widget on `contact.html`
and this site stays a fast, unhackable brochure while the SaaS holds the customer data.
Build custom only if the business outgrows that.
