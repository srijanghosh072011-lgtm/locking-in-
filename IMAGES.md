# Photo manifest

All photos are **real photography** hotlinked from Unsplash (free to use commercially under
the [Unsplash License](https://unsplash.com/license), no attribution required). If any link
ever dies, `js/main.js` automatically swaps it for a branded placeholder tile, so the site
never shows a broken-image icon.

**Recommended:** replace stock with real photos of the client's crew, trucks and jobs —
real photos convert better and help local SEO. To swap any image, replace the `src` URL on
the `<img data-photo ...>` tag (keep the `data-photo` attribute for the fallback safety net).

**Verify after deploy:** open every page once and eyeball the photos. If one shows the
orange "PLUMBO — PHOTO SLOT" tile or doesn't fit the subject, grab a replacement from the
suggested search below and paste its URL in.

| Slot (what/where) | Subject needed | Current source | Find a replacement |
|---|---|---|---|
| Homepage hero background (`index.html`) | Plumber at work, dark-friendly | `photo-1621905251189-08b45d6a269e` | unsplash.com/s/photos/plumber |
| Service card — Plumbing Repairs | Repair under a sink | `photo-1581578731548-c64695cc6952` | unsplash.com/s/photos/plumber-repair |
| Service card — Pipe Setup | Pipework / wrench on fitting | `photo-1585704032915-c3400ca199e7` | unsplash.com/s/photos/plumbing-pipes |
| Service card — Faucets & Fixture | Faucet close-up | `photo-1584622650111-993a426fbf0a` | unsplash.com/s/photos/faucet |
| Service card — Drain Cleaning | Bathroom / tub drain | `photo-1552321554-5fefe8c9ef14` | unsplash.com/s/photos/bathtub |
| Service card — Water Heaters | Boiler / gauges / mechanical | `photo-1504917595217-d4dc5ebe6122` | unsplash.com/s/photos/boiler-room |
| Service card + emergency section | Tradesperson on site | `photo-1541888946425-d81bb19240f5` / `photo-1504307651254-35680f356dfd` | unsplash.com/s/photos/construction-worker |
| Service card — Sump Pumps | House exterior / basement | `photo-1600585154340-be6161a56a0c` | unsplash.com/s/photos/house-exterior |
| About — handshake | Customer trust moment | `photo-1600880292203-757bb62b4baf` | unsplash.com/s/photos/handshake-worker |
| Tip — frozen pipes | Winter / icicles | `photo-1477601263568-180e2c6d046e` | unsplash.com/s/photos/icicles |
| Tip — water heater signs | Technician / diagnostics | `photo-1581092160562-40aa08e78837` | unsplash.com/s/photos/technician |
| Tip — tankless | Modern kitchen / hot water | `photo-1556911220-bff31c812dba` | unsplash.com/s/photos/modern-kitchen |
| Review avatars (×6) | Headshots | `photo-1507003211169…`, `photo-1494790108377…`, `photo-1500648767791…`, `photo-1438761681033…`, `photo-1472099645785…`, `photo-1544005313…` | Replace with real customer initials/avatars or remove |

Full URLs follow the pattern:
`https://images.unsplash.com/<photo-id>?auto=format&fit=crop&q=70&w=<width>`

Tip: keep `w=` close to the display size (cards ~900, heroes ~1800) so pages stay fast.
