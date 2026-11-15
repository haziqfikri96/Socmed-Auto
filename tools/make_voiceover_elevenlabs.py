"""Generate voiceover lines with ElevenLabs text-to-speech.

usage: make_voiceover_elevenlabs.py <lines.json> <out_dir> [voice_id]
lines.json is {"name": "text", ...}; existing files are skipped so re-runs only spend credits on new lines.
The API key is injected by the environment's network proxy; set ELEVENLABS_API_KEY to use your own.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

LINES = json.loads(Path(sys.argv[1]).read_text())
OUT = Path(sys.argv[2])
VOICE = sys.argv[3] if len(sys.argv) > 3 else "nPczCjzI2devNBz1zQrb"  # Brian
KEY = os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")

for name, text in LINES.items():
    wav = OUT / f"{name}.wav"
    if wav.exists():
        print("skip", name)
        continue
    mp3 = OUT / f"{name}.mp3"
    body = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True},
    })
    code = subprocess.run(
        ["curl", "-sS", "-m", "120", "-X", "POST",
         f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
         "-H", f"xi-api-key: {KEY}", "-H", "Content-Type: application/json", "-d", body,
         "-o", str(mp3), "-w", "%{http_code}"],
        capture_output=True, text=True,
    ).stdout.strip()
    if code != "200":
        print("FAILED", name, code, mp3.read_bytes()[:300] if mp3.exists() else "")
        mp3.unlink(missing_ok=True)
        continue
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
         "-ar", "48000", "-ac", "2", str(wav)],
        check=True,
    )
    mp3.unlink()
    print("ok  ", name)
