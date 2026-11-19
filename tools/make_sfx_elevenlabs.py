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
    "falling_wind": (10.0, "Strong wind rushing past the ears while falling very fast through a tunnel, steady whooshing air, no music, no voices"),
    "gear_clunk": (1.0, "Single heavy mechanical gear engaging clunk, metal gears locking into place, tight and close, no reverb"),
    "hydraulic_hiss": (1.2, "Short hydraulic pressure hiss and soft piston push, clean mechanical, no music"),
    "machine_whir": (6.0, "Smooth steady spinning machine whir, gears and fluid turning inside a metal housing, even tone, no music, no voices"),
    "lock_click": (0.6, "Crisp metallic latch lock click, short and solid"),
    "eruption": (3.0, "Cartoon volcano eruption, deep rumble building into a big lava burst whoosh, fun and punchy, no music"),
    "snore": (3.0, "Gentle cartoon snoring, two slow soft snores with a little whistle, comedic, no music"),
    "sparkle": (1.0, "Bright magical sparkle chime, short twinkling anime shine sound, clean, no music"),
    "gulp": (0.8, "Cartoon nervous gulp swallow with a tiny water-drop plink, anime sweat drop sound effect"),
    "ice_crackle": (2.0, "Crisp ice crystals crackling and spreading across a glass surface, close macro frost forming, sharp tiny cracks, no music"),
    "steam_hiss": (3.0, "Soft continuous hot steam hiss rising from boiling water, gentle airy, no bubbling, no music"),
    "fluid_swirl": (4.0, "Deep slow underwater fluid swirl whoosh, liquid churning in a closed glass vessel, smooth low rumble, no music"),
    "ice_lock": (2.0, "Rapid sequence of tiny crystalline ice clicks locking into place like dominoes, glassy and bright, no music"),
    "ice_thud": (1.2, "Solid block of ice dropped onto a metal shelf, heavy dull thud with a short icy crack, no reverb"),
    "timer_tick": (3.0, "Fast mechanical stopwatch ticking, crisp clock ticks speeding up slightly, close and dry, no music"),
    "science_pulse": (30.0, "Dark minimal science documentary underscore, slow deep sub pulse every second with a cold airy synth pad, mysterious, no melody, no drums, no voices"),
    "sting": (1.2, "Punchy comedic bass hit sting, deep boom with a short dramatic orchestral stab, cartoon reaction, no reverb tail"),
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
