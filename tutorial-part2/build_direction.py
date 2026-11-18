"""Direction for HyperFrames tutorial Part 2 ("your first real video"), same system as Part 1: acting, camera,
four dives through Quill's screen, what appears on it, captions, emotes, sound cues. Anchored to word timings.

Writes direction.json (make_audio.py), direction.js (window.D) and a trimmed lines.js (index.html).
usage: python build_direction.py   (after make_dialogue.py)
"""
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
# trim every line's last word to where the voice really stops (the aligner pads ~0.3 s of silence)
for l in L:
    k = hashlib.sha1(f"{l['who']}|{l['text']}".encode()).hexdigest()[:12]
    a, sr = sf.read(HERE / f"assets/lines/{k}.wav"); a = np.abs(a if a.ndim == 1 else a.mean(1))
    env = np.convolve(a, np.ones(int(0.02 * sr)) / int(0.02 * sr), "same")
    end = round(l["s"] + np.where(env > env.max() * 0.05)[0][-1] / sr + 0.03, 3)
    if end < l["e"]:
        l["e"] = end; l["words"][-1]["e"] = max(l["words"][-1]["s"] + 0.1, end)
(HERE / "lines.js").write_text("window.LINES = " + json.dumps(L) + ";\nwindow.DUR = " + str(DUR) + ";\n")
S = lambda i: L[i]["s"]
E = lambda i: L[i]["e"]
r = lambda x: round(x, 3)


def W(i, word, end=False):
    for w in L[i]["words"]:
        if w["w"].lower().strip(".,?!:").startswith(word.lower()):
            return w["e"] if end else w["s"]
    raise KeyError(f"{word!r} not in line {i}: {L[i]['text']}")


def typing(text, t0, t1, seed):
    """Per-character reveal times between t0 and t1 with an authored, irregular (seeded) rhythm."""
    rnd = random.Random(seed)
    gaps = [rnd.uniform(0.6, 1.4) * (2.2 if c in " /@-" else 1.0) for c in text]
    k = (t1 - t0) / sum(gaps); out, t = [], t0
    for g in gaps:
        t += g * k; out.append(r(t))
    return out


# ---- four dives through Quill's screen: [open, close]
P0 = [S(2) - 0.02, S(3) - 0.03]            # init + cd
P1 = [W(4, "just") - 0.25, S(6) - 0.02]    # describe it (prompt) + be specific (highlights)
P2 = [S(7) - 0.04, S(8) - 0.02]            # preview -> Studio timeline -> "make it orange"
P3 = [S(9) - 0.04, S(10) - 0.02]           # draft vs high-quality render
PORTALS = [P0, P1, P2, P3]
OPEN, SHUT = 0.45, 0.18

rows = []
rows.append([0, "cmd", "npx hyperframes init my-video", typing("npx hyperframes init my-video", W(2, "npx") - 0.1, W(2, "name") + 0.05, 1)])
rows.append([0, "cmd", "cd my-video", typing("cd my-video", W(2, "name") + 0.12, P0[1] - SHUT - 0.3, 2)])
PROMPT = "Using /hyperframes, make a 20-second vertical video about how volcanoes erupt. Bold text, dark theme."
rows.append([1, "prompt", PROMPT, typing(PROMPT, W(4, "just"), E(4) - 0.05, 3)])
C_DRAFT, C_HIGH = "npx hyperframes render --quality draft", "npx hyperframes render --quality high"
rows.append([2, "cmd", "npx hyperframes preview", typing("npx hyperframes preview", S(7) + 0.1, W(7, "preview", True), 4)])
rows.append([3, "cmd", C_DRAFT, typing(C_DRAFT, W(9, "draft") - 0.15, W(9, "tweak", True), 5), len("npx hyperframes render")])
rows.append([3, "cmd", C_HIGH, typing(C_HIGH, W(9, "high"), W(9, "final") - 0.1, 6), len("npx hyperframes render")])
HOLDS = {0: r(P0[1] - SHUT - 0.28), 3: r(W(9, "final") - 0.05)}     # finished terminals hold still (screenshot moments)
HL = [["vertical", r(W(5, "vertical"))], ["20-second", r(W(5, "long"))]]   # "be specific": the words light up as she says them
PREVIEW_AT = W(7, "you")            # Studio opens: preview + timeline
ORANGE_AT = W(7, "orange")          # the preview turns orange as she says it
VID = [S(10) - 0.03, S(11) - 0.03]  # the finished volcano video plays above Shichi while he reacts

dev = [[0, "hopeful", "idle"], [S(1), "happy", "idle"], [S(3), "suspicious", "chinThink"], [S(4), "happy", "idle"],
       [S(6), "worried", "idle"], [S(7), "curious", "idle"], [S(8), "unimpressed", "crossArms"], [S(9), "curious", "idle"],
       [S(10), "starstruck", "amazed"], [S(11), "happy", "cheer"]]
quill = [[0, "happy", "none"], [S(1), "proud", "point"], [S(2), "proud", "none"], [S(4), "smug", "shrug"],
         [S(5), "proud", "point"], [S(6), "happy", "none"], [S(7), "proud", "none"], [S(8), "cheeky", "shrug"],
         [S(9), "proud", "point"], [S(11), "cheeky", "none"], [S(12), "excited", "wave"]]
shots = [[0, "devPush", 1], [S(1) - 0.03, "quillClose", 1], [S(3) - 0.03, "devClose", 1], [S(4) - 0.03, "quillClose", 1],
         [S(6) - 0.03, "devClose", 1], [S(7) - 0.03, "quillClose", 1], [S(8) - 0.03, "dev", 1], [S(9) - 0.03, "quillClose", 1],
         [S(10) - 0.03, "devLow", 1], [S(11) - 0.03, "quillClose", 1], [S(12) - 0.03, "quillEnd", 1]]
emotes = [[S(3) + 0.3, S(4) - 0.06, "dev", "question"], [S(6) + 0.25, S(7) - 0.06, "dev", "sweat"],
          [S(10) + 0.25, S(11) - 0.06, "dev", "sparkle"]]
GLOW = [W(1, "step"), P0[0]]
PART3 = W(12, "comment")

EMOTE_SFX = {"question": ("pop", -10), "sweat": ("gulp", -8), "sparkle": ("sparkle", -10)}
sfx = [["impact_deep", P0[0] + 0.37, -6], ["sparkle", P0[0] + 0.55, -14],
       ["whoosh_soft", P1[0], -10], ["whoosh_soft", P2[0], -10], ["whoosh_soft", P3[0], -10],
       ["pop", r(PREVIEW_AT), -12], ["ding", r(ORANGE_AT), -10], ["sparkle", PART3, -12]]
sfx += [[EMOTE_SFX[k][0], a, EMOTE_SFX[k][1]] for a, _, _, k in emotes]
sfx += [["pop", t, -14] for _, t in HL]
for pi, kind, text, times, *_ in rows:
    for k, t in enumerate(times):
        if text[k] != " " and k % 2 == 0:
            sfx.append(["tick", t, -20])
RISER = [P0[0] + 0.2]

out = {"DUR": DUR, "VOL": [-10, -9], "SLP": [-10, -9], "dev": [[r(t), a, b] for t, a, b in dev],
       "quill": [[r(t), a, b] for t, a, b in quill], "shots": [[r(t), s, h] for t, s, h in shots],
       "emotes": [[r(a), r(b), w, k] for a, b, w, k in emotes], "cards": [],
       "portals": [[r(a), r(b)] for a, b in PORTALS], "OPEN": OPEN, "SHUT": SHUT, "rows": rows,
       "holds": HOLDS, "hold": 999, "hl": HL, "previewAt": r(PREVIEW_AT), "orangeAt": r(ORANGE_AT), "fileAt": 999,
       "working": [999, 999], "vid": [r(x) for x in VID], "glow": [r(x) for x in GLOW], "part2": r(PART3), "loop": 999,
       "sfx": [[n, r(t), g] for n, t, g in sfx], "riser": [r(x) for x in RISER], "snore": [], "shakes": []}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print(f"{len(rows)} screen rows, {len(sfx)} sfx, portals {out['portals']} · {DUR:.2f}s")
