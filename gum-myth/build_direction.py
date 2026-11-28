"""Direction for "Does swallowed gum really stay for 7 years?" (20 s): shot windows, visual cues and sound cues keyed
to the narration's word timings (assets/lines.json). Writes direction.json (make_audio.py) and direction.js (window.D).

usage: python build_direction.py   (after make_dialogue.py)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
r = lambda x: round(x, 3)


def W(i, word):
    return next(w for w in L[i]["words"] if w["w"].lower().strip(".,?!:").startswith(word.lower()))["s"]


# hook + stomach share one set (the camera pushes in); intestine + choice share the tunnel; exit is outside the tunnel end
shots = [[0, "hook"], [r(S(1) - 0.06), "stomach"], [r(S(2) - 0.05), "intestine"], [r(S(3) - 0.05), "choice"], [r(S(4) - 0.05), "exit"]]
cues = {
    "impact": 0.95,                                            # gum hits the acid pool
    "dissolve": r(W(1, "dissolve")), "sugar": r(W(1, "sugar")), "sweet": r(W(1, "sweeteners")), "mint": r(W(1, "mint")),
    "boing": r(W(1, "and") - 0.05),                            # rubber core bounces once the coatings are gone
    "rubber": r(W(2, "rubber")), "stamp": r(W(2, "can't")), "muscle": r(W(2, "muscle")), "shatter": r(W(2, "push")),
    "card": r(S(3) + 0.08), "swallow": r(W(3, "swallow")), "spit": r(W(3, "spit")), "comment": r(W(3, "comment")),
    "out": r(W(4, "exits")), "days": r(W(4, "one")),
    "loop": r(DUR - 0.25),                                     # 0.25 s upward whip back to frame 1
}
# [file, time, dB relative to the voice peak]; whoosh/whip files are aligned by their peak (make_audio.py)
sfx = [["gm_gulp_drop", 0.0, -6], ["gm_acid_splash", cues["impact"], -6], ["ot_bubble_pops", r(cues["impact"] + 0.5), -16],
       ["gm_fizz", r(cues["sugar"] - 0.1), -10], ["gm_fizz", r(cues["mint"] - 0.1), -13], ["gm_boing", cues["boing"], -8],
       ["foley_whoosh", r(shots[2][0] + 0.1), -10], ["gm_stamp", cues["stamp"], -6],
       ["gm_squeeze", r(cues["muscle"] - 0.05), -8], ["gm_squeeze", r(cues["muscle"] + 0.95), -12], ["ot_frost_chime", r(cues["shatter"] + 0.05), -14],
       ["bts_soft_whoosh", r(cues["card"]), -14], ["foley_ui_pop", cues["swallow"], -10], ["foley_ui_pop", cues["spit"], -10],
       ["foley_whoosh", r(shots[4][0] + 0.02), -12], ["gm_bubble_pop", cues["out"], -6], ["sparkle", r(cues["out"] + 0.05), -14],
       ["foley_ui_pop", cues["days"], -12], ["bts_air_whip", r(cues["loop"] + 0.14), -10]]

out = {"DUR": DUR, "shots": shots, "cues": cues, "sfx": sfx}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", shots); print("cues", cues)
