"""Generate the sound-effects kit with the ElevenLabs sound-generation API into 48 kHz WAVs.

The API key is injected by the environment's network proxy; set ELEVENLABS_API_KEY to use your own.
Existing files are skipped, so re-running only spends credits on new entries.

FOLEY (new effects): clean, crisp, realistic one-shots. Rules (also in .claude/skills/sfx-foley/SKILL.md):
  - model_id "eleven_text_to_sound_v3", prompt_influence 0.7, explicit short duration_seconds:
    0.5–0.8 s for clicks / pops / impacts, 0.8–1.5 s for whooshes / cracks
  - prompt = [physical source + action] + [texture / weight] + "dry close-mic studio foley, crisp transient, no reverb, one-shot"
    (never a one- or two-word prompt; the script refuses prompts that break the rules)
  - every take is cleaned with FFmpeg: leading silence removed (transient at 0.00 s), loudness normalised to -16 LUFS,
    10 ms fade-out; the script prints duration, leading silence, LUFS and peak so each take can be auditioned
  - in a mix, place Foley about -10 dB under the voiceover

usage: python tools/make_sfx_elevenlabs.py sfx/elevenlabs            # generate anything missing
       python tools/make_sfx_elevenlabs.py sfx/elevenlabs --audition  # print stats for every Foley WAV
"""
import json
import os
import re
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
    "tech_pulse": (20.0, "Upbeat minimal tech creator background loop, punchy electronic kick and sub pulse at 118 bpm, bright plucky synth arpeggio, clean modern, no vocals, no melody lead"),
    "scan_sweep": (1.5, "Digital scanner sweep, futuristic laser scan passing left to right, clean sci-fi UI sound, short"),
    "key_typing": (2.0, "Fast mechanical keyboard typing, crisp clicky keys, a burst of quick keystrokes then enter key, close and dry"),
    "ui_click": (0.5, "Crisp modern UI click pop, short clean digital tap, satisfying"),
    "kids_bed": (20.0, "Playful upbeat kids science background music loop, bouncy pizzicato strings and light marimba, cheerful and curious, steady tempo, no vocals, no drums"),
    "science_pulse": (30.0, "Dark minimal science documentary underscore, slow deep sub pulse every second with a cold airy synth pad, mysterious, no melody, no drums, no voices"),
    "sting": (1.2, "Punchy comedic bass hit sting, deep boom with a short dramatic orchestral stab, cartoon reaction, no reverb tail"),
}

# Foley one-shots: v3 model, prompt_influence 0.7, short durations, cleaned + normalised (see docstring)
FOLEY_MODEL, FOLEY_INFLUENCE, FOLEY_LUFS = "eleven_text_to_sound_v3", 0.7, -16
FOLEY = {
    "foley_ui_pop": (0.5, "Subtle soft matte button click, clean modern UI tap, dry close-mic foley, no reverb, one-shot"),
    "foley_whoosh": (0.9, "Fast soft air sweep transition, smooth wind movement, clean modern broadcast whoosh, no metallic resonance, one-shot"),
    "foley_ice_crack": (0.8, "Sharp brittle ice cube cracking in a glass, crisp high-frequency crystalline fracture, dry close-mic foley, no reverb, one-shot"),
    "foley_sub_impact": (0.8, "Clean warm low-end cinematic thud, tight punchy sub bass drop, no distortion, one-shot"),
    # Mpemba BTS short (durations set by the user)
    "bts_sub_thud": (0.7, "Tight warm sub bass thud, soft felt mallet hitting a large padded drum, clean low-end punch, dry close-mic foley, no distortion, no metallic ring, one-shot"),
    "bts_ice_snap": (0.6, "Crisp crystalline ice snap, thin sheet of clear ice breaking cleanly in two, bright brittle transient, dry close-mic foley, no reverb, one-shot"),
    "bts_soft_whoosh": (0.7, "Clean soft air whoosh, a quick gentle gust of wind passing the microphone, smooth and natural, dry foley, no metallic ring, no reverb, one-shot"),
    # Claude skills explainer
    "sk_tactile_pop": (0.5, "Crisp tactile pop, a firm plastic button snapping into place, short bright transient, dry close-mic foley, no reverb, one-shot"),
    "sk_scroll_ticks": (0.7, "Rapid soft scroll-wheel ticks, a mouse wheel spun quickly with tiny clean detents, dry close-mic foley, no reverb, one-shot"),
    "sk_error_thud": (0.5, "Soft muted error thud, a padded low knock like a gentle wrong-answer bump, warm and short, dry close-mic, no reverb, no distortion, one-shot"),
    "sk_mouse_click": (0.5, "Single crisp computer mouse click, clean plastic left-button press, dry close-mic foley, no reverb, one-shot"),
    "sk_chime": (0.6, "Bright clean success chime, two quick rising glass bell notes, light and cheerful, dry, no reverb tail, one-shot"),
    "sk_typing": (1.2, "Fast crisp mechanical keyboard typing burst, quick tactile keystrokes in an even rhythm, dry close-mic foley, no reverb, one-shot"),
    "sk_pops_up": (0.8, "Three quick ascending soft UI pops, small rounded bubbles rising in pitch one after another, clean and subtle, dry close-mic, no reverb, one-shot"),
    # Onion BTS short
    "ob_scan_hum": (2.0, "Subtle soft digital scanner hum, gentle electronic sweep tone with a light warm buzz, clean and smooth, no music, no beeps, no metallic ringing", "ambient"),
    "ob_key_click": (0.5, "Single crisp mechanical keyboard keystroke, one clean tactile key press, dry close-mic foley, no reverb, one-shot"),
    # Onion tears short (kids)
    "ot_veg_slice": (0.6, "Crisp chef knife slicing through a fresh juicy onion on a wooden cutting board, sharp wet crunch, dry close-mic foley, no reverb, one-shot"),
    "ot_gas_burst": (0.7, "Punchy fizzy gas burst, a soda bottle cap popped open with a quick rush of bright carbonated bubbles, clear and loud, dry close-mic foley, no reverb, one-shot"),
    "ot_bubble_pops": (0.8, "Rapid cluster of small cartoon bubble pops, quick bright plip sounds in a fast burst, dry close-mic foley, no reverb, one-shot"),
    "ot_alarm_ding": (0.6, "Subtle cute alarm bell ding, small brass desk bell struck twice quickly, bright and clean, dry close-mic, no reverb, one-shot"),
    "ot_water_splash": (0.8, "Small clean water splash, a few drops of water hitting a glossy surface, bright wet droplets, dry close-mic foley, no reverb, one-shot"),
    "ot_frost_chime": (0.6, "Frosty icy chime, tiny glass bell tapped once with a cold sparkly ring, bright and clean, dry close-mic, no reverb, one-shot"),
    # Pioneer anomaly short
    "pa_sonar_ping": (0.6, "Crisp clean telemetry sonar ping, single bright electronic beep from a spacecraft radio, short tight decay, dry close-mic, no reverb, one-shot"),
    "pa_wave_sweep": (1.2, "Soft smooth wave sweep, gentle warm air pressure swell passing slowly by, clean and natural, no metallic resonance, no reverb, one-shot"),
    "pa_shimmer": (0.8, "Delicate crystalline shimmer, tiny glass chimes brushed once, bright sparkling high frequencies, dry close-mic foley, no reverb, one-shot"),
    "pa_reactor_hum": (3.0, "Warm low steady reactor hum, soft electrical transformer drone with gentle low rumble, smooth and even, no music, no metallic ringing", "ambient"),
    "bts_air_whip": (0.5, "Short clean air whip, thin bamboo stick swished fast through the air, tight natural swish, dry close-mic foley, no metallic tail, no reverb, one-shot"),
}
SHORT = re.compile(r"click|pop|tap|tick|thud|impact|hit|knock|drop", re.I)    # 0.5–0.8 s
MEDIUM = re.compile(r"whoosh|sweep|swish|crack|fracture|snap|swipe", re.I)     # 0.8–1.5 s


def check_foley(name, seconds, prompt, kind="oneshot"):
    """Refuse prompts and durations that produce muddy or sci-fi results."""
    words = len(prompt.replace(",", " ").split())
    if kind == "ambient":     # sustained hums/beds: detailed prompt, explicit 1–6 s, still cleaned and normalised
        assert words >= 8 and 1.0 <= seconds <= 6.0, f"{name}: ambient needs a detailed prompt and 1–6 s"
        return
    assert words >= 8, f"{name}: prompt too short ({words} words); use source+action, texture/weight, foley tail"
    assert "one-shot" in prompt.lower(), f"{name}: prompt must end with the one-shot / no-reverb foley tail"
    assert "reverb" in prompt.lower() or "resonance" in prompt.lower() or "distortion" in prompt.lower(), f"{name}: say what to avoid (no reverb ...)"
    assert 0.5 <= seconds <= 1.5, f"{name}: one-shots are 0.5–1.5 s (API minimum 0.5), got {seconds}"
    # house defaults: 0.5–0.8 s for clicks/pops/impacts, 0.8–1.5 s for whooshes/cracks; a shorter cut asked for on purpose is allowed
    if MEDIUM.search(name + " " + prompt) and seconds < 0.8:
        print(f"note {name}: {seconds} s is shorter than the 0.8–1.5 s default for whooshes/cracks (kept as requested)")
    elif SHORT.search(name + " " + prompt) and not MEDIUM.search(name + " " + prompt) and seconds > 0.8:
        print(f"note {name}: {seconds} s is longer than the 0.5–0.8 s default for clicks/pops/impacts")


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True)


def clean(src, wav):
    """Leading silence off (transient at 0.00 s), -16 LUFS (two-pass, linear), 10 ms fade-out, 48 kHz stereo."""
    trim = "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0"
    m = ff(["-i", str(src), "-af", f"{trim},loudnorm=I={FOLEY_LUFS}:TP=-1:LRA=7:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    norm = (f"loudnorm=I={FOLEY_LUFS}:TP=-1:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
            f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    dur = float(ff(["-i", str(src), "-af", trim, "-f", "null", "-"]).stderr.rsplit("time=", 1)[-1].split()[0].split(":")[-1])
    fade = f"afade=t=out:st={max(0.0, dur - 0.01):.3f}:d=0.01"
    r = ff(["-y", "-i", str(src), "-af", f"{trim},{norm},{fade}", "-ar", "48000", "-ac", "2", str(wav)])
    assert r.returncode == 0, r.stderr[-400:]


def audition(wav):
    """Print what matters before mixing: length, leading silence, loudness, peak."""
    lead = ff(["-i", str(wav), "-af", "silencedetect=n=-50dB:d=0.005", "-f", "null", "-"]).stderr
    st = re.findall(r"silence_start: (-?[\d.]+)", lead); en = re.findall(r"silence_end: ([\d.]+)", lead)
    lead_s = float(en[0]) if st and abs(float(st[0])) < 0.001 and en else 0.0     # only a silence that starts at 0 counts
    m = ff(["-i", str(wav), "-af", "loudnorm=print_format=json,astats=metadata=0", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    dur = ff(["-i", str(wav), "-f", "null", "-"]).stderr.rsplit("time=", 1)[-1].split()[0]
    note = "" if float(j["input_i"]) > FOLEY_LUFS - 1.5 else "  (transient one-shot: the -1 dBTP ceiling caps it below -16 LUFS)"
    print(f"  {wav.name:24} len {dur}  lead {lead_s:.3f}s  {j['input_i']} LUFS  peak {j['input_tp']} dBTP{note}")


if "--audition" in sys.argv:
    for name in FOLEY:
        if (OUT / f"{name}.wav").exists():
            audition(OUT / f"{name}.wav")
    sys.exit(0)

manifest = {}
for name, (seconds, prompt, *kind) in FOLEY.items():
    check_foley(name, seconds, prompt, *(kind or ["oneshot"]))
    wav = OUT / f"{name}.wav"
    manifest[name] = {"seconds": seconds, "prompt": prompt, "model_id": FOLEY_MODEL, "prompt_influence": FOLEY_INFLUENCE, "lufs": FOLEY_LUFS}
    if wav.exists():
        print("skip", name)
        continue
    mp3 = OUT / f"{name}.mp3"
    body = json.dumps({"text": prompt, "duration_seconds": seconds, "prompt_influence": FOLEY_INFLUENCE, "model_id": FOLEY_MODEL})
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
    peak = ff(["-i", str(mp3), "-af", "volumedetect", "-f", "null", "-"]).stderr
    peak = float(peak.split("max_volume: ")[1].split()[0]) if "max_volume: " in peak else -99
    if peak < -30:                    # near-silent take: reject it rather than normalise noise up
        print(f"FAILED {name}: take is near-silent (peak {peak} dB); change the prompt and run again")
        mp3.unlink(); continue
    clean(mp3, wav); mp3.unlink()
    print("ok  ", name); audition(wav)

# legacy kit (made before the Foley rules; existing files are kept, never regenerated)
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
