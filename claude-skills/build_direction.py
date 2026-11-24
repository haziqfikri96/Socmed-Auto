"""Direction for "Stop Installing Claude Skills Manually" (~28 s, 3D lab cut): shot windows, kinetic-type and UI cues and sound
cues keyed to the narration's word timings (assets/lines.json). Writes direction.js (window.D) and direction.json.

usage: python build_direction.py   (after make_dialogue.py)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
r = lambda x: round(x, 3)


def W(i, word, nth=0, end=False):
    hits = [w for w in L[i]["words"] if w["w"].lower().strip(".,?!:'").startswith(word.lower())]
    return hits[nth]["e"] if end else hits[nth]["s"]


shots = [[0, "hook"], [r(S(1) - 0.05), "github"], [r(S(2) - 0.05), "save"], [r(S(3) - 0.05), "demo"], [r(S(4) - 0.05), "checks"], [r(S(5) - 0.05), "cta"]]
cues = {
    "h1": r(W(0, "stop")), "h2": r(W(0, "claude")), "h3": r(W(0, "manually")), "h4": r(W(0, "one")),
    "thousands": r(W(1, "thousands")), "wasting": r(W(1, "wasting")), "thirty": r(W(1, "thirty")), "readme": r(W(1, "readme")), "painful": r(W(1, "painful")),
    "save": r(W(2, "save")), "forget": r(W(2, "forget")), "name": r(W(2, "find")),
    "cmd0": r(W(3, "n-p-x")), "cmd1": r(W(3, "skills", 1, True)), "ask0": r(W(3, "just")), "ask1": r(W(3, "this", 0, True)),
    "search": r(W(3, "searches")), "verify": r(W(3, "verifies")), "install": r(W(3, "installs")),
    "c1": r(W(4, "no")), "c2": r(W(4, "no", 1)), "c3": r(W(4, "the")),
    "cta": r(W(5, "comment")), "follow": r(W(5, "follow")),
    "loop": r(DUR - 0.28),
}
# [file, time, dB relative to the voice peak]; whoosh/whip files are aligned by their peak (make_audio.py)
sfx = [["sk_tactile_pop", cues["h1"], -9], ["ob_key_click", cues["h2"], -10], ["sk_tactile_pop", cues["h3"], -11],
       ["foley_whoosh", r(shots[1][0] + 0.15), -11], ["sk_scroll_ticks", cues["wasting"], -11], ["sk_error_thud", cues["readme"], -9],
       ["bts_soft_whoosh", r(shots[2][0] + 0.08), -11], ["sk_mouse_click", cues["save"], -8], ["sk_chime", r(cues["save"] + 0.18), -10],
       ["bts_sub_thud", r(shots[2][0] + 0.05), -10],   # Quill zaps the README stack away
       ["foley_whoosh", r(shots[3][0] + 0.12), -12], ["sk_typing", cues["cmd0"], -13], ["sk_chime", r(cues["cmd1"] + 0.1), -12],   # orb spawns
       ["sk_typing", cues["ask0"], -14], ["foley_ui_pop", cues["search"], -11],
       ["sk_pops_up", cues["c1"], -11], ["sk_tactile_pop", cues["c2"], -12], ["sk_tactile_pop", cues["c3"], -11],
       ["bts_soft_whoosh", r(shots[5][0] + 0.08), -11], ["sk_tactile_pop", cues["cta"], -10], ["foley_ui_pop", cues["follow"], -12],
       ["bts_air_whip", r(DUR - 0.12), -10]]
out = {"DUR": DUR, "shots": shots, "cues": cues, "sfx": sfx}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("shots", shots); print("cues", cues)
