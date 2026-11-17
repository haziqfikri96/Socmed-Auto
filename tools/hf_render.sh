#!/usr/bin/env bash
# Fast HyperFrames renders. Draft by default; master quality only when asked.
#   tools/hf_render.sh <project>                 full draft  -> <project>/review.mp4
#   tools/hf_render.sh <project> 27 29           test clip   -> <project>/review-27-29.mp4
#   tools/hf_render.sh <project> --final         master      -> videos/<project>.mp4
# Audio is never regenerated here: run make_dialogue.py / make_audio.py yourself (both reuse cached takes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
P="${1:?project folder}"; shift
WORKERS="${HF_WORKERS:-3}"
cd "$ROOT/$P"
MODE=draft; [[ "${1:-}" == "--final" ]] && MODE=final
OUT="$PWD"
# 3D projects: drafts render from a temporary copy whose render-mode.js says HF_DRAFT = true (half-res WebGL),
# so the tracked render-mode.js (full quality) is never modified.
if [[ $MODE == draft && -f render-mode.js ]]; then
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  cp -a . "$TMP/"; rm -f "$TMP"/review*.mp4
  echo 'window.HF_DRAFT = true;' > "$TMP/render-mode.js"
  cd "$TMP"
fi
if [[ "${1:-}" == "--final" ]]; then
  npx --yes hyperframes@0.9.30 render --quality high --fps 30 --workers "$WORKERS" --quiet --output "../videos/$P.mp4"
elif [[ $# -ge 2 ]]; then
  npx --yes hyperframes@0.9.30 render --quality draft --fps 30 --workers "$WORKERS" --quiet --start "$1" --end "$2" --output "$OUT/review-$1-$2.mp4"
else
  npx --yes hyperframes@0.9.30 render --quality draft --fps 30 --workers "$WORKERS" --quiet --output "$OUT/review.mp4"
fi
