"""Direction for the Mpemba behind-the-scenes short (18 s): shot cues and sound cues keyed to the narration's word
timings (assets/lines.json), plus a voice waveform for the timeline panel. Writes direction.json (make_audio.py)
and direction.js (window.D).

usage: python build_direction.py   (after make_dialogue.py)
"""
import json
from pathlib import Path
import numpy as np, soundfile as sf

HERE = Path(__file__).resolve().parent
L = json.loads((HERE / "assets/lines.json").read_text())
DUR = float((HERE / "lines.js").read_text().split("window.DUR = ")[1].split(";")[0])
S = lambda i: L[i]["s"]
E = lambda i: L[i]["e"]
r = lambda x: round(x, 3)


def W(i, word, end=False):
    hit = next(w for w in L[i]["words"] if w["w"].lower().strip(".,?!:'\"").startswith(word.lower()))
    return hit["e"] if end else hit["s"]


cues = {
    "shrink": [1.2, 1.9],                                   # hero render shrinks into the IDE preview
    "whipPipe": r(S(1) - 0.1),                              # whip into the pipeline diagram
    "cards": [r(W(1, "local")), r(W(1, "local") + 0.3), r(W(1, "local") + 0.6)],
    "step1": r(S(2) - 0.05),                                # split: wireframe vs final
    "mol": r(W(2, "h2o")),                                  # both halves switch to the H2O lattice
    "step2": r(S(3) - 0.05),                                # timeline
    "sweep": [r(S(3) + 0.08), r(E(3) - 0.05)],              # playhead travel
    "crack": r(W(3, "crack")), "whoosh": r(W(3, "whoosh")),  # markers the playhead hits on the words
    "step3": r(S(4) - 0.05),                                # terminal
    "typed": r(S(4) + 0.85),                                # command fully typed
    "done": r(W(4, "mp4") - 0.05),                          # render finished
    "reveal": r(W(4, "mp4") + 0.1),                         # final MP4 snaps full screen
    "cta": r(W(4, "comment")),                              # CTA pill pops
    "loop": r(DUR - 0.28),                                   # whip back to the opening frame
}
# Sound cues: [file, time, dB relative to the voice peak]. Clean Foley (sfx-foley rules, v3 model); whoosh/whip cues are
# placed by their loudest point (make_audio.py aligns the file's peak to the cue time).
sfx = [["bts_sub_thud", 0.0, -4], ["foley_ice_crack", 0.02, -6], ["foley_ice_crack", 0.9, -15],          # hook: warm thud + glass ice crack
       ["foley_whoosh", r(cues["whipPipe"] + 0.1), -10]] + [["foley_ui_pop", c, -14] for c in cues["cards"]] + [  # stack cards: matte clicks
       ["foley_whoosh", r(cues["step1"] + 0.1), -10],                                                       # 05.5 transition
       ["sparkle", cues["mol"], -16],
       ["foley_whoosh", r(cues["step2"] + 0.1), -10],                                                       # 09.5 transition
       ["bts_ice_snap", cues["crack"], -7], ["bts_soft_whoosh", cues["whoosh"], -10],                     # on "ice crack" / "whoosh"
       ["foley_whoosh", r(cues["step3"] + 0.1), -11], ["key_typing", r(S(4) + 0.05), -16], ["foley_ui_pop", cues["done"], -14],
       ["bts_sub_thud", cues["reveal"], -9], ["foley_ui_pop", cues["cta"], -12],
       ["bts_air_whip", r(cues["loop"] + 0.12), -10]]                                                     # loop whip, 10 dB under the voice

# timeline panel: a 96-bar envelope of the real Mpemba narration
a, sr = sf.read(HERE.parent / "mpemba-effect/assets/dialogue.wav", always_2d=True)
env = np.abs(a.mean(1)); n = 96; step = len(env) // n
bars = [float(env[i * step:(i + 1) * step].max()) for i in range(n)]
bars = [round(b / max(bars), 2) for b in bars]

out = {"DUR": DUR, "cues": cues, "sfx": sfx, "bars": bars}
(HERE / "direction.json").write_text(json.dumps(out, indent=1))
(HERE / "direction.js").write_text("window.D = " + json.dumps(out) + ";\n")
print("cues", cues)
