"""Builds assets/mix.wav for the auto-gearbox video: soft pulse bed, mechanical effects and the narration.

Run with any Python that has numpy and soundfile: python make_audio.py assets/mix.wav
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR, DUR = 48000, 56.0
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
BEAT = 60 / 112
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
fx("whoosh_fast", 4.9, 0.45)          # into the gearbox
fx("pop", 5.6, 0.35)                  # torque converter appears
loop("machine_whir", 8.3, 21.0, 0.16)  # converter spinning
fx("lock_click", 14.6, 0.5)           # stopped in Drive
fx("hydraulic_hiss", 17.8, 0.45)      # lock-up clutch moves
fx("gear_clunk", 18.3, 0.6)           # locked
fx("whoosh_fast", 21.5, 0.45)         # to the planetary set
for at in (24.6, 25.6, 27.0):
    fx("tick", at, 0.35)              # sun, planets, ring
loop("machine_whir", 22.5, 42.4, 0.12)
fx("lock_click", 28.6, 0.5)           # ring held
fx("gear_clunk", 34.2, 0.6)           # everything locked
fx("lock_click", 38.5, 0.5)           # carrier held
fx("whoosh_soft", 40.3, 0.4)          # spinning backwards
fx("hydraulic_hiss", 43.4, 0.5)       # clutches pushed by oil
fx("gear_clunk", 43.8, 0.5)
fx("hydraulic_hiss", 44.2, 0.3)
fx("ding", 46.4, 0.35)                # computer
fx("counter", 48.0, 0.3)              # 1 -> 10 gears
fx("whoosh_fast", 51.2, 0.45)         # back to the host
fx("pop", 52.4, 0.35)

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
