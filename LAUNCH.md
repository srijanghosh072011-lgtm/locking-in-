# Go-Live Checklist

Work top to bottom. 🔴 = the site isn't ready without it · 🟠 = do it for a credible launch · 🟢 = after launch.

## 🔴 Must-do before launch

- [ ] **Swap the real business details.** Find-and-replace these placeholders across every `.html` file plus `sitemap.xml`, `robots.txt`, `llms.txt`:
  - `(306) 555-0142` and `+13065550142` → real phone
  - `2310 Albert Street, Regina, SK S4P 2V7` → real address
  - `hello@plumboregina.ca` → real email
  - `https://www.plumboregina.ca` → real domain
  - `plumboregina` (social handles) → real Facebook / Instagram / YouTube
  - Business name "Plumbo Plumbing & Heating" if different
- [ ] **Turn the forms on.** Get a free Access Key at [web3forms.com](https://web3forms.com), then replace `YOUR_WEB3FORMS_ACCESS_KEY` in every `.html`. Test by submitting the contact form and confirming the email arrives. (Details in `README.md`.)
- [ ] **Replace stats & reviews with real ones.** "12,000+ jobs", "4.9★", "300+ reviews" and the testimonials are placeholders. Publishing fake reviews breaks Canada's Competition Act — use the client's real numbers/reviews or delete them.
- [ ] **Add real photos.** Swap the stock photos for the client's own crew/truck/job photos (see `IMAGES.md`). Real photos convert better and help local SEO.
- [ ] **Deploy with HTTPS.** GitHub Pages, Netlify or Cloudflare Pages — all give free SSL. (Deploy steps in `README.md`.)
- [ ] **Regenerate `og-image.png`** if the phone/name changed (it's baked into the share image). Ask me and I'll rebuild it.

## 🟠 For a credible, findable launch

- [ ] **Google Business Profile** — claim/verify it with the *exact* same name, address, phone as the site. This is the #1 driver of "plumber near me" and AI answers.
- [ ] **Bing Places** — Copilot and ChatGPT lean on Bing's index.
- [ ] **Submit `sitemap.xml`** in Google Search Console and Bing Webmaster Tools.
- [ ] **Consistent citations** — same name/address/phone on Yelp, YellowPages.ca, HomeStars, BBB, 411.ca.
- [ ] **Analytics** — add GA4 or a privacy-friendly option (Plausible). Gate any analytics script behind the existing cookie-consent "Accept" button (see the note in `js/main.js`).
- [ ] **Lawyer glance** at `privacy-policy.html` and `terms.html` — they're solid templates, not legal advice.

## 🟢 After launch

- [ ] **Ask every happy customer for a Google review**, ideally mentioning the service + neighbourhood ("water heater install in Lakeview") — AI engines quote these.
- [ ] **Keep content fresh** — touch the tip articles and add one every month or two; AI search favours recently-updated pages.
- [ ] **Add a real CAPTCHA** (Cloudflare Turnstile, free) on the forms for extra spam protection beyond the built-in honeypot.
- [ ] **Booking / CRM / QuickBooks** — if the client wants a dashboard, follow-ups and invoicing, use Jobber or Housecall Pro (~$50/mo) and embed their booking widget on `contact.html`. Don't build it custom (see `README.md`).

## What's already handled (from the original brief)

HTTPS-ready · cookie consent banner · spam honeypot · client-side input validation · privacy policy · terms of service · security headers (`_headers`) · branded 404 · alt text, keyboard nav, focus states, reduced-motion · Schema.org structured data · `robots.txt` welcoming AI crawlers · `llms.txt` · sitemap · self-hosted social share image.

Because this is a **static site with no backend, database or login**, most classic security risks (API keys in the frontend, SQL injection, plaintext passwords, IDOR) don't apply — there's nothing server-side to attack.
