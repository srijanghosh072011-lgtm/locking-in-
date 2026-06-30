#!/usr/bin/env python3
"""Self-host the hero/service photos from Pexels (free commercial licence).

Downloads each photo referenced in build.py's IMG table into dist/images/.
If a download fails, the live pages still work: each <img> carries a data-cdn
fallback to the Pexels CDN (see app.js). Run AFTER build.py.

Usage:  python3 scripts/fetch_images.py
"""
import sys, pathlib, urllib.request, importlib.util

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build", ROOT/"build.py")
build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)

OUT = ROOT/"dist"/"images"
OUT.mkdir(parents=True, exist_ok=True)
ok = fail = 0
for key,(fn,cdn,alt) in build.IMG.items():
    dest = OUT/fn
    if dest.exists():
        continue
    try:
        req = urllib.request.Request(cdn, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        print(f"  ✓ {fn}"); ok += 1
    except Exception as e:                       # noqa: BLE001
        print(f"  ✗ {fn} ({e}) — page will use CDN fallback", file=sys.stderr); fail += 1
print(f"Done: {ok} downloaded, {fail} failed (CDN fallback covers failures).")
