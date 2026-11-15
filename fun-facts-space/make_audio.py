"""Builds assets/mix.wav: a synthesised 120 BPM bed plus the ElevenLabs sound kit in sfx/elevenlabs."""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf

SR, DUR = 48000, 23.0
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


FX = Path(__file__).resolve().parents[1] / "sfx/elevenlabs"


def fx(name, at, gain=1.0, length=None):
    data, sr = sf.read(FX / f"{name}.wav", always_2d=True)
    assert sr == SR
    if length:
        data = data[: int(length * SR)].copy()
        tail = int(0.05 * SR)
        data[-tail:] *= np.linspace(1, 0, tail)[:, None]
    add(data / max(1e-6, np.abs(data).max()), at, gain)


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
    full = 3.0 <= t0 < 20.5
    if full:
        add(kick(), t0, 0.6)
        add(hat(), t0 + BEAT / 2, 0.12)
        add(tone(BASS[bar], 0.42, 5.0), t0 + BEAT / 2, 0.30)
    if b % 4 == 0:
        for f in CHORDS[bar]:
            add(tone(f, 2.0, 0.9, (1.0, 0.2)), t0, 0.05 if full else 0.035)

fx("space_ambience", 0.0, 0.22)
fx("space_ambience", 22.0, 0.22, 1.0)
fx("impact_deep", 0.04, 0.75)
fx("riser", 3.0 - 2.48, 0.25)
for c in [3.0, 9.5, 15.0, 20.5]:
    fx("whoosh_fast", c - 0.3, 0.5)
    fx("whoosh_soft", c, 0.35)
fx("pop", 4.6, 0.45)
fx("pop", 7.0, 0.45)
fx("counter", 10.4, 0.3, 3.5)
fx("ding", 13.9, 0.5)
fx("counter", 15.9, 0.3, 2.1)
fx("impact_deep", 18.0, 0.6)
fx("impact_deep", 20.62, 0.7)
fx("ding", 20.9, 0.4)

# narration: everything else ducks under the voice
VO = Path(__file__).resolve().parent / "assets/vo"
voice = np.zeros((N, 2))
for name, at in [("1_hook", 0.45), ("2_venus", 3.25), ("3_sun", 9.7), ("4_jupiter", 15.2), ("5_cta", 21.0)]:
    data, sr = sf.read(VO / f"{name}.wav", always_2d=True)
    assert sr == SR
    i = int(at * SR)
    voice[i:i + len(data)] += data / np.abs(data).max() * 0.9
win = int(0.25 * SR)
env = np.convolve(np.abs(voice).max(axis=1), np.ones(win) / win, mode="same")
duck = 1 - 0.6 * np.clip(env / 0.08, 0, 1)
mix *= duck[:, None]
mix += voice

fade = int(0.4 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix * 1.1) * 0.9
sf.write(Path(sys.argv[1]), mix, SR, subtype="PCM_16")
