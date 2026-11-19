"""Direction for "The Mpemba Effect" (30 s science explainer): shot windows, visual cues and sound cues, all keyed to
the narration's word timings (assets/lines.json). Writes direction.json (make_audio.py) and direction.js (window.D).

usage: python build_direction.py   (after make_dialogue.py)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
E = lambda i: L[i]["e"]
r = lambda x: round(x, 3)


def W(i, word, end=False, nth=0):
    hits = [w for w in L[i]["words"] if w["w"].lower().strip(".,?!:").startswith(word.lower())]
    return hits[nth]["e"] if end else hits[nth]["s"]


# shots: [start, name]  (each narration line is one shot; whip-pans and the dive sit on the cuts)
shots = [[0, "race"], [S(1) - 0.08, "gauge"], [S(2) - 0.05, "evap"], [S(3) - 0.05, "xray"], [S(4) - 0.05, "molecules"], [S(5) - 0.05, "payoff"]]
cues = {
    "freezeL": [r(1.2), r(W(0, "freezes", True))],            # ice spiderwebs across the hot beaker first
    "mpemba": r(W(1, "mpemba")),                                # title pop
    "gaugeDrop": [r(S(1) + 0.3), r(E(1) - 0.2)],                # columns fall toward 0 °C, uncertain band at 0…-5 °C
    "evap": [r(S(2)), r(E(2))],                                 # level drops ~4.5 % below the dashed line
    "xray": [r(S(3)), r(E(3))],
    "nucleate": r(W(4, "warmer") - 0.1),                        # warmer-origin sample snaps into the lattice
    "stamp": r(W(5, "experiment") + 0.05),                      # OBSERVED — STILL DEBATED
    "whipOut": r(DUR - 0.55),                                   # whip back to the opening frame (loop)
}
badges = [["THEORY 1: EVAPORATION", r(S(2) + 0.05), r(E(2))], ["THEORY 2: CONVECTION", r(S(3) + 0.05), r(E(3))],
          ["THEORY 3: LESS SUPERCOOLING", r(S(4) + 0.05), r(E(4))]]
sfx = [["impact_deep", 0.0, -4], ["timer_tick", 0.35, -15], ["ice_crackle", 1.6, -9], ["ice_crackle", 3.3, -11],
       ["whoosh_fast", r(S(1) - 0.12), -6], ["pop", r(W(1, "mpemba") + 0.02), -5],
       ["whoosh_soft", r(S(2) - 0.08), -9], ["steam_hiss", r(S(2)), -11],
       ["whoosh_soft", r(S(3) - 0.08), -9], ["fluid_swirl", r(S(3) + 0.3), -10], ["fluid_swirl", r(S(3) + 2.5), -12],
       ["whoosh_fast", r(S(4) - 0.1), -7], ["sparkle", r(cues["nucleate"]), -8], ["ice_lock", r(cues["nucleate"] + 0.05), -7],
       ["ice_thud", r(S(5)), -5], ["pop", r(cues["stamp"]), -7], ["riser", r(DUR - 2.5), -23], ["whoosh_fast", r(cues["whipOut"]), -16]]
tones = [["down", r(W(2, "evaporates")), 1.1, -17]]           # subtle downward tone as the level drops

out = {"DUR": DUR, "shots": [[r(a), b] for a, b in shots], "cues": cues, "badges": badges, "sfx": sfx, "tones": tones}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", out["shots"]); print("cues", cues)
