# Image credits

All photographs are licensed under the [Pexels License](https://www.pexels.com/license/)
(free for commercial use, no attribution required — credited here as good practice).
**No AI-generated images are used anywhere on this site.**

Photos are self-hosted via `scripts/fetch_images.py` into `dist/images/`. Each
`<img>` also carries a `data-cdn` fallback to the Pexels CDN, so pages render
even before the self-host step runs.

| File | Subject | Source |
|------|---------|--------|
| family-kitchen.jpg | Happy family in a bright modern kitchen (hero) | pexels.com/photo/3935320 |
| kitchen-sink.jpg | Modern kitchen sink & tap | pexels.com/photo/6419128 |
| hot-water.jpg | Wall-mounted hot water unit | pexels.com/photo/3964736 |
| pipe-repair.jpg | Plumber repairing pipework | pexels.com/photo/8487376 |
| gas-flame.jpg | Blue gas flame | pexels.com/photo/6024314 |
| dripping-tap.jpg | Dripping tap | pexels.com/photo/1463917 |
| finished-bath.jpg | Finished modern bathroom | pexels.com/photo/6585757 |
| technician.jpg | Smiling plumbing technician | pexels.com/photo/8487371 |
| handshake.jpg | Customer handshake | pexels.com/photo/4246119 |
| blocked-drain.jpg | Clearing a blocked drain | pexels.com/photo/6419122 |
| vancouver.jpg | Greater Vancouver skyline | pexels.com/photo/2382681 |

> Before launch, confirm each photo ID still resolves and matches the described
> subject (Pexels IDs are stable but content should be eyeballed). Swap any that
> don't fit — just edit the `IMG` table in `build.py` and re-run the build.
