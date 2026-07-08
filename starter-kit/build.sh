#!/bin/sh
# Build: stamp src/ -> dist/ from site.config, then GATE the output.
# The gate makes it impossible to ship the bugs that hit the last site:
#   - leftover {{TOKENS}}
#   - placeholder phone / form key / example.com
#   - SITE_URL missing or with a trailing slash (canonical-drift source)
set -eu
cd "$(dirname "$0")"

CONFIG=site.config
SRC=src
OUT=dist

[ -f "$CONFIG" ] || { echo "FAIL: $CONFIG not found"; exit 1; }

# --- validate SITE_URL up front (this is the value that broke last time) ---
SITE_URL=$(grep -E '^SITE_URL=' "$CONFIG" | head -1 | cut -d= -f2-)
[ -n "$SITE_URL" ] || { echo "FAIL: SITE_URL is empty"; exit 1; }
case "$SITE_URL" in
  */) echo "FAIL: SITE_URL must NOT end in a trailing slash: $SITE_URL"; exit 1 ;;
  http://*|https://*) : ;;
  *) echo "FAIL: SITE_URL must start with http(s)://: $SITE_URL"; exit 1 ;;
esac

# --- stamp ---
rm -rf "$OUT"; cp -r "$SRC" "$OUT"
esc() { printf '%s' "$1" | sed -e 's/[\\&|]/\\&/g'; }

while IFS= read -r line; do
  case "$line" in ''|\#*) continue ;; esac
  key=${line%%=*}; val=${line#*=}
  find "$OUT" -type f \( -name '*.html' -o -name '*.xml' -o -name '*.txt' -o -name '_headers' \) \
    -exec sed -i "s|{{${key}}}|$(esc "$val")|g" {} +
done < "$CONFIG"

# --- GATE: refuse to ship a broken build ---
# Only inspect stamped, deployable content (HTML/XML/TXT/_headers). js/ and css/
# are hand-written code and legitimately contain strings like 'YOUR_' or '{{'.
CONTENT="$OUT/index.html $OUT/404.html $OUT/sitemap.xml $OUT/robots.txt $OUT/_headers"
set -- $CONTENT; kept=""; for f in "$@"; do [ -f "$f" ] && kept="$kept $f"; done; CONTENT=$kept

fail=0
if grep -no '{{[A-Z0-9_]\{1,\}}}' $CONTENT >/dev/null 2>&1; then
  echo "FAIL: unresolved tokens (add them to site.config):"; grep -rno '{{[A-Z0-9_]\{1,\}}}' $CONTENT | sort -u; fail=1
fi
for bad in "555-01" "555-1234" "YOUR_" "REPLACE_WITH" "example.com" "example.ca" "lorem" "TODO"; do
  if grep -niF "$bad" $CONTENT >/dev/null 2>&1; then
    echo "FAIL: placeholder still present: '$bad'"; grep -niF "$bad" $CONTENT | head -3; fail=1
  fi
done

# canonical / og:url / sitemap / robots must all carry the SAME host
host=$(printf '%s' "$SITE_URL" | sed -E 's#https?://##; s#/.*##')
for f in "$OUT/index.html" "$OUT/sitemap.xml" "$OUT/robots.txt"; do
  [ -f "$f" ] || continue
  if grep -q 'http' "$f" && ! grep -q "$host" "$f"; then
    echo "FAIL: $f has absolute URLs that don't match SITE_URL host ($host)"; fail=1
  fi
done

[ "$fail" -eq 0 ] || { echo; echo "Build gated. Fix the above, re-run ./build.sh"; exit 1; }
echo "OK — built to $OUT/ for host: $host"
echo "Next: run PRE-LAUNCH.md checks (Lighthouse, Rich Results, JS-off), then deploy $OUT/"
