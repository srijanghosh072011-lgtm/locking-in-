# Vale Legal — Premium Law-Firm Landing Template

A high-end, **black-and-gold** landing page for a personal-brand attorney or
boutique corporate firm. Built as a **reusable template**: no framework, no
build step, no external runtime dependencies — just open `index.html`.

- **Look:** warm-black + gold, Cormorant Garamond display + Lato UI, cinematic
  motion, double-bezel cards. Awwwards-tier without the bloat.
- **Stack:** hand-written HTML + one CSS file + ~90 lines of vanilla JS.
- **Self-contained:** self-hosted fonts, self-contained SVG artwork. Renders
  fully offline, deploys anywhere static.

> **Placeholder brand:** everything is fictional demo content — "Adrian Vale",
> `valelegal.example`, `+1 (555) 214-0199`, Regina SK. Replace it all before
> launch (see the checklist below).

---

## Quick start

```bash
# any static server works, e.g.
python3 -m http.server 8000
# → open http://localhost:8000
```

Deploy the folder to Netlify, Cloudflare Pages, Vercel, GitHub Pages, or any
static host. The included `_headers` file applies security headers on Netlify /
Cloudflare Pages automatically.

## File map

```
index.html          Full one-page site (semantic, SEO + JSON-LD in <head>)
styles.css          All styling + design tokens (rebrand here)
main.js             Mobile nav, scroll-reveal, count-up, newsletter demo
404.html            Branded not-found page
robots.txt          Allows search + AI answer crawlers; points to sitemap
sitemap.xml         One-URL sitemap (extend as you add pages)
_headers            CSP + security headers (Netlify / Cloudflare Pages)
site.webmanifest    PWA manifest + theme color
assets/fonts/       Self-hosted Cormorant Garamond + Lato (woff2, latin)
assets/img/         SVG placeholder art + favicon + OG image
PHOTO-GUIDE.md      Imagery: specs, sources, AI prompts, how to swap
```

## Rebrand in one place

Open **`styles.css`** → the `:root` block is the entire theme. Change
`--gold`, `--gold-bright`, `--bg`, and the font variables and the whole site
follows. Then find-and-replace the placeholder content:

| Replace | With |
|---------|------|
| `Adrian Vale` / `A.VALE` / `VALE` | your name / brand |
| `valelegal.example` | your real domain (in `index.html`, `robots.txt`, `sitemap.xml`) |
| `+1 (555) 214-0199` / `tel:+15552140199` | your real phone |
| `consult@valelegal.example` | your real email |
| `Regina, SK` / areaServed `Canada` | your location |
| JSON-LD `Attorney` block | your real NAP, credentials, `sameAs` links |
| Photos | see `PHOTO-GUIDE.md` |

## What's already done for you (design)

- Responsive at 375 / 768 / 1024 / 1440; no horizontal scroll.
- Self-hosted fonts (privacy + performance), `font-display: swap`, preloaded.
- Custom-eased motion; **all** of it respects `prefers-reduced-motion`.
- Accessible: skip link, visible focus rings, keyboard nav, labelled form,
  AA-contrast palette, semantic landmarks, one `<h1>`.
- Native `<details>` accordion for the FAQ (no JS needed).
- Zero inline scripts/styles → a **strict Content-Security-Policy** actually works.

---

## Pre-launch checklist (from the playbook)

This template pre-satisfies many items; the rest are content/deploy tasks.

**Already handled**
- [x] Security headers (`_headers`: CSP, HSTS, nosniff, frame-deny, referrer, permissions)
- [x] Strict CSP with no `unsafe-inline`
- [x] Canonical, meta title/description, Open Graph + Twitter tags
- [x] `Attorney` + `FAQPage` JSON-LD (mirrors visible content)
- [x] `robots.txt` (allows AI crawlers) + `sitemap.xml`
- [x] Semantic HTML, one H1, heading hierarchy, alt text, focus states
- [x] Perf: preload LCP art + key fonts, lazy-load below-fold, width/height set
- [x] Custom 404, favicon, web manifest, `theme-color`

**You must do before launch**
- [ ] Replace ALL placeholder content (table above) — no `.example`, no 555
- [ ] Swap placeholder art for real photos (`PHOTO-GUIDE.md`)
- [ ] Point domain; enable HTTPS; verify `_headers` land (securityheaders.com)
- [ ] Regenerate `og.png` (1200×630) for social previews
- [ ] Wire the newsletter + contact form to a real backend/provider (CASL: real opt-in)
- [ ] Add a real **PIPEDA-compliant Privacy Policy**, Terms, Disclaimer (footer links are stubs) — get legal review
- [ ] Submit sitemap in Google Search Console + Bing; set up GA4 with `tel:`/form key events
- [ ] Test forms actually deliver; verify `tel:`/`mailto:` on a real phone

> **Not legal advice.** The Canadian/PIPEDA/CASL notes reflect the pre-launch
> playbook; have a lawyer review your policies and practices.

## License / attribution

- **Fonts:** Cormorant Garamond & Lato — SIL Open Font License (bundled).
- **Everything else:** your project. The placeholder copy and SVG art are
  original and free for you to use, adapt, and ship.
