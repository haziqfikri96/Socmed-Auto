"""Builds assets/mix.wav for the HyperFrames explainer: light bed, UI effects and the narration.

Run with any Python that has numpy and soundfile: python make_audio.py assets/mix.wav
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR, DUR = 48000, 45.6
HERE = Path(__file__).resolve().parent
FX = HERE.parent / "sfx/elevenlabs"
N = int(SR * DUR)
mix = np.zeros((N, 2))


def load(path):
    data, sr = sf.read(path, always_2d=True)
    assert sr == SR, path
    return data / max(1e-6, np.abs(data).max())


def add(sig, at, gain=1.0):
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    i = int(at * SR)
    j = min(N, i + len(sig))
    if j > i:
        mix[i:j] += sig[: j - i] * gain


def fx(name, at, gain=1.0):
    add(load(FX / f"{name}.wav"), at, gain)


def tone(freq, length, decay, harm):
    t = np.arange(int(length * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    return s * np.minimum(t / 0.01, 1) * np.exp(-t * decay)


def loop(name, start, end, gain):
    src = load(FX / f"{name}.wav")
    n = int((end - start) * SR)
    sig = np.concatenate([src] * (n // len(src) + 1))[:n].copy()
    env = np.full(n, gain)
    edge = int(0.4 * SR)
    env[:edge] *= np.linspace(0, 1, edge)
    env[-edge:] *= np.linspace(1, 0, edge)
    add(sig * env[:, None], start)


# light, curious bed: plucked arpeggio over soft pads, 112 bpm
BEAT = 60 / 118
CHORDS = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
b = 0
while b * BEAT * 4 < DUR:
    chord = CHORDS[b % 4]
    for f in chord:
        add(tone(f / 2, BEAT * 4.4, 0.7, (1.0, 0.3)), b * BEAT * 4, 0.035)
    for k in range(8):
        add(tone(chord[k % 3] * (2 if k % 4 == 3 else 1), 0.35, 9.0, (1.0, 0.2, 0.08)), b * BEAT * 4 + k * BEAT / 2, 0.05)
    b += 1

# effects on the story beats (times match the narration in assets/words.json)
fx("pop", 0.15, 0.4)                  # host pops in
for at in (0.6, 0.9, 1.2, 1.5, 1.8, 2.1):
    fx("tick", at, 0.18)              # code rain
fx("impact_deep", 5.0, 0.45)          # HyperFrames title
fx("whoosh_fast", 6.3, 0.4)
for k in range(10):
    fx("tick", 9.2 + k * 0.15, 0.15)  # typing HTML
fx("whoosh_soft", 11.0, 0.35)         # frames slide out
fx("ding", 12.45, 0.35)               # MP4
for k, at in enumerate((13.9, 14.15, 14.4, 14.65, 14.9, 15.15)):
    fx("pop", at, 0.25)               # feature tiles
for at in (17.4, 18.6, 19.8, 20.8, 22.0, 23.9, 24.8, 25.6):
    fx("whoosh_fast", at - 0.05, 0.3) # feature cuts
fx("impact_deep", 17.5, 0.3)          # kinetic text slam
fx("counter", 20.9, 0.25)             # chart counting up
fx("pop", 24.85, 0.35); fx("ding", 25.15, 0.3); fx("whoosh_soft", 25.4, 0.3)  # sound effects demo
fx("whoosh_soft", 26.9, 0.35)         # website shrinks to video
fx("pop", 28.6, 0.35)                 # chat bubble
for k in range(14):
    fx("tick", 29.7 + k * 0.13, 0.12) # Claude writing code
for k in range(18):
    fx("tick", 31.9 + k * 0.075, 0.12)  # typing command 1
fx("ding", 33.4, 0.3)
for k in range(16):
    fx("tick", 33.6 + k * 0.08, 0.12)   # typing command 2
fx("ding", 35.0, 0.35)
fx("pop", 35.2, 0.3)                  # "make me a video"
fx("counter", 36.6, 0.2)              # render progress
fx("ding", 37.9, 0.4)                 # video ready
for at in (38.3, 38.8, 39.5):
    fx("pop", at, 0.3)                # free / open source / HeyGen chips
fx("whoosh_fast", 40.9, 0.4)
fx("impact_deep", 42.9, 0.35)         # COMMENT HYPERFRAMES

# narration on top, the bed ducked under it
vo = load(HERE / "assets/vo.wav") * 0.95
duck = np.ones(N)
env = np.abs(vo[:, 0])
win = int(0.25 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
duck[: len(env)] = 1 - 0.45 * np.clip(env / (env.max() * 0.3), 0, 1)
mix *= duck[:, None]
add(vo, 0.0, 1.0)

peak = np.abs(mix).max()
mix = mix / peak * 0.89
sf.write(sys.argv[1], mix, SR, subtype="PCM_16")
print("wrote", sys.argv[1], f"{DUR}s")
