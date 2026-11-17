"""Builds assets/mix.wav for the HyperFrames skit: lo-fi bed, UI effects and the two-voice dialogue.

Run after make_dialogue.py, with any Python that has numpy and soundfile: python make_audio.py assets/mix.wav
"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf

SR = 48000
HERE = Path(__file__).resolve().parent
FX = HERE.parent / "sfx/elevenlabs"
LINES = json.loads((HERE / "assets/lines.json").read_text())
dia, _ = sf.read(HERE / "assets/dialogue.wav", always_2d=True)
N = len(dia); DUR = N / SR
mix = np.zeros((N, 2))
L = lambda i: LINES[i]


def load(name):
    d, sr = sf.read(FX / f"{name}.wav", always_2d=True); assert sr == SR
    return d / max(1e-6, np.abs(d).max())


def add(sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if j > i: mix[i:j] += sig[: j - i] * gain


def tone(freq, length, decay, harm):
    t = np.arange(int(length * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    s = s * np.minimum(t / 0.012, 1) * np.exp(-t * decay)
    return np.stack([s, s], axis=1)


# lo-fi bed: soft electric-piano chords, a little bass and a muted kick/hat pattern at 84 bpm
BEAT = 60 / 84
CH = [(261.63, 329.63, 392.0, 493.88), (220.0, 261.63, 329.63, 392.0), (174.61, 220.0, 261.63, 329.63), (196.0, 246.94, 293.66, 349.23)]
b = 0
while b * BEAT * 4 < DUR:
    c = CH[b % 4]; t0 = b * BEAT * 4
    for f in c: add(tone(f, BEAT * 4.2, 0.9, (1.0, 0.35, 0.1)), t0, 0.022)
    add(tone(c[0] / 2, BEAT * 1.8, 1.6, (1.0, 0.25)), t0, 0.06); add(tone(c[0] / 2, BEAT * 1.8, 1.6, (1.0, 0.25)), t0 + BEAT * 2, 0.05)
    for k in range(4):
        kick = tone(55, 0.25, 18, (1.0,)); add(kick, t0 + k * BEAT, 0.12 if k % 2 == 0 else 0.0)
        rng = np.random.default_rng(b * 4 + k); hat = rng.standard_normal((int(0.04 * SR), 2)) * np.exp(-np.arange(int(0.04 * SR)) / SR * 90)[:, None]
        add(hat, t0 + k * BEAT + BEAT / 2, 0.02)
    b += 1

fx = lambda name, at, g: add(load(name), at, g)
fx("pop", 2.9, 0.3)                                   # file chip
for i in range(1, len(LINES)): fx("whoosh_soft", L(i)["s"] - 0.12, 0.07)   # camera moves
fx("impact_deep", L(4)["s"] - 0.3, 0.3)               # shock punch-in
fx("pop", L(5)["s"], 0.35); fx("ding", L(5)["s"] + 3.3, 0.25)            # HTML -> MP4 card
for w in L(7)["words"][:9:2]: fx("pop", w["s"], 0.22)  # feature chips
fx("pop", L(11)["s"], 0.35)
for k in range(30): fx("tick", L(11)["s"] + 0.2 + k * 0.08, 0.09)       # typing the commands
fx("ding", L(11)["s"] + 2.7, 0.3)
fx("pop", L(13)["s"], 0.35)                           # GitHub card
fx("counter", L(14)["e"] - 0.1, 0.15); fx("ding", L(15)["s"] + 0.1, 0.3)   # render done
fx("eruption", L(15)["e"] + 0.15, 0.55)               # volcano video plays
fx("riser", L(19)["s"] - 2.4, 0.15)
fx("pop", L(19)["e"] - 0.3, 0.35)                     # the sleep video appears
fx("snore", L(19)["e"] - 0.1, 0.5)
fx("counter", L(19)["e"] + 0.6, 0.25)                 # views racing up
fx("impact_deep", L(20)["s"], 0.5)                    # "Quill!"
fx("pop", L(21)["s"] + 0.5, 0.35)

# duck the bed under speech, then the dialogue on top
env = np.convolve(np.abs(dia[:, 0]), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
mix *= (1 - 0.5 * np.clip(env / (env.max() * 0.3), 0, 1))[:, None]
mix += dia * 0.95
mix = mix / np.abs(mix).max() * 0.89
sf.write(sys.argv[1], mix, SR, subtype="PCM_16")
print("wrote", sys.argv[1], f"{DUR:.2f}s")
