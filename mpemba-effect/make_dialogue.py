"""Voice every line of script.json with ElevenLabs (word timings included), then join them into
assets/dialogue.wav and write assets/lines.json: [{who, text, s, e, words: [{w, s, e}]}].

usage: python make_dialogue.py   (needs numpy + soundfile; lines already in assets/lines/ are reused)
"""
import hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "tools/make_voiceover_timed.py"
VOICE = {"will": ("bIHbv24MWmeRgasZH58o", 1.08)}  # Will, crisp narrator
GAP = {"will": 0.04}   # seconds from the previous line's last word to this line (tight banter)
TEMPO = 1.04                          # crisp narrator pace
TAIL = 0.3                            # the video ends this long after the final word, so it loops cleanly
lines = json.loads((HERE / "script.json").read_text())
SR, t, chunks, out = 48000, 0.25, [], []
for i, entry in enumerate(lines):
    who, text = entry[0], entry[1]
    pause = entry[2] if len(entry) > 2 else 0      # optional pause after the line (seconds)
    gain = 10 ** ((entry[3] if len(entry) > 3 else 0) / 20)  # optional vocal boost in dB
    key = hashlib.sha1(f"{who}|{text}".encode()).hexdigest()[:12]               # takes are cached by content
    wav, words = HERE / f"assets/lines/{key}.wav", HERE / f"assets/lines/{key}.json"
    if not wav.exists():
        (HERE / "assets/lines/tmp.txt").write_text(text)
        subprocess.run([sys.executable, str(TOOL), str(HERE / "assets/lines/tmp.txt"), str(wav), str(words), VOICE[who][0], str(VOICE[who][1])], check=True)
    a, sr = sf.read(wav, always_2d=True); assert sr == SR
    w = json.loads(words.read_text())
    if TEMPO != 1.0:   # pitch-preserving speed-up (cached next to the take)
        fast = wav.with_name(wav.stem + f"_x{TEMPO}.wav")
        if not fast.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", f"atempo={TEMPO}", "-ar", str(SR), str(fast)], check=True)
        a, _ = sf.read(fast, always_2d=True)
        w = [{**x, "s": x["s"] / TEMPO, "e": x["e"] / TEMPO} for x in w]
    # zero dead air: the line ends 0.05 s after the voice really stops (the aligner pads ~0.3 s)
    env = np.convolve(np.abs(a.mean(1)), np.ones(int(0.02 * SR)) / int(0.02 * SR), "same")
    vend = np.where(env > env.max() * 0.10)[0][-1] / SR + 0.05
    a = a[: int(vend * SR)]
    w[-1]["e"] = min(w[-1]["e"], vend)
    dur = len(a) / SR
    out.append({"who": who, "text": text, "s": round(t, 3), "e": round(t + w[-1]["e"], 3),
                "words": [{"w": x["w"], "s": round(t + x["s"], 3), "e": round(t + x["e"], 3)} for x in w]})
    chunks.append((int(t * SR), a * gain))
    t += w[-1]["e"] + pause
    if i + 1 < len(lines): t += GAP[lines[i + 1][0]]
total = t + TAIL
mix = np.zeros((int(total * SR), 2))
for i0, a in chunks: mix[i0:i0 + len(a)] += a[:, :2] if a.shape[1] > 1 else np.repeat(a, 2, axis=1)
sf.write(HERE / "assets/dialogue.wav", mix, SR, subtype="PCM_16")
(HERE / "assets/lines.json").write_text(json.dumps(out))
(HERE / "lines.js").write_text("window.LINES = " + json.dumps(out) + ";\nwindow.DUR = " + str(round(total, 2)) + ";\n")
print(f"{len(out)} lines, {total:.2f}s")
for l in out: print(f"{l['s']:6.2f}-{l['e']:6.2f} {l['who']:5} {l['text']}")
