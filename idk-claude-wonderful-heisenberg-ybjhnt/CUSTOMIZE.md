# Before you launch — replace these placeholders

The site is built around a fictional but realistic brand, **Wascana Plumbing &
Drain**. Everything below is invented and must be swapped for the real
business's details. Most live in `build/partials/` (shared) or the page sources
in `build/src/`; after editing, run `python3 build/build.py` to regenerate.

## ⚠️ Safety note on the phone number

The number **(306) 555-0147** is deliberately from the **555-01xx range that is
officially reserved for fictional use** — so the demo never dials a real person
or business. **You must replace it with the real number everywhere** before
launch (it appears in `tel:` links, visible text, and JSON-LD schema).

Quick find-and-replace targets (do these across `build/partials/*` and
`build/src/*`, then rebuild):

| Placeholder | Appears as | Replace with |
|---|---|---|
| Phone (display) | `(306) 555-0147` | Real number |
| Phone (links/schema) | `+13065550147` / `+1-306-555-0147` | Real number, E.164 |
| Email | `dispatch@wascanaplumbing.ca`, `privacy@…` | Real inboxes |
| Domain | `www.wascanaplumbing.ca` | Real domain (canonical, OG, schema, sitemap, robots) |
| Street address | `1184 McDonald Street` | Real shop address |
| Postal code | `S4N 5W3` | Real postal code |
| Geo coords | `50.4452, -104.5686` | Real lat/long (from Google Maps) |
| Founding year | `2009` / "since 2009" | Real year |
| Stats | `6,200+` jobs, `15+` years, `30+` areas | Real figures |
| Google rating | `4.9` / `487 reviews` | **Real** GBP rating & count (see below) |
| Team names | Dave/Dylan/Megan Kowalchuk | Real team, or remove the team cards |
| Hours | Mon–Fri 7:30–5:30, Sat 8–4 | Real hours |
| Prices | every "from $…" figure | Your real flat-rate pricing |
| Credentials | "Licensed journeyperson", "$5M insured", "MCA Saskatchewan" | Verify each is true; add real licence #s |

## ⚠️ Ratings & reviews must be real

The `aggregateRating` in the JSON-LD and the "4.9 / 487 reviews" copy will make
Google show stars in search results. **Google requires these to reflect genuine,
on-site or verifiable reviews.** Publishing invented ratings violates Google's
policy and can get you penalised. Either:
- wire in your real Google Business Profile rating + review count, or
- remove the `aggregateRating` blocks and review copy until you have real ones.

## Things to connect

- **Map:** embed your Google Business Profile map in the `.mapframe` on
  `build/src/contact.page.html`.
- **Google Business Profile:** claim/verify it; link it from the review section.
- **Forms:** currently client-side only (see README "Backend contract"). Point
  them at a real, secured endpoint before collecting live data.
- **Analytics:** none is loaded. If you add some, only fire it after cookie
  "Accept" (the banner already dispatches a `cookies:accepted` event you can
  hook). Keep it CASL/PIPEDA-friendly.
- **Legal pages:** `privacy.html`, `terms.html` are solid Canada-aware starting
  points — **have a Saskatchewan lawyer review them.**
- **Favicon/OG:** swap `assets/favicon.svg` if you have a final logo; add
  `assets/img/og-cover.jpg` (see `assets/img/README.md`).
