"""Build the skit's direction (acting, camera, cards, emotes, sound cues) from the word timings in assets/lines.json.

Every beat is anchored to a line or a word, so re-voicing or retiming the dialogue keeps everything in sync.
Writes direction.json (read by make_audio.py) and direction.js (window.D, read by index.html).

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
    """Start (or end) of the first word in line i that starts with `word` (case-insensitive)."""
    for w in L[i]["words"]:
        if w["w"].lower().strip(".,?!").startswith(word.lower()):
            return w["e"] if end else w["s"]
    raise KeyError(f"{word!r} not in line {i}: {L[i]['text']}")


r = lambda x: round(x, 3)
VOL = [S(13) - 0.05, W(15, "remember")]             # volcano video: "Done." -> into Quill's next line
SLP = [W(17, "asleep") - 0.1, E(17) + 0.04]          # the phone clip of Shichi asleep, under "Asleep at your desk. Two million views."
HOOK = 1.0                                           # first second: punch-in from the monitor's point of view

# Shichi: [time, expression, pose]. One expression per beat; it changes only when something happens.
dev = [
    [0, "shock", "recoil"], [S(1), "confused", "handsHips"], [S(2), "unimpressed", "shrug"], [S(3), "confused", "crossArms"],
    [S(4), "shock", "recoil"], [S(5), "curious", "idle"], [W(5, "real"), "happy", "idle"],
    [S(6), "suspicious", "chinThink"], [S(7), "hopeful", "idle"], [S(8), "happy", "idle"], [S(10), "hopeful", "idle"],
    [S(11), "happy", "idle"], [S(12), "happy", "point"], [S(14), "starstruck", "amazed"], [S(15), "happy", "idle"],
    [W(15, "remember"), "suspicious", "crossArms"], [S(16), "suspicious", "handsHips"], [S(17), "worried", "idle"],
    [SLP[0], "asleep", "sleep"], [SLP[1], "horror", "recoil"], [S(18), "angry", "angry"], [S(19) + 0.3, "unimpressed", "handsHips"],
]
# Quill: [time, mood, gesture]
quill = [
    [0, "innocent", "none"], [W(0, "final"), "nervous", "none"], [S(1), "innocent", "shrug"], [S(2), "neutral", "none"],
    [S(3), "proud", "point"], [W(3, "hyperframes"), "excited", "point"], [S(4), "proud", "none"], [S(5), "excited", "cheer"],
    [S(6), "neutral", "none"], [S(7), "smug", "shrug"], [W(7, "you"), "proud", "none"], [S(8), "happy", "none"], [S(9), "happy", "point"],
    [S(10), "happy", "none"], [S(11), "proud", "cheer"], [S(12), "happy", "none"], [S(13), "proud", "wave"], [S(15), "sly", "none"],
    [S(17), "innocent", "shrug"], [S(18) + 0.05, "wince", "cover"], [S(19), "cheeky", "shrug"], [S(20), "cheeky", "wave"],
]
# Camera: always on whoever is talking; reaction cutaways are 0.8 s or less. [time, shot, hard cut]
shots = [[0, "hookPunch", 1], [W(0, "final") + 0.08, "quillClose", 1], [W(0, "final") + 0.78, "hookHold", 1]]   # 0.7 s nervous-Quill reaction on "final final v3"
for i, line in enumerate(L):
    if i == 0:
        continue
    shot = {"dev": "dev", "quill": "quill"}[line["who"]]
    if i in (4, 10, 16, 18):
        shot = "devClose"                   # short exclamations get a close-up
    if i in (15, 19):
        shot = "quillClose"
    if i == 14:
        shot = "devLow"                     # "Whoa." under the volcano card
    shots.append([S(i) - 0.03, shot, 1 if line["who"] != L[i - 1]["who"] else 0])
shots.append([S(17) + 0.05, "devClose", 1])          # worried reaction to "It's you." (gulp), straight into the sleep clip
shots.append([SLP[0], "sleepCam", 1])
shots = sorted(shots, key=lambda x: x[0])
# Emotes: [from, to, who, kind] with kind in bang | question | sparkle | sweat | anger
emotes = [
    [S(4) + 0.05, E(4) + 0.2, "dev", "bang"], [W(6, "who"), E(6) + 0.2, "dev", "question"], [S(10), E(10) + 0.4, "dev", "sparkle"],
    [S(14), E(14) + 0.25, "dev", "sparkle"], [S(16), E(16) + 0.1, "dev", "question"], [S(17) + 0.12, S(17) + 0.85, "dev", "sweat"],
    [S(18), S(19) + 0.4, "dev", "anger"],
]
# Cards: [id, from, to]
cards = [
    ["cHtml", W(3, "hyperframes") - 0.1, E(3) + 0.02], ["cFeat", S(5), E(5) + 0.02], ["cTerm", S(9), S(11) - 0.02],
    ["cGit", S(11) - 0.02, E(11) + 0.02], ["cCta", S(20), DUR + 1],
]
# Sound cues for make_audio.py: [effect, time, gain dB]
EMOTE_SFX = {"bang": ("ding", -4), "question": ("pop", -6), "sparkle": ("sparkle", -6), "sweat": ("gulp", -4), "anger": ("sting", -2)}
sfx = [[EMOTE_SFX[k][0], t0, EMOTE_SFX[k][1]] for t0, _, _, k in emotes]
sfx += [["pop", 0.3, -8], ["impact_deep", 0.02, -9]]                              # hook: file icon bounce, punch-in
sfx += [["pop", c[1], -9] for c in cards[:4]]                                     # card springs
sfx += [["ding", W(3, "mp4") + 0.1, -10]]                                          # MP4 done
sfx += [["tick", S(9) + 0.2 + k * 0.07, -18] for k in range(28)] + [["ding", S(9) + 2.3, -10]]   # typing the install commands
sfx += [["ding", S(13) + 0.05, -10], ["eruption", VOL[0] + 0.25, -5]]              # render done, volcano erupts
sfx += [["counter", W(17, "two"), -12]]                                            # views racing up
sfx += [["impact_deep", S(18), -3]]                                                # rage: bass hit under the sting
RISER = [S(17) - 0.15]                                                             # riser ends here, then dead silence until "It's you."
SNORE = [SLP[0] + 0.1, -6]                                                         # snore, 6 dB down + low-pass
SHAKES = [[S(18), 4 / 30]]                                                         # 4-frame camera shake on "Quill!"

out = {"DUR": DUR, "VOL": [r(x) for x in VOL], "SLP": [r(x) for x in SLP], "HOOK": HOOK,
       "dev": [[r(t), a, b] for t, a, b in dev], "quill": [[r(t), a, b] for t, a, b in quill],
       "shots": [[r(t), s, h] for t, s, h in shots], "emotes": [[r(a), r(b), w, k] for a, b, w, k in emotes],
       "cards": [[c, r(a), r(b)] for c, a, b in cards], "sfx": [[n, r(t), g] for n, t, g in sfx],
       "riser": [r(x) for x in RISER], "snore": [r(SNORE[0]), SNORE[1]], "shakes": [[r(a), r(b)] for a, b in SHAKES],
       "viewsDone": r(W(17, "million", end=True))}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print(f"{len(dev)} dev beats, {len(quill)} quill beats, {len(shots)} shots, {len(emotes)} emotes, {len(sfx)} sfx · {DUR:.2f}s")
print("volcano", out["VOL"], "sleep clip", out["SLP"], "views 2.0M by", out["viewsDone"])
