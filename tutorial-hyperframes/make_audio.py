"""Builds assets/mix.wav for the HyperFrames skit: lo-fi bed, every sound cue from direction.json, and the dialogue.

Run after make_dialogue.py and build_direction.py, with any Python that has numpy and soundfile:
    python make_audio.py assets/mix.wav
"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf

SR = 48000
HERE = Path(__file__).resolve().parent
FX = HERE.parent / "sfx/elevenlabs"
D = json.loads((HERE / "direction.json").read_text())
dia, _ = sf.read(HERE / "assets/dialogue.wav", always_2d=True)
N = int(D["DUR"] * SR)
dia = np.pad(dia, ((0, max(0, N - len(dia))), (0, 0)))[:N]
bed = np.zeros((N, 2))
fxm = np.zeros((N, 2))
db = lambda g: 10 ** (g / 20)


def load(name):
    d, sr = sf.read(FX / f"{name}.wav", always_2d=True); assert sr == SR, name
    return d / max(1e-6, np.abs(d).max())


def add(buf, sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if j > i >= 0: buf[i:j] += sig[: j - i] * gain


def tone(freq, length, decay, harm):
    t = np.arange(int(length * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    s = s * np.minimum(t / 0.012, 1) * np.exp(-t * decay)
    return np.stack([s, s], axis=1)


def lowpass(sig, cutoff):
    """One-pole low-pass, so a sound sits behind the music."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    out = np.zeros_like(sig); acc = np.zeros(sig.shape[1])
    for n in range(len(sig)):
        acc = (1 - a) * sig[n] + a * acc; out[n] = acc
    return out


# lo-fi bed: soft electric-piano chords, bass and a muted kick/hat at 84 bpm
BEAT = 60 / 84
CH = [(261.63, 329.63, 392.0, 493.88), (220.0, 261.63, 329.63, 392.0), (174.61, 220.0, 261.63, 329.63), (196.0, 246.94, 293.66, 349.23)]
b = 0
while b * BEAT * 4 < D["DUR"]:
    c = CH[b % 4]; t0 = b * BEAT * 4
    for f in c: add(bed, tone(f, BEAT * 4.2, 0.9, (1.0, 0.35, 0.1)), t0, 0.022)
    add(bed, tone(c[0] / 2, BEAT * 1.8, 1.6, (1.0, 0.25)), t0, 0.06); add(bed, tone(c[0] / 2, BEAT * 1.8, 1.6, (1.0, 0.25)), t0 + BEAT * 2, 0.05)
    for k in range(4):
        if k % 2 == 0: add(bed, tone(55, 0.25, 18, (1.0,)), t0 + k * BEAT, 0.12)
        rng = np.random.default_rng(b * 4 + k); n = int(0.04 * SR)
        add(bed, rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / SR * 90)[:, None], t0 + k * BEAT + BEAT / 2, 0.02)
    b += 1

# every cue from the direction (emote SFX are synced to the emote pop-ins there)
for name, at, g in D["sfx"]:
    add(fxm, load(name), at, db(g))
# soft tension riser that stops dead, then silence until "It's you."
r_end = None
if D.get("riser"):
    riser = load("riser"); r_end = D["riser"][0]
    add(fxm, lowpass(riser, 2500), r_end - len(riser) / SR, db(-8 - 14))   # soft swell, well under the dialogue
# snore: 6 dB down and low-passed so it sits inside the lo-fi bed
if D.get("snore"):
    add(fxm, lowpass(load("snore"), 1400), D["snore"][0], db(-6) * 0.5)

# the bed ducks under speech, and drops to dead silence for the punchline beat
env = np.convolve(np.abs(dia[:, 0]), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.5 * np.clip(env / (env.max() * 0.3), 0, 1)
if r_end is not None:
    i0, i1 = int(r_end * SR), int((r_end + 0.15) * SR)
    duck[i0:i1] = 0; fxm[i0:i1] = 0
    ramp = int(0.25 * SR); duck[i1:i1 + ramp] *= np.linspace(0, 1, ramp)
mix = bed * duck[:, None] + fxm + dia * 0.95
mix = mix / np.abs(mix).max() * 0.89
fade = int(0.02 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]   # click-free loop point
sf.write(sys.argv[1], mix, SR, subtype="PCM_16")
# deliver at -14 LUFS / -1 dBTP (TikTok's loudness target), two-pass ffmpeg loudnorm
import subprocess, re as _re, shutil
if shutil.which("ffmpeg"):
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", sys.argv[1], "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    flt = f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    tmp = sys.argv[1] + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", sys.argv[1], "-af", flt, "-ar", str(SR), "-c:a", "pcm_s16le", tmp], check=True)
    Path(tmp).replace(sys.argv[1])
print("wrote", sys.argv[1], f"{D['DUR']:.2f}s, {len(D['sfx'])} cues")
