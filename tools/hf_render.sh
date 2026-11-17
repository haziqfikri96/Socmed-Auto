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
# projects with a 3D scene read render-mode.js: half-res WebGL for drafts, full for the master; restored afterwards
if [[ -f render-mode.js ]]; then
  [[ $MODE == draft ]] && echo 'window.HF_DRAFT = true;   // tools/hf_render.sh sets this to true while it renders a draft' > render-mode.js
  trap "echo 'window.HF_DRAFT = false;   // tools/hf_render.sh sets this to true while it renders a draft' > render-mode.js" EXIT
fi
if [[ "${1:-}" == "--final" ]]; then
  npx --yes hyperframes@0.9.30 render --quality high --fps 30 --workers "$WORKERS" --quiet --output "../videos/$P.mp4"
elif [[ $# -ge 2 ]]; then
  npx --yes hyperframes@0.9.30 render --quality draft --fps 30 --workers "$WORKERS" --quiet --start "$1" --end "$2" --output "review-$1-$2.mp4"
else
  npx --yes hyperframes@0.9.30 render --quality draft --fps 30 --workers "$WORKERS" --quiet --output review.mp4
fi
