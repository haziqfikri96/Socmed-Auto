"""Generate the sound-effects kit with the ElevenLabs sound-generation API into 48 kHz WAVs.

The API key is injected by the environment's network proxy; set ELEVENLABS_API_KEY to use your own.
Existing files are skipped, so re-running only spends credits on new entries.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
KEY = os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")
# name -> (seconds, prompt)
KIT = {
    "whoosh_soft": (0.8, "Short soft cinematic whoosh, air swish passing left to right, clean, no reverb tail"),
    "whoosh_fast": (0.6, "Very fast sharp whoosh transition swipe, tight and clean"),
    "impact_deep": (2.0, "Deep cinematic sub bass impact hit, punchy, short dark tail"),
    "pop": (0.5, "Single clean soft UI bubble pop, short and round"),
    "tick": (0.5, "Single soft digital UI click tick, very short"),
    "riser": (2.5, "Cinematic tension riser, synth sweep rising in pitch and volume, stops abruptly at the peak"),
    "ding": (1.5, "Single bright positive bell chime ding, clean with a short ring"),
    "counter": (3.5, "Fast digital counter rolling up, rapid soft ticking that speeds up slightly, clean, no music"),
    "space_ambience": (22.0, "Calm deep space ambient drone, dark low hum with a subtle airy shimmer, no melody, no drums"),
    "ocean_ambience": (22.0, "Deep underwater ambience, muffled low ocean rumble with slow gentle swells and faint distant bubbles, no melody, no drums, no voices"),
    "sonar_ping": (1.5, "Single clean submarine sonar ping with a soft echo tail"),
}

manifest = {}
for name, (seconds, prompt) in KIT.items():
    wav = OUT / f"{name}.wav"
    manifest[name] = {"seconds": seconds, "prompt": prompt}
    if wav.exists():
        print("skip", name)
        continue
    mp3 = OUT / f"{name}.mp3"
    body = json.dumps({"text": prompt, "duration_seconds": seconds, "prompt_influence": 0.5})
    code = subprocess.run(
        ["curl", "-sS", "-m", "180", "-X", "POST", "https://api.elevenlabs.io/v1/sound-generation",
         "-H", f"xi-api-key: {KEY}", "-H", "Content-Type: application/json", "-d", body,
         "-o", str(mp3), "-w", "%{http_code}"],
        capture_output=True, text=True,
    ).stdout.strip()
    if code != "200":
        print("FAILED", name, code, mp3.read_bytes()[:300] if mp3.exists() else "")
        mp3.unlink(missing_ok=True)
        continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(wav)], check=True)
    mp3.unlink()
    print("ok  ", name)

(OUT / "kit.json").write_text(json.dumps(manifest, indent=2) + "\n")
