"""Generate one narration track with word timings using ElevenLabs text-to-speech.

usage: make_voiceover_timed.py <script.txt> <out.wav> <words.json> [voice_id] [speed]
The API key is injected by the environment's network proxy; set ELEVENLABS_API_KEY to use your own.
"""
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

text = " ".join(Path(sys.argv[1]).read_text().split())
out_wav, out_words = Path(sys.argv[2]), Path(sys.argv[3])
voice = sys.argv[4] if len(sys.argv) > 4 else "TX3LPaxmHKxFdv7VOQHJ"  # Liam
speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
key = os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")

body = json.dumps({
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": speed},
})
res = subprocess.run(
    ["curl", "-sS", "-m", "180", "-X", "POST",
     f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
     "-H", f"xi-api-key: {key}", "-H", "Content-Type: application/json", "-d", body],
    capture_output=True, check=True,
).stdout
data = json.loads(res)
if "audio_base64" not in data:
    sys.exit(f"API error: {str(data)[:400]}")

mp3 = out_wav.with_suffix(".mp3")
mp3.write_bytes(base64.b64decode(data["audio_base64"]))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(out_wav)], check=True)
mp3.unlink()

al = data["alignment"]
words, cur, start, end = [], "", None, None
for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
    if ch.isspace():
        if cur:
            words.append({"w": cur, "s": round(start, 3), "e": round(end, 3)})
        cur, start = "", None
    else:
        if start is None:
            start = s
        cur += ch
        end = e
if cur:
    words.append({"w": cur, "s": round(start, 3), "e": round(end, 3)})
out_words.write_text(json.dumps(words) + "\n")
print(len(words), "words,", words[-1]["e"], "s")
