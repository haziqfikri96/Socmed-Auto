"""assets/mix.wav for "Stop Installing Claude Skills Manually": Will's narration on top, an upbeat tech bed ducked
under it, and the UI/Foley cues from direction.json. Loudness-normalised to -14 LUFS / -1 dBTP.

usage: python make_audio.py assets/mix.wav   (after make_dialogue.py and build_direction.py)
"""
import json, shutil, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

SR = 48000
HERE = Path(__file__).resolve().parent
FX = HERE.parent / "sfx/elevenlabs"
D = json.loads((HERE / "direction.json").read_text())
N = int(D["DUR"] * SR)
dia, _ = sf.read(HERE / "assets/dialogue.wav", always_2d=True)
dia = np.pad(dia, ((0, max(0, N - len(dia))), (0, 0)))[:N]
db = lambda g: 10 ** (g / 20)


def load(name):
    d, sr = sf.read(FX / f"{name}.wav", always_2d=True); assert sr == SR, name
    return d / max(1e-6, np.abs(d).max())


def add(buf, sig, at, gain):
    i = int(at * SR); j = min(N, i + len(sig))
    if j > i >= 0: buf[i:j] += sig[: j - i] * gain


# bed: upbeat tech pulse, ducked under the voice
pulse = load("tech_pulse")
bed = np.zeros((N, 2)); pos = 0; xf = int(0.5 * SR)
while pos < N:
    seg = pulse.copy(); seg[:xf] *= np.linspace(0, 1, xf)[:, None]; seg[-xf:] *= np.linspace(1, 0, xf)[:, None]
    add(bed, seg, pos / SR, 1.0); pos += len(pulse) - xf
env = np.convolve(np.abs(dia[:, 0]), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.55 * np.clip(env / (env.max() * 0.3), 0, 1)
fx = np.zeros((N, 2))
VPK = np.abs(dia).max()          # cue gains are dB relative to the voice peak
PEAKED = ("whoosh", "whip")      # these sweep in: their loudest point lands on the cue time
for name, at, g in D["sfx"]:
    s = load(name)
    if any(k in name for k in PEAKED):
        env = np.convolve(np.abs(s).max(1), np.ones(480) / 480, "same"); at -= np.argmax(env) / SR
    add(fx, s, at, db(g) * VPK)
mix = bed * db(-20) * duck[:, None] + fx + dia * 1.0
mix = mix / np.abs(mix).max() * 0.89
fade = int(0.02 * SR); mix[:fade] *= np.linspace(0, 1, fade)[:, None]
f0 = N - int(0.12 * SR); mix[f0:] *= np.linspace(1, 0, N - f0)[:, None]   # loop-safe tail after the last word
sf.write(sys.argv[1], mix, SR, subtype="PCM_16")
if shutil.which("ffmpeg"):
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", sys.argv[1], "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    flt = f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    tmp = sys.argv[1] + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", sys.argv[1], "-af", flt, "-ar", str(SR), "-c:a", "pcm_s16le", tmp], check=True)
    Path(tmp).replace(sys.argv[1])
print("wrote", sys.argv[1], f"{D['DUR']:.2f}s, {len(D['sfx'])} cues")
