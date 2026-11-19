"""Direction for HyperFrames tutorial Part 3 ("why your AI video looks like a PowerPoint"), same system as Part 1: acting, camera,
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
    on = np.where(env > env.max() * 0.05)[0]
    end = round(l["s"] + on[-1] / sr + 0.03, 3)
    start = round(l["s"] + on[0] / sr, 3)
    if start > l["words"][0]["s"]:
        l["words"][0]["s"] = min(start, l["words"][0]["e"] - 0.05)
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


# ---- two dives through Quill's screen: [open, close]
P0 = [S(2) - 0.02, S(3) - 0.03]            # the prompt (camera zoom / spring text physics / SFX)
P1 = [S(5) - 0.04, S(7) - 0.03]            # before vs after preview
PORTALS = [P0, P1]
OPEN, SHUT = 0.45, 0.18

PROMPT = "Add camera zoom, spring text physics, and whoosh + impact SFX"
# each prompt word appears whole on the matching spoken word
spoken = [("Add", W(2, "three")), ("camera", W(2, "camera")), ("zoom,", W(2, "zoom")), ("spring", W(2, "spring")),
          ("text", W(2, "text")), ("physics,", W(2, "physics")), ("and", W(2, "and")), ("whoosh", W(2, "sound")),
          ("+", W(2, "sound") + 0.12), ("impact", W(2, "effects")), ("SFX", W(2, "effects") + 0.16)]
ptimes, built = [], ""
for n, (w, at) in enumerate(spoken):
    if n: built += " "; ptimes.append(r(at - 0.01))
    built += w; ptimes += [r(at)] * len(w)
assert built == PROMPT, built
rows = [[0, "prompt", PROMPT, ptimes]]
HL = [["camera zoom", r(W(2, "zoom", True))], ["spring text physics", r(W(2, "physics", True))], ["SFX", r(W(2, "effects") + 0.2)]]
WORKING = [r(E(2) + 0.05), r(P0[1] - SHUT + 0.02)]
HOLDS = {}

PREVIEW_AT = P1[0] + OPEN * 0.6              # preview + timeline slide in as the dive opens
FLAT_AT = W(5, "flat")                       # BEFORE: the title just fades in, no sound
AFTER_AT = S(6) - 0.05                       # riser + whoosh flip the badge to AFTER and light the SFX track
SPRING_AT = W(6, "snappy")                   # AFTER: the title springs in (the film's one visible spring)
MUTE = [r(PREVIEW_AT), r(AFTER_AT)]          # the music bed drops away during BEFORE: flat and silent

dev = [[0, "unimpressed", "shrug"], [S(1), "curious", "idle"], [S(3), "curious", "chinThink"], [S(4), "curious", "idle"],
       [S(7), "starstruck", "amazed"], [S(8), "happy", "idle"]]
quill = [[0, "happy", "none"], [S(1), "smug", "shrug"], [W(1, "watch"), "proud", "point"], [S(2), "proud", "none"],
         [S(4), "sly", "none"], [S(5), "proud", "none"], [S(8), "proud", "point"], [S(9), "excited", "wave"]]
shots = [[0, "devPush", 1], [S(1) - 0.03, "quillClose", 1], [S(3) - 0.03, "devClose", 1], [S(4) - 0.03, "quillClose", 1],
         [S(7) - 0.03, "devClose", 1], [S(8) - 0.03, "quillClose", 1], [S(9) - 0.03, "quillEnd", 1]]
emotes = [[S(3) + 0.25, S(4) - 0.06, "dev", "question"], [S(7) + 0.05, S(8) - 0.06, "dev", "bang"]]
GLOW = [W(1, "watch") - 0.15, P0[0]]         # soft cyan edge glow + riser into dive 1
SAVE = S(9)                                  # "save & try →" on Quill's face
LOOP = DUR - 0.25

sfx = [["impact_deep", P0[0] + 0.37, -6], ["sparkle", P0[0] + 0.55, -14], ["whoosh_soft", P1[0], -10],
       ["pop", emotes[0][0], -10], ["ding", emotes[1][0], -6], ["sparkle", SAVE, -10],
       ["riser", AFTER_AT - 2.48 + 0.1, -18], ["whoosh_fast", AFTER_AT - 0.2, -8], ["impact_deep", AFTER_AT + 0.05, -5],
       ["pop", SPRING_AT, -8], ["sparkle", W(6, "sound"), -9], ["impact_deep", W(6, "hits"), -9]]
sfx += [["pop", t, -15] for _, t in HL]
for n, (w, at) in enumerate(spoken):
    sfx.append(["tick", at, -19])
RISER = [P0[0] + 0.2]
for _r in rows: assert _r[3] == sorted(_r[3]), ("typing runs backwards", _r[2])

out = {"DUR": DUR, "VOL": [-10, -9], "SLP": [-10, -9], "dev": [[r(t), a, b] for t, a, b in dev],
       "quill": [[r(t), a, b] for t, a, b in quill], "shots": [[r(t), s, h] for t, s, h in shots],
       "emotes": [[r(a), r(b), w, k] for a, b, w, k in emotes], "cards": [],
       "portals": [[r(a), r(b)] for a, b in PORTALS], "OPEN": OPEN, "SHUT": SHUT, "rows": rows,
       "holds": HOLDS, "hold": 999, "hl": HL, "pvPortal": 1, "previewAt": r(PREVIEW_AT), "flatAt": r(FLAT_AT),
       "afterAt": r(AFTER_AT), "springAt": r(SPRING_AT), "mute": MUTE, "fileAt": 999, "orangeAt": 999,
       "working": WORKING, "vid": [999, 999], "glow": [r(x) for x in GLOW], "part2": r(SAVE), "loop": r(LOOP),
       "sfx": [[n, r(t), g] for n, t, g in sfx], "riser": [r(x) for x in RISER], "snore": [], "shakes": []}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
for _r in rows: assert _r[3] == sorted(_r[3]) and _r[3][0] < _r[3][-1] + 1e-9, ("typing runs backwards", _r[2])
print(f"{len(rows)} screen rows, {len(sfx)} sfx, portals {out['portals']} · {DUR:.2f}s")
