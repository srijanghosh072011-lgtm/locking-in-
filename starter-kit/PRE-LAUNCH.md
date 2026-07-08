# Pre-launch checklist

`./build.sh` already gates the mechanical stuff (tokens, placeholders, canonical
host). These are the judgement calls it can't make for you.

## Blocking — do not launch without these
- [ ] `SITE_URL` in `site.config` is the host you're **actually** deploying to.
- [ ] Real phone number in `PHONE_E164` + `PHONE_DISPLAY` (no 555 numbers).
- [ ] Real `WEB3FORMS_KEY`, and in the Web3Forms dashboard: turn on the
      **domain allowlist + captcha** (the key is public — anyone can read it).
- [ ] Submitted the contact form for real and the email arrived.
- [ ] Reviews/ratings/counts are **real** (or removed). No stock-photo "customers".
      Only add `AggregateRating`/`Review` schema once you have verifiable reviews.
- [ ] Deployed somewhere that honours `_headers` (Cloudflare/Netlify Pages) — or
      accept that on GitHub Pages you ship no security headers.

## Should-do
- [ ] `og-image.png` exists at the site root and opens at `SITE_URL/og-image.png`.
- [ ] Real, self-hosted photos (not hotlinked stock). Add width/height to each.
- [ ] `areaServed` in the schema lists only towns you truly serve — and each has a page.
- [ ] Lighthouse ≥ 95 in all four categories.
- [ ] Google Rich Results Test on every page: 0 errors.
- [ ] Load with JavaScript disabled — nav + forms still usable.

## Copy/paste checks
    grep -rEn "555-|YOUR_|REPLACE_WITH|example\.(com|ca)|lorem|TODO" dist/   # expect no output
    grep -rno "{{[A-Z0-9_]*}}" dist/                                        # expect no output
