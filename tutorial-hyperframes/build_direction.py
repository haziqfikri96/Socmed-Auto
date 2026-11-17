"""Direction for the HyperFrames tutorial v2 (see STORYBOARD.md): acting, camera, the three dives through Quill's
screen ("portals"), what is typed on that screen and when, captions, emotes and sound cues. Everything is anchored
to the word timings in assets/lines.json, so the voice track is reused as is.

Writes direction.json (make_audio.py) and direction.js (window.D, index.html).
usage: python build_direction.py   (after make_dialogue.py)
"""
import json
import random
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


def words_in(text, t0, t1):
    """Whole words at speech rhythm (comments are Quill's annotation, not typed input): each word's chars share one time."""
    ws = text.split(" "); step = (t1 - t0) / max(1, len(ws)); out = []
    for i, w in enumerate(ws):
        out += [r(t0 + i * step)] * (len(w) + (1 if i < len(ws) - 1 else 0))
    return out


def typing(text, t0, t1, seed):
    """Per-character reveal times between t0 and t1 with an authored, irregular (seeded) rhythm."""
    rnd = random.Random(seed)
    gaps = [rnd.uniform(0.6, 1.4) * (2.2 if c in " /@-" else 1.0) for c in text]
    k = (t1 - t0) / sum(gaps)
    out, t = [], t0
    for g in gaps:
        t += g * k
        out.append(r(t))
    return out


# ---- the three dives through Quill's screen: [open, close]
P1 = [S(2) - 0.02, S(5) - 0.03]
P2 = [W(6, "using") - 0.25, S(7) - 0.02]
P3 = [S(8) - 0.04, S(9) - 0.02]
PORTALS = [P1, P2, P3]
OPEN, SHUT = 0.45, 0.22          # unmask in (expo-out), pull back (ease-in) before the cut

# ---- what appears on Quill's screen. Each row: [portal, kind, text, char_times]
rows = []
rows.append([0, "comment", "# you need Node 22+", words_in("# you need Node 22+", P1[0] + 0.45, W(2, "twenty-two", True))])
rows.append([0, "comment", "# and FFmpeg", words_in("# and FFmpeg", W(2, "and"), W(2, "ffmpeg"))])
rows.append([0, "cmd", "node -v", typing("node -v", W(2, "ffmpeg", True) + 0.05, W(2, "computer", True) - 0.05, 2)])
rows.append([0, "cmd", "ffmpeg -version", typing("ffmpeg -version", W(2, "computer", True), S(3) + 0.35, 3)])
C1 = "claude plugin marketplace add heygen-com/hyperframes"
rows.append([0, "cmd", C1, typing(C1, W(3, "add"), W(3, "marketplace", True) + 0.15, 4)])
C2 = "claude plugin install hyperframes@hyperframes"
rows.append([0, "cmd", C2, typing(C2, W(4, "install"), E(4) + 0.2, 5)])
# the prompt types word by word as Quill says it
spoken = [("Using", "using"), ("/hyperframes,", "slash", "hyperframes"), ("make", "make"), ("a", ("a", 0)), ("10-second", "ten-second"),
          ("intro", "intro"), ("with", "with"), ("a", ("a", 1)), ("fade-in", "fade-in"), ("title", "title")]
words6 = L[6]["words"]


def word_span(key):
    if isinstance(key, tuple):
        hits = [w for w in words6 if w["w"].lower().strip(".,?!") == key[0]]
        w = hits[key[1]]
        return w["s"], w["e"]
    w = next(w for w in words6 if w["w"].lower().strip(".,?!").startswith(key))
    return w["s"], w["e"]


prompt, ptimes = "", []
for item in spoken:
    word, keys = item[0], item[1:]
    s0, _ = word_span(keys[0])
    _, e1 = word_span(keys[-1])
    if prompt:
        prompt += " "; ptimes.append(r(s0 - 0.02))
    prompt += word
    ptimes += typing(word, s0, max(s0 + 0.08, e1 - 0.04), hash(word) % 997)
rows.append([1, "prompt", prompt, ptimes])
rows.append([2, "cmd", "npx hyperframes preview", typing("npx hyperframes preview", W(8, "preview") - 0.1, W(8, "browser", True) - 0.2, 6)])
rows.append([2, "cmd", "npx hyperframes render", typing("npx hyperframes render", W(8, "render") - 0.05, W(8, "mp4") - 0.05, 7)])
PREVIEW_AT = W(8, "browser")             # the live 9:16 preview opens
FILE_AT = W(8, "mp4") + 0.05             # my-video.mp4 lands
WORKING = [W(6, "title", True) + 0.05, P2[1] - SHUT]   # Claude Code's working indicator after the prompt

# ---- acting
dev = [
    [0, "curious", "idle"], [S(1), "happy", "typing"], [S(5), "happy", "idle"], [S(7), "curious", "chinThink"],
    [S(9), "shock", "recoil"], [S(10), "starstruck", "cheer"],
]
quill = [
    [0, "excited", "wave"], [W(0, "here"), "proud", "none"], [S(1), "happy", "none"], [S(2), "proud", "none"],
    [S(5), "happy", "none"], [S(6), "smug", "shrug"], [S(7), "happy", "none"], [S(8), "proud", "point"],
    [S(9), "cheeky", "none"], [S(10), "cheeky", "none"], [W(10, "follow"), "excited", "wave"],
]
# ---- camera outside the dives (inside a dive the camera is pushed into Quill's screen)
shots = [[0, "quillPush", 1], [S(1) - 0.03, "devClose", 1], [S(2) - 0.03, "quillClose", 1],
         [S(5) - 0.03, "devClose", 1], [S(6) - 0.03, "quillClose", 1], [S(7) - 0.03, "dev", 1],
         [S(8) - 0.03, "quillClose", 1], [S(9) - 0.03, "devClose", 1], [S(10) - 0.03, "quillEnd", 1]]
emotes = [[S(5) + 0.45, E(5) + 0.25, "dev", "question"], [S(9), E(9) + 0.25, "dev", "bang"]]
GLOW = [W(0, "here"), P1[0]]             # Quill's screen brightens before the first dive
PART2 = W(10, "part")                    # "part 2 →" appears on Quill's own screen

# ---- sound: riser -> silence -> impact on the hero dive; soft whooshes on the others; typing on real keystrokes
sfx = [["impact_deep", P1[0] + 0.37, -6], ["sparkle", P1[0] + 0.55, -14],
       ["whoosh_soft", P2[0], -10], ["whoosh_soft", P3[0], -10],
       ["ding", FILE_AT + 0.05, -9], ["pop", emotes[0][0], -10], ["ding", emotes[1][0], -6], ["sparkle", PART2, -12]]
for pi, kind, text, times in rows:
    for k, t in enumerate(times):
        if text[k] != " " and k % 2 == 0:           # every other keystroke, so it reads as typing, not a drumroll
            sfx.append(["tick", t, -20])
RISER = [P1[0] + 0.2]                                # the riser ends here, then silence until the impact

out = {"DUR": DUR, "VOL": [-10, -9], "SLP": [-10, -9], "dev": [[r(t), a, b] for t, a, b in dev],
       "quill": [[r(t), a, b] for t, a, b in quill], "shots": [[r(t), s, h] for t, s, h in shots],
       "emotes": [[r(a), r(b), w, k] for a, b, w, k in emotes], "cards": [],
       "portals": [[r(a), r(b)] for a, b in PORTALS], "OPEN": OPEN, "SHUT": SHUT,
       "rows": rows, "previewAt": r(PREVIEW_AT), "fileAt": r(FILE_AT), "working": [r(x) for x in WORKING],
       "glow": [r(x) for x in GLOW], "part2": r(PART2),
       "sfx": [[n, r(t), g] for n, t, g in sfx], "riser": [r(x) for x in RISER], "snore": [], "shakes": []}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print(f"{len(rows)} screen rows, {len(sfx)} sfx, portals {out['portals']} · {DUR:.2f}s")
