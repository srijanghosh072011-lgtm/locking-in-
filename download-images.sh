#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Download the real (licensed) Pexels photos this site uses, and self-host them.
#
# By default the site references these photos via the Pexels CDN, so they work
# the moment you open or deploy it. For production you may prefer to self-host
# (faster, no third-party dependency). Run this from the project root:
#
#     bash download-images.sh
#
# It downloads the images to assets/img/ and rewrites <img src> in the built
# HTML to point at the local copies. Re-run after `python3 build.py`.
# All images are free for commercial use under the Pexels License (see CREDITS.md).
# ---------------------------------------------------------------------------
set -eu
cd "$(dirname "$0")"
mkdir -p assets/img

PAIRS="4262167:hero-family 6419128:pipe-repair 8978316:technician 3173206:hot-water 6782428:bathroom 6444979:bathroom-2 9462224:kitchen-drain 6126281:gas-flame 8112851:leak-tap"

for pair in $PAIRS; do
  id="${pair%%:*}"; name="${pair##*:}"
  url="https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=1600"
  echo "downloading ${name}.jpg ..."
  curl -fsSL "$url" -o "assets/img/${name}.jpg"
done

echo "localising <img src> in built HTML -> /assets/img ..."
python3 - <<'PY'
import re, glob, os
IMG = {"4262167":"hero-family","6419128":"pipe-repair","8978316":"technician",
       "3173206":"hot-water","6782428":"bathroom","6444979":"bathroom-2",
       "9462224":"kitchen-drain","6126281":"gas-flame","8112851":"leak-tap"}
files = []
for d in [".", "services", "locations", "blog", "legal", "admin"]:
    files += glob.glob(os.path.join(d, "*.html"))
# Only rewrite <img src="..."> — leaves og:image / JSON-LD as absolute CDN URLs.
pat = re.compile(r'src="https://images\.pexels\.com/photos/(\d+)/[^"]*"')
def repl(m):
    name = IMG.get(m.group(1))
    return 'src="/assets/img/%s.jpg"' % name if name else m.group(0)
for f in files:
    s = open(f, encoding="utf-8").read()
    ns = pat.sub(repl, s)
    if ns != s:
        open(f, "w", encoding="utf-8").write(ns)
        print("  updated", f)
print("done.")
PY
echo "Self-hosting complete. Commit assets/img/*.jpg and the updated HTML."
