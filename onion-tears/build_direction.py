"""Direction for "Why Do Onions Make You Cry?" (20 s, kids): shot windows, visual cues and sound cues keyed to the
narration's word timings (assets/lines.json). Writes direction.json (make_audio.py) and direction.js (window.D).

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


# the eye shot carries both the nerve line and the tear line; the fridge shot carries the fridge tip
shots = [[0, "board"], [r(S(1) - 0.06), "cells"], [r(S(2) - 0.05), "eye"], [r(S(4) - 0.06), "fridge"], [r(W(4, "comment") - 0.1), "outro"]]
cues = {
    "pop": r(W(1, "cells")), "enzyme": r(W(1, "enzymes")), "gas": r(W(1, "stinging")),
    "hit": r(W(2, "hits")), "nerve": r(W(2, "pain")), "panic": r(W(3, "panic")), "tears": r(W(3, "flooding")),
    "fridge": r(W(4, "fridge")), "slow": r(W(4, "slow")),
}
# [file, time, dB relative to the voice peak]; whoosh/whip files are aligned by their peak (make_audio.py)
sfx = [["ot_veg_slice", 0.0, -6], ["ot_gas_burst", 0.15, -9],
       ["foley_whoosh", r(shots[1][0] + 0.1), -10], ["ot_bubble_pops", cues["pop"], -10], ["foley_ui_pop", cues["enzyme"], -14], ["ot_bubble_pops", cues["gas"], -11],
       ["foley_whoosh", r(shots[2][0] + 0.1), -11], ["ot_gas_burst", cues["hit"], -15], ["foley_ui_pop", cues["nerve"], -12],
       ["ot_alarm_ding", cues["panic"], -9], ["ot_water_splash", cues["tears"], -9], ["ot_water_splash", r(cues["tears"] + 0.8), -13],
       ["bts_soft_whoosh", r(shots[3][0] + 0.08), -10], ["ot_frost_chime", cues["fridge"], -10], ["foley_ui_pop", cues["slow"], -12],
       ["foley_whoosh", r(shots[4][0] + 0.1), -11], ["bts_air_whip", r(DUR - 0.12), -10]]

out = {"DUR": DUR, "shots": shots, "cues": cues, "sfx": sfx}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", shots); print("cues", cues)
