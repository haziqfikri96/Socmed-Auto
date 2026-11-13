"""Builds assets/mix.wav: a synthesised 120 BPM bed plus the editor-v1 sound kit on the cuts."""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf

SR, DUR = 48000, 19.0
KIT = Path.home() / ".claude/skills/editor-v1/sfx/ev1kit"
N = int(SR * DUR)
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)


def add(sig, at, gain=1.0):
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    i = int(at * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(N, i + len(sig))
    mix[i:j] += sig[: j - i] * gain


def sfx(name, at, gain=1.0):
    data, sr = sf.read(KIT / f"{name}.wav", always_2d=True)
    assert sr == SR
    add(data, at, gain)


def kick():
    t = np.arange(int(0.28 * SR)) / SR
    f = 45 + 95 * np.exp(-t * 32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13)


def hat():
    t = np.arange(int(0.05 * SR)) / SR
    n = rng.standard_normal(len(t))
    return np.diff(n, prepend=0) * np.exp(-t * 90)


def tone(freq, length, decay=3.0, harm=(1.0, 0.35, 0.12)):
    t = np.arange(int(length * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    env = np.minimum(t / 0.01, 1) * np.exp(-t * decay)
    return s * env


BEAT = 0.5
BASS = [55.0, 55.0, 43.65, 49.0]
CHORDS = [(220, 261.63, 329.63), (220, 261.63, 329.63), (174.61, 220, 261.63), (196, 246.94, 293.66)]

for b in range(int(DUR / BEAT)):
    t0 = b * BEAT
    bar = (b // 4) % 4
    full = 3.0 <= t0 < 16.0
    if full:
        add(kick(), t0, 0.85)
        add(hat(), t0 + BEAT / 2, 0.12)
        add(tone(BASS[bar], 0.42, 5.0), t0 + BEAT / 2, 0.30)
    if b % 4 == 0:
        for f in CHORDS[bar]:
            add(tone(f, 2.0, 0.9, (1.0, 0.2)), t0, 0.05 if full else 0.035)

CUTS = [3.0, 7.0, 12.0, 16.0]
sfx("impact_1", 0.06, 0.8)
sfx("click_1", 0.26, 0.6)
sfx("click_2", 0.38, 0.6)
sfx("riser_1", 3.0 - 0.98, 0.5)
for c in CUTS:
    sfx("swish_1", c - 0.2, 0.6)
    sfx("subboom_1", c, 0.55)
sfx("clicktrain_1", 3.6, 0.35)
sfx("click_3", 5.1, 0.6)
sfx("impact_2", 5.8, 0.45)
for i, t in enumerate([9.0, 9.4, 9.8, 10.4]):
    sfx(f"click_{i % 4 + 1}", t, 0.55)
for i, t in enumerate([12.6, 13.1, 13.6, 14.1]):
    sfx(f"click_{i % 4 + 1}", t, 0.6)
sfx("impact_2", 16.12, 0.7)
sfx("outro_1", 17.3, 0.6)

fade = int(0.4 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix * 1.1) * 0.9
sf.write(Path(sys.argv[1]), mix, SR, subtype="PCM_16")
