---
name: shichi-voice
description: House rules for Shichi.AI voiceovers with ElevenLabs text-to-speech (model eleven_v4, output format, v4 audio tags, caption-safe word timings, voices for Shichi and Quill). Use before voicing any narration or dialogue, or editing tools/make_voiceover_timed.py or a project's make_dialogue.py.
---

# Shichi.AI voiceovers (ElevenLabs TTS)

## Model and voices
- `model_id`: **`eleven_v4`** (default in `tools/make_voiceover_timed.py` and `tools/make_voiceover_elevenlabs.py`; override with `ELEVEN_TTS_MODEL` or the 6th argument). Projects voiced before 23 Nov 2026 used `eleven_multilingual_v2` and keep their cached takes.
- Voices: **Shichi = Will** `bIHbv24MWmeRgasZH58o`; **Quill = Laura** `FGY2WhTYpPnrIDTdsKH5`. Narrator videos use Will.
- Sound effects are a different endpoint and model: `eleven_text_to_sound_v3` on `/v1/sound-generation` (see the `sfx-foley` skill).

## Output quality
- Account is on the **Starter** plan: the best format it allows is **`mp3_44100_128`** (requested by the tools, then decoded to 48 kHz stereo WAV for mixing). Checked against the API on 23 Nov 2026: `mp3_44100_192` returns 403 (Creator and up), `pcm_44100` returns 403 (Pro and up).
- If the plan is upgraded, change `output_format` in `tools/make_voiceover_timed.py` (Creator: `mp3_44100_192`; Pro: `pcm_44100`). TikTok re-encodes audio to about 128 kbps AAC, so the audible gain is small.

## Eleven v4 audio tags (delivery)
- Inline tags steer delivery and are not spoken: `[excited]`, `[curious]`, `[confident]`, `[fast-paced]` (others work too).
- Use them **sparingly**: at most one per line, at the start of a sentence, where the energy really changes (hook line, reveal, call to action). Never in the middle of a word or a name.
- Captions stay 1:1 with speech: the API returns the tag characters in the alignment, and `make_voiceover_timed.py` drops everything between `[` and `]` from `words.json`. `make_dialogue.py` (template: `mpemba-bts/`) also stores the line's `text` without tags. Never build captions from raw script text.
- A tag is part of the line's cache key: adding or changing a tag re-voices that line (spends credits), so decide tags before voicing.

## Pacing
- Keep zero dead air: `make_dialogue.py` trims each take 0.05 s after the voice stops and can speed takes with `TEMPO` (ffmpeg `atempo`, pitch kept). v4 reads a little slower than v2 at the same settings; prefer `[fast-paced]` or a small `TEMPO` over cutting words.
- Check word timings after voicing (`assets/lines.json`) before building captions and sound cues.
