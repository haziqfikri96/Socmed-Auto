"""Direction for the onion behind-the-scenes short (18 s). The 3D comes from the onion project's scene, driven by a
source-time map (BTS time -> onion scene time); HUD overlays sit on the full-screen 3D. Writes direction.js (window.D)
and direction.json (make_audio.py).

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


shots = [[0, "hook"], [r(S(1) - 0.03), "shader"], [r(S(2) - 0.03), "timeline"], [r(S(3) - 0.03), "render"]]
cues = {
    "eyeWipe": r(W(1, "eyeball") - 0.15),     # second wipe: from the cells to the eyeball
    "cta": 10.5,                              # early call to action (brief)
    "termOff": 15.5,                          # terminal pill snaps off
    "loop": r(DUR - 0.28),                    # whip back to frame 1
}
sfx = [["bts_sub_thud", 0.0, -4], ["ot_veg_slice", 0.0, -6], ["ot_gas_burst", 0.15, -12],
       ["foley_whoosh", r(shots[1][0] + 0.1), -10], ["ob_scan_hum", r(shots[1][0] + 0.05), -16],
       ["foley_whoosh", r(cues["eyeWipe"] + 0.1), -11], ["ob_scan_hum", r(cues["eyeWipe"] + 0.05), -17],
       ["foley_ui_pop", r(W(2, "hyperframes")), -12], ["ot_water_splash", r(shots[2][0] + 0.45), -9], ["foley_ui_pop", cues["cta"], -11],
       ["ob_key_click", r(shots[3][0] + 0.05), -10], ["bts_air_whip", r(DUR - 0.12), -10]]
out = {"DUR": DUR, "shots": shots, "cues": cues, "sfx": sfx}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", shots); print("cues", cues)
