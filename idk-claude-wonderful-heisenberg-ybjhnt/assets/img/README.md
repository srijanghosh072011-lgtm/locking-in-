# Image manifest — real stock photos to drop in

**Why this file exists:** the site was built in a sandbox whose network policy
blocks every image host (Unsplash, Pexels, Wikimedia all returned policy
denials), so the photos could not be downloaded or hot-linked from inside the
build. Every photo slot is therefore wired as a proper, accessible `<img>` that
**degrades gracefully to a branded navy panel** until you drop the real file in.
Nothing is AI-generated and nothing is a "lorem ipsum" placeholder — these are
production image slots waiting for verified stock photos.

All photos below are from **Unsplash**, which is **free for commercial use with
no attribution required** (you may still credit the photographer as a courtesy).
Always confirm the current licence on the photo page before publishing.

## How to add the photos (5 minutes each)

1. Open the link, pick a shot that matches the description.
2. Download at ~1600px on the long edge (Unsplash → "Download" → medium/large).
3. **Optimise** it (https://squoosh.app) to WebP or progressive JPG, aim <200 KB.
4. Save it into this folder using the **exact filename** in the table.
5. Keep roughly the aspect ratio noted so it isn't cropped oddly.
6. Re-run `python3 build/build.py` is *not* needed for images — just refresh.

> Tip: for best Lighthouse performance, export a 2nd `@2x` width and add a
> `srcset`, and convert to `.webp`. The markup already sets width/height and
> `loading="lazy"` (hero is `fetchpriority="high"`).

## The slots

| Filename | Used on | What it should show | Aspect | Source |
|---|---|---|---|---|
| `hero-plumber.jpg` | Home hero (background) | A real plumber, hands-on under a sink / on a pipe. Gritty, authentic, room on one side for text. | ~16:10 | Specific: https://unsplash.com/photos/young-plumber-fixing-new-pipe-under-sink-with-wrench-PU9Z6n761bc · or browse https://unsplash.com/s/photos/plumber-working |
| `og-cover.jpg` | Social share preview | Same vibe as hero, 1200×630, logo-safe. Can be a crop of the hero. | 1.91:1 | Reuse hero, or https://unsplash.com/s/photos/plumber |
| `about-van.jpg` | Home "Why us" + About | Service van / technician walking to a door with tools. | ~3:2 | https://unsplash.com/s/photos/work-van · https://unsplash.com/s/photos/plumber |
| `team.jpg` | About — the crew | A few uniformed tradespeople, friendly, by a truck or job site. | ~3:2 | https://unsplash.com/s/photos/plumber-at-work |
| `emergency-pipe.jpg` | Emergency service page | Hands on a burst/leaking pipe, wrench, water. Urgent. | ~3:4 (tall) | https://unsplash.com/photos/a-plumber-works-under-a-sink-hoIQtR0NoQE · https://unsplash.com/s/photos/pipe-leak |
| `drain-camera.jpg` | Drain cleaning page | Drain snake / inspection camera / floor drain work. | ~4:3 | https://unsplash.com/s/photos/drain-cleaning · https://unsplash.com/s/photos/plumbing-service |
| `water-heater.jpg` | Water heaters page | Plumber connecting a tank/tankless water heater, gas line, venting. | ~4:3 | https://unsplash.com/s/photos/water-heater-repair · https://unsplash.com/s/photos/water-heater |
| `regina-home.jpg` | Regina area page | Character/older home or snowy prairie street scene. | ~4:3 | https://unsplash.com/s/photos/canadian-house-winter |
| `white-city.jpg` | White City area page | Newer executive 2-storey home on a large lot. | ~4:3 | https://unsplash.com/s/photos/suburban-house |
| `emerald-park.jpg` | Emerald Park area page | Modern family home with attached garage. | ~4:3 | https://unsplash.com/s/photos/family-home |
| `pilot-butte.jpg` | Pilot Butte area page | Bungalow under a wide prairie sky. | ~4:3 | https://unsplash.com/s/photos/prairie-house |
| `blog-frozen-pipe.jpg` | Blog index + (optional in article) | Frost on an exposed pipe / icy exterior pipe. | ~16:9 | https://unsplash.com/s/photos/frozen-pipe |
| `blog-hard-water.jpg` | Blog index + hard-water article | Limescale on a faucet/aerator, or a chrome tap close-up. | ~16:9 | https://unsplash.com/s/photos/limescale-faucet |
| `blog-sump.jpg` | Blog index | A sump pump basin / basement floor. | ~16:9 | https://unsplash.com/s/photos/sump-pump |

## Don't want to source 14 photos?

At minimum, add **`hero-plumber.jpg`** and **`og-cover.jpg`**. Every other slot
already looks intentional as a deep-navy brand panel with an icon and label, so
the site is fully presentable even before the rest are added.
