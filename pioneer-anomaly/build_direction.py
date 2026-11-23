"""Direction for "The Pioneer Anomaly" (27 s): shot windows, visual cues and sound cues keyed to the narration's word
timings (assets/lines.json). Writes direction.json (make_audio.py) and direction.js (window.D).

usage: python build_direction.py   (after make_dialogue.py)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
r = lambda x: round(x, 3)


def W(i, word, end=False, nth=0):
    hits = [w for w in L[i]["words"] if w["w"].lower().strip(".,?!:").startswith(word.lower())]
    return hits[nth]["e"] if end else hits[nth]["s"]


shots = [[0, "hook"], [r(S(1) - 0.08), "traj"], [r(S(2) - 0.05), "xray"], [r(S(3) - 0.05), "photon"], [r(S(4) - 0.05), "payoff"]]
cues = {
    "drag": r(W(0, "force")),                 # red drag vector appears
    "behind": r(W(1, "four")),                # 400,000 KM BEHIND callout
    "xray": r(W(2, "cracked")),               # x-ray scan switches the materials
    "heat": r(W(2, "heat")),                  # RTGs glow, infrared waves start
    "dish": r(W(2, "back")),                  # waves reflect off the back of the dish
    "accel": r(W(3, "microscopic")),          # 8.74e-10 m/s^2 label
    "backward": r(W(3, "backward")),          # sunward recoil arrows pulse
    "solved": r(S(4) + 0.1),                  # SOLVED: ANISOTROPIC HEAT
    "loop": r(DUR - 0.28),                    # whip back to the opening frame
}
# [file, time, dB relative to the voice peak]; whoosh/whip files are aligned by their peak (make_audio.py)
sfx = [["foley_sub_impact", 0.0, -4], ["pa_sonar_ping", 0.2, -10], ["pa_sonar_ping", 1.3, -16], ["foley_ui_pop", cues["drag"], -14],
       ["foley_whoosh", r(shots[1][0] + 0.1), -10], ["foley_ui_pop", cues["behind"], -12],
       ["foley_whoosh", r(shots[2][0] + 0.1), -11], ["pa_wave_sweep", cues["xray"], -12],
       ["pa_reactor_hum", cues["heat"], -14], ["pa_reactor_hum", r(cues["heat"] + 2.8), -15], ["pa_wave_sweep", cues["dish"], -13],
       ["pa_shimmer", cues["accel"], -10], ["pa_shimmer", cues["backward"], -13],
       ["foley_whoosh", r(shots[4][0] + 0.1), -12], ["foley_ui_pop", cues["solved"], -12], ["foley_sub_impact", cues["solved"], -12],
       ["bts_air_whip", r(cues["loop"] + 0.12), -10]]

out = {"DUR": DUR, "shots": shots, "cues": cues, "sfx": sfx}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", shots); print("cues", cues)
