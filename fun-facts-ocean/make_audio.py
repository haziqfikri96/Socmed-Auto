"""Builds assets/mix.wav for the ocean video: looped ambience, soft pads, ElevenLabs effects and narration.

Run with the editor-v1 venv python: ~/.cache/editor-v1/venv/bin/python make_audio.py assets/mix.wav
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR, DUR = 48000, 60.0
HERE = Path(__file__).resolve().parent
FX = HERE.parent / "sfx/elevenlabs"
VO = HERE / "assets/vo"
N = int(SR * DUR)
mix = np.zeros((N, 2))


def load(path):
    data, sr = sf.read(path, always_2d=True)
    assert sr == SR, path
    return data


def add(sig, at, gain=1.0):
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    i = int(at * SR)
    j = min(N, i + len(sig))
    if j > i:
        mix[i:j] += sig[: j - i] * gain


def fx(name, at, gain=1.0, length=None):
    data = load(FX / f"{name}.wav")
    if length:
        data = data[: int(length * SR)].copy()
        tail = int(0.05 * SR)
        data[-tail:] *= np.linspace(1, 0, tail)[:, None]
    add(data / max(1e-6, np.abs(data).max()), at, gain)


def tone(freq, length, decay, harm):
    t = np.arange(int(length * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harm))
    return s * np.minimum(t / 0.01, 1) * np.exp(-t * decay)


# ambience: three 22 s clips, cross-faded by 1 s
amb = load(FX / "ocean_ambience.wav")
amb = amb / np.abs(amb).max()
xf = int(1.0 * SR)
for k in range(3):
    seg = amb.copy()
    if k > 0:
        seg[:xf] *= np.linspace(0, 1, xf)[:, None]
    if k < 2:
        seg[-xf:] *= np.linspace(1, 0, xf)[:, None]
    add(seg, k * (len(amb) - xf) / SR, 0.28)

# soft pads and a slow bass pulse
CHORDS = [(220, 261.63, 329.63), (174.61, 220, 261.63), (196, 246.94, 293.66), (220, 261.63, 329.63)]
BASS = [55.0, 43.65, 49.0, 55.0]
for b in range(int(DUR / 2)):
    t = b * 2.0
    for f in CHORDS[b % 4]:
        add(tone(f, 2.6, 0.8, (1.0, 0.2)), t, 0.04)
    if 4.5 <= t < 54.5:
        add(tone(BASS[b % 4], 0.9, 3.0, (1.0, 0.3)), t, 0.16)

# effects
fx("impact_deep", 0.04, 0.75)
fx("riser", 4.5 - 2.48, 0.25)
for c in [4.5, 14.5, 24.5, 34.5, 44.5, 54.5]:
    fx("whoosh_fast", c - 0.3, 0.5)
    fx("whoosh_soft", c, 0.35)
# fact 1
fx("counter", 5.5, 0.3, 2.4)
fx("ding", 8.0, 0.45)
fx("pop", 8.8, 0.45)
# fact 2
fx("counter", 15.5, 0.3, 3.2)
fx("sonar_ping", 18.7, 0.4)
fx("pop", 19.5, 0.45)
# fact 3
fx("counter", 25.5, 0.3, 2.6)
fx("impact_deep", 30.5, 0.6)
fx("pop", 31.5, 0.45)
# fact 4
fx("pop", 35.4, 0.35)
fx("sonar_ping", 37.0, 0.35)
fx("sonar_ping", 39.1, 0.35)
# fact 5
fx("counter", 46.0, 0.3, 2.1)
fx("ding", 48.2, 0.45)
fx("pop", 49.9, 0.4)
# outro
fx("impact_deep", 54.62, 0.7)
fx("ding", 54.9, 0.4)

# narration; everything else ducks under the voice
voice = np.zeros((N, 2))
LINES = [("1_hook", 0.45), ("2_water", 4.8), ("3_depth", 14.8), ("4_trench", 24.8),
         ("5_light", 34.8), ("6_map", 44.8), ("7_cta", 55.0)]
for name, at in LINES:
    data = load(VO / f"{name}.wav")
    i = int(at * SR)
    voice[i:i + len(data)] += data / np.abs(data).max() * 0.9
win = int(0.25 * SR)
cs = np.cumsum(np.pad(np.abs(voice).max(axis=1), (win, 0)))
env = np.roll((cs[win:] - cs[:-win]) / win, -win // 2)
duck = 1 - 0.6 * np.clip(env / 0.08, 0, 1)
mix *= duck[:, None]
mix += voice

fade = int(0.8 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix * 1.1) * 0.9
sf.write(Path(sys.argv[1]), mix, SR, subtype="PCM_16")
