"""Direction for the HyperFrames tutorial reply video (acting, camera, cards, emotes, sound cues),
anchored to the word timings in assets/lines.json. Writes direction.json (make_audio.py) and direction.js (index.html).

usage: python build_direction.py   (run after make_dialogue.py)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
E = lambda i: L[i]["e"]


def W(i, word, end=False):
    for w in L[i]["words"]:
        if w["w"].lower().strip(".,?!").startswith(word.lower()):
            return w["e"] if end else w["s"]
    raise KeyError(f"{word!r} not in line {i}: {L[i]['text']}")


r = lambda x: round(x, 3)
# Shichi: [time, expression, pose]
dev = [
    [0, "curious", "idle"], [S(1), "happy", "point"], [S(2), "curious", "chinThink"], [S(3), "happy", "typing"],
    [S(5), "happy", "idle"], [S(6), "curious", "chinThink"], [S(7), "hopeful", "idle"], [S(8), "amazed", "amazed"],
    [S(9), "shock", "recoil"], [S(10), "starstruck", "cheer"],
]
# Quill: [time, mood, gesture]
quill = [
    [0, "excited", "wave"], [S(1), "happy", "none"], [S(2), "proud", "point"], [S(3), "proud", "point"], [S(4), "happy", "none"],
    [S(5), "happy", "none"], [S(6), "smug", "shrug"], [W(6, "using"), "proud", "point"], [S(7), "happy", "none"],
    [S(8), "proud", "point"], [S(9), "cheeky", "none"], [S(10), "excited", "cheer"], [W(10, "follow"), "excited", "wave"],
]
# Camera: on the speaker; short exclamations get a close-up.
shots = [[0, "quillClose", 1]]
for i, line in enumerate(L):
    if i == 0:
        continue
    shot = {"dev": "dev", "quill": "quill"}[line["who"]]
    if i in (1, 9):
        shot = "devClose"
    if i == 10:
        shot = "quillClose"
    shots.append([S(i) - 0.03, shot, 1 if line["who"] != L[i - 1]["who"] else 0])
shots = sorted(shots, key=lambda x: x[0])
emotes = [[S(5) + 0.4, E(5) + 0.25, "dev", "question"], [S(7), E(7) + 0.2, "dev", "question"],
          [S(9), E(9) + 0.2, "dev", "bang"], [S(10) + 0.2, E(10), "dev", "sparkle"]]
# Cards: [id, from, to]
cards = [
    ["cTitle", 0.15, W(0, "here")],
    ["cReq", W(2, "you") - 0.05, E(2) + 0.1],
    ["cInst", S(3) - 0.02, S(5) + 0.35],
    ["cAsk", W(6, "using") - 0.1, E(6) + 0.15],
    ["cRun", S(8) - 0.02, E(8) + 0.25],
    ["cCta", S(10) - 0.02, DUR + 1],
]
EMOTE_SFX = {"bang": ("ding", -4), "question": ("pop", -6), "sparkle": ("sparkle", -6)}
sfx = [[EMOTE_SFX[k][0], t0, EMOTE_SFX[k][1]] for t0, _, _, k in emotes]
sfx += [["pop", c[1], -9] for c in cards]
sfx += [["pop", W(2, "node"), -12], ["pop", W(2, "ffmpeg"), -12]]                                   # requirement rows
T1, T2 = W(3, "add"), S(4) + 0.1                                                                      # command 1 / 2 typing starts
sfx += [["tick", T1 + k * 0.07, -18] for k in range(16)] + [["tick", T2 + k * 0.06, -18] for k in range(14)]
sfx += [["ding", E(4) + 0.15, -10]]                                                                   # installed
sfx += [["tick", W(6, "using") + k * 0.08, -19] for k in range(22)]                                   # typing the prompt
sfx += [["ding", W(8, "render") + 0.4, -10]]                                                          # MP4 done
out = {"DUR": DUR, "VOL": [-10, -9], "SLP": [-10, -9], "dev": [[r(t), a, b] for t, a, b in dev],
       "quill": [[r(t), a, b] for t, a, b in quill], "shots": [[r(t), s, h] for t, s, h in shots],
       "emotes": [[r(a), r(b), w, k] for a, b, w, k in emotes], "cards": [[c, r(a), r(b)] for c, a, b in cards],
       "sfx": [[n, r(t), g] for n, t, g in sfx], "riser": [], "snore": [], "shakes": [],
       "T1": r(T1), "T2": r(T2), "nodeAt": r(W(2, "node")), "ffAt": r(W(2, "ffmpeg")),
       "previewAt": r(W(8, "preview")), "renderAt": r(W(8, "render")), "freeAt": r(W(10, "free")), "openAt": r(W(10, "open"))}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print(f"{len(dev)} dev beats, {len(quill)} quill beats, {len(shots)} shots, {len(emotes)} emotes, {len(sfx)} sfx · {DUR:.2f}s")
