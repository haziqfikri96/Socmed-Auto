"""Builds assets/mix.wav for the Earth-hole video: tense pads, falling wind, effects and the narration.

Run with the editor-v1 venv python: ~/.cache/editor-v1/venv/bin/python make_audio.py assets/mix.wav
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR, DUR = 48000, 37.5
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


def wind(start, end, g0, g1):
    """Looped falling wind from start to end with the gain ramping g0 -> g1."""
    src = load(FX / "falling_wind.wav")
    n = int((end - start) * SR)
    sig = np.concatenate([src] * (n // len(src) + 1))[:n].copy()
    env = np.linspace(g0, g1, n)
    edge = int(0.3 * SR)
    env[:edge] *= np.linspace(0, 1, edge)
    env[-edge:] *= np.linspace(1, 0, edge)
    add(sig * env[:, None], start)


# pads and a pulse that speeds up during the falls
CHORDS = [(110, 130.81, 164.81), (98, 123.47, 146.83), (87.31, 110, 130.81), (98, 123.47, 146.83)]
for b in range(int(DUR / 2) + 1):
    for f in CHORDS[b % 4]:
        add(tone(f, 2.6, 0.8, (1.0, 0.25)), b * 2.0, 0.05)
t = 3.7
while t < 13.6:
    add(tone(55.0, 0.3, 9.0, (1.0, 0.4)), t, 0.22)
    t += 0.6 - 0.35 * (t - 3.7) / 9.9
t = 19.8
while t < 25.0:
    add(tone(55.0, 0.3, 9.0, (1.0, 0.4)), t, 0.22)
    t += 0.25 + 0.35 * (t - 19.8) / 5.2

fx("impact_deep", 0.02, 0.6)
fx("whoosh_fast", 1.2, 0.5)       # planet sliced open
fx("pop", 2.3, 0.4)               # jumper appears
fx("whoosh_soft", 3.6, 0.5)       # the jump
wind(3.7, 13.6, 0.08, 0.5)
fx("riser", 13.6 - 2.48, 0.3)
fx("impact_deep", 13.6, 0.7)      # slow motion at the centre
wind(13.6, 19.8, 0.1, 0.1)
fx("ding", 18.5, 0.4)             # weightless
fx("whoosh_fast", 19.7, 0.5)
wind(19.8, 25.0, 0.5, 0.08)
fx("pop", 25.0, 0.6)              # pops out the far side
fx("ding", 26.7, 0.5)             # 38 minutes
fx("whoosh_soft", 28.9, 0.5)
wind(28.9, 33.2, 0.1, 0.4)
fx("impact_deep", 33.2, 0.75)     # the hot core

voice = np.zeros((N, 2))
vo = load(HERE / "assets/vo.wav") * 0.9
voice[: len(vo)] += vo[:N]
win = int(0.25 * SR)
cs = np.cumsum(np.pad(np.abs(voice).max(axis=1), (win, 0)))
env = np.roll((cs[win:] - cs[:-win]) / win, -win // 2)
mix *= (1 - 0.6 * np.clip(env / 0.08, 0, 1))[:, None]
mix += voice

fade = int(0.8 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix * 1.1) * 0.9
sf.write(Path(sys.argv[1]), mix, SR, subtype="PCM_16")
