"""Voice every line of script.json with ElevenLabs (word timings included), then join them into
assets/dialogue.wav and write assets/lines.json: [{who, text, s, e, words: [{w, s, e}]}].

usage: python make_dialogue.py   (needs numpy + soundfile; lines already in assets/lines/ are reused)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "tools/make_voiceover_timed.py"
VOICE = {"dev": ("bIHbv24MWmeRgasZH58o", 1.04), "quill": ("FGY2WhTYpPnrIDTdsKH5", 1.1)}  # Will, Laura
GAP = {"dev": 0.22, "quill": 0.18}
lines = json.loads((HERE / "script.json").read_text())
SR, t, chunks, out = 48000, 0.25, [], []
for i, (who, text) in enumerate(lines):
    wav, words = HERE / f"assets/lines/{i:02d}.wav", HERE / f"assets/lines/{i:02d}.json"
    if not wav.exists():
        (HERE / "assets/lines/tmp.txt").write_text(text)
        subprocess.run([sys.executable, str(TOOL), str(HERE / "assets/lines/tmp.txt"), str(wav), str(words), VOICE[who][0], str(VOICE[who][1])], check=True)
    a, sr = sf.read(wav, always_2d=True); assert sr == SR
    w = json.loads(words.read_text())
    dur = len(a) / SR
    out.append({"who": who, "text": text, "s": round(t, 3), "e": round(t + w[-1]["e"], 3),
                "words": [{"w": x["w"], "s": round(t + x["s"], 3), "e": round(t + x["e"], 3)} for x in w]})
    chunks.append((int(t * SR), a))
    t += dur + GAP[who] + (0.45 if text.endswith("?") and who == "dev" else 0)
total = t + 1.6
mix = np.zeros((int(total * SR), 2))
for i0, a in chunks: mix[i0:i0 + len(a)] += a[:, :2] if a.shape[1] > 1 else np.repeat(a, 2, axis=1)
sf.write(HERE / "assets/dialogue.wav", mix, SR, subtype="PCM_16")
(HERE / "assets/lines.json").write_text(json.dumps(out))
(HERE / "lines.js").write_text("window.LINES = " + json.dumps(out) + ";\nwindow.DUR = " + str(round(total, 2)) + ";\n")
print(f"{len(out)} lines, {total:.2f}s")
for l in out: print(f"{l['s']:6.2f}-{l['e']:6.2f} {l['who']:5} {l['text']}")
