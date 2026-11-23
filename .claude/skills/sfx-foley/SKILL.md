---
name: sfx-foley
description: Rules for generating clean, crisp, realistic Foley sound effects (clicks, pops, whooshes, cracks, impacts) with the ElevenLabs sound-generation API for Shichi.AI videos. Use whenever a video needs a new sound effect, before calling /v1/sound-generation or editing tools/make_sfx_elevenlabs.py.
---

# Clean Foley with ElevenLabs (Shichi.AI)

Goal: dry, punchy, realistic one-shots. No muddy reverb tails, no sci-fi artifacts, no leading silence.

## 1. Generate with the project script, not by hand

Add the effect to the `FOLEY` dict in `tools/make_sfx_elevenlabs.py`, then run:

```bash
python tools/make_sfx_elevenlabs.py sfx/elevenlabs
```

Existing WAVs are skipped (never regenerate an effect that already exists). The script refuses prompts and durations that break the rules below.

## 2. API parameters (`POST https://api.elevenlabs.io/v1/sound-generation`)

| Parameter | Value |
|---|---|
| `model_id` | `"eleven_text_to_sound_v3"` (always) |
| `duration_seconds` | always explicit and short: **0.5–0.8 s** for clicks / pops / impacts, **0.8–1.5 s** for whooshes / cracks |
| `prompt_influence` | `0.7` (literal, clean sound design; the API default 0.3 drifts into texture) |

Header: `xi-api-key: proxy-injected` (the proxy injects the real key).

## 3. Prompt formula

`[physical source + action]` + `[texture / weight]` + `"dry close-mic studio foley, crisp transient, no reverb, one-shot"`

Never a one- or two-word prompt ("whoosh", "ice crack"). Always say what to avoid (no reverb / no metallic resonance / no distortion).

Saved examples (in the kit as `foley_*`):

| Name | Seconds | Prompt |
|---|---|---|
| `foley_ui_pop` | 0.5 | Subtle soft matte button click, clean modern UI tap, dry close-mic foley, no reverb, one-shot |
| `foley_whoosh` | 0.9 | Fast soft air sweep transition, smooth wind movement, clean modern broadcast whoosh, no metallic resonance, one-shot |
| `foley_ice_crack` | 0.8 | Sharp brittle ice cube cracking in a glass, crisp high-frequency crystalline fracture, dry close-mic foley, no reverb, one-shot |
| `foley_sub_impact` | 0.8 | Clean warm low-end cinematic thud, tight punchy sub bass drop, no distortion, one-shot |

## 4. Clean and audition every take (FFmpeg, done by the script)

1. `silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0`: the transient hits at 0.00 s, so a cue placed at time t sounds at t.
2. Two-pass `loudnorm` to **-16 LUFS**, true peak -1 dBTP, linear. Very short transient one-shots (clicks, cracks) can't reach -16 LUFS under a -1 dBTP ceiling; they stop at the ceiling, and the audition notes it.
3. 10 ms fade-out (no click at the cut), 48 kHz stereo WAV.

Audition before mixing:

```bash
python tools/make_sfx_elevenlabs.py sfx/elevenlabs --audition
```

It prints length, leading silence (must be 0.000 s), integrated LUFS and true peak for each Foley WAV. Listen to it too: reject a take with a metallic ring, a reverb tail or a synthetic "laser" character, and change the prompt (new name) rather than overwrite.

## 5. Mixing

- Place Foley about **-10 dB under the voiceover**; the voice always stays dominant.
- Transition whooshes at the loop point sit at least 8 dB under the last spoken words.
- Projects' `make_audio.py` place cues by time from `direction.json`; because the cleaned files start on the transient, no offset is needed.
