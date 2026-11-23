#!/usr/bin/env bash
# Renders the three caption-free Mpemba hero clips this short is built from into assets/ (MP4s are gitignored).
# Full quality, from a temporary copy of ../mpemba-effect with its captions hidden.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp -a "$HERE/../mpemba-effect/." "$TMP/"; rm -rf "$TMP"/review*.mp4 "$TMP/.hyperframes"
sed -i 's/#cap { position: absolute;/#cap { display: none !important; position: absolute;/' "$TMP/index.html"
sed -i 's/#stamp { position: absolute;/#stamp { display: none !important; position: absolute;/' "$TMP/index.html"   # no OBSERVED badge in the BTS
cd "$TMP"
for r in "0 4.6 race" "21.2 24.8 mol" "25.0 29.4 pay"; do set -- $r
  [[ -f "$HERE/assets/clip_$3.mp4" ]] && { echo "skip clip_$3"; continue; }
  npx --yes hyperframes@0.9.30 render --quality high --fps 30 --workers 3 --quiet --start "$1" --end "$2" --output "$HERE/assets/clip_$3.mp4"
done
