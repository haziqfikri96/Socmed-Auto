# QC brief for Gemini: HyperFrames tutorial Part 3 (draft)

Paste everything below, together with `review.mp4` from tutorial-part3.

---

You are a strict video QC reviewer for a TikTok short. Watch the attached video (1080x1920, 30 fps, 28.94 s, with audio) frame by frame and report every problem you find. Judge it against the intent below, not your own taste. Do not praise; list problems with timestamps.

## What this video is
Part 3 of a tutorial series on the TikTok channel Shichi.AI, titled "Why your AI video looks like a PowerPoint". It teaches that adding camera motion, spring text physics and sound effects to a HyperFrames prompt turns a flat video into a dynamic one, shown as a BEFORE vs AFTER comparison. It is a DRAFT render: the 3D scene is intentionally drawn at half resolution (slightly soft); text and UI are full sharpness. Do not report 3D softness.

Characters (low-poly 3D, night balcony with a desk):
- Shichi: the human developer (black hair, black "Shichi.AI" t-shirt). Male voice. Caption colour for his active word: amber.
- Quill: a white floating robot whose face is a dark rounded screen with cyan eyes. Female voice. Caption colour for her active word: cyan.

Core idea: the demos happen INSIDE Quill's face-screen. Twice, the camera dives into Quill's screen, the screen opens to fill the frame, and a Claude Code prompt / a before-after preview appears on it.

## Script and expected picture (timestamps ±0.2 s)
- 0.35–4.30  Shichi close-up, disappointed (camera already slowly pushing in): "Part three! I made my first video... why does it look like a PowerPoint?"
- 4.81–7.34  Quill close-up, smug: "Because you didn't ask for motion or sound. Watch." From ≈6.8 s a soft, even cyan glow builds around the edges of her face-screen (no bright spot), with a soft riser in the audio.
- 7.56–12.50 DIVE 1. The glow carries into the dive as the screen opens to fill the frame. Grey line "# in Claude Code" above a prompt box with "> ". Quill: "Tell Claude three things: camera zoom, spring text physics, and sound effects." The prompt appears word by word in sync with her voice:
  "Add camera zoom, spring text physics, and whoosh + impact SFX"
  Cyan highlights: "camera zoom" at ≈9.7 s, "spring text physics" at ≈10.9 s, "SFX" at ≈11.5 s.
  "✻ Working…" appears below the box at ≈11.86 s, then the camera pulls out at ≈12.3–12.5 s.
- 12.60–13.42 Shichi close-up, curious, yellow "?" icon (pop sound): "Just those three?" The "?" must not appear in any Quill shot.
- 13.71–14.12 Quill close-up: "Listen."
- 14.46–20.49 DIVE 2 (before vs after). A 9:16 preview window (dark volcano scene) with a badge in its corner, above a timeline panel with a video track (two clips) and an SFX waveform track, and a cyan playhead that moves left to right the whole time.
  - BEFORE (≈14.7–17.0 s): badge "BEFORE", grey timeline, SFX track dim. Quill: "Before: flat and silent." The title "HOW VOLCANOES ERUPT" just fades in flatly (≈15.2 s). Background music drops away almost completely; there should be about 1 s of near silence after "silent." (intentional).
  - Transition (≈16.9–17.1 s): riser + whoosh; the badge flips to "AFTER", the video track turns blue and the SFX waveform turns cyan.
  - AFTER (≈17.0–20.5 s): low impact sound; the preview window and the volcano scene push in (camera zoom); lava glow pulses and glowing embers arc up from the crater; at ≈18.6 s (on "snappy") the title springs in with an overshoot bounce (pop sound); sparkle at "sound", impact at "hits". Quill: "After: camera push, snappy text, and sound hits."
- 20.57–22.91 Shichi close-up, star eyes, red "!" icon (ding): "Whoa! Same prompt, completely different vibe!" His whole face and mouth must be above the caption area. The "!" must not appear in any Quill shot.
- 23.31–26.55 Quill: "Motion plus sound is everything. Save this for your next video!"
- 26.91–28.57 Quill: "Follow Shichi dot AI for more!" At ≈26.83 s her face-screen changes to "save & try →" (must fit inside the screen bezel), with a sparkle sound.
- 28.69–28.94 Final 0.25 s: "save & try →" crossfades back to Quill's eyes so the video loops into 0.00 s. The video ends at 28.94 s.

## Rules the video must follow (report every violation)
1. TikTok safe zones: no captions, text or important UI in the top 180 px, the bottom 320 px (y > 1600), or the right 120 px (x > 960). The prompt box, preview window and timeline panel must sit inside x 80–940 px.
2. Captions: word by word, bottom area (around y 1430–1530), only the current phrase shown, active word coloured by speaker (amber Shichi, cyan Quill). Caption text must match the spoken words exactly; the highlighted word must match the word being heard (report >0.15 s early or late). A caption must disappear when the speaker stops and never linger into the next shot.
3. Lip-sync: whoever is speaking opens and closes their mouth with the syllables (closed / small / wide); the listener's mouth stays closed. A mouth must not open before the voice starts or keep moving after it stops.
4. Speaker framing: the camera is on whoever is talking (inside a dive counts as Quill talking). Report any shot showing the wrong character for more than 0.8 s.
5. No page chrome: no watermark or handle in a corner, no "STEP 1"-style labels, no title cards, no progress bars, no end card. (The BEFORE/AFTER badge inside the preview window is intentional.)
6. Accuracy: the prompt text must be exactly "Add camera zoom, spring text physics, and whoosh + impact SFX". Highlights must cover exactly those three phrases.
7. Typing: the prompt appears whole word by word in order, never out of order or all at once.
8. Transitions: each dive should feel like the camera entering Quill's screen (the screen rectangle grows to fill the frame), not a fade or a hard swap. Report any flash, black frame, broken frame or jump. The cyan glow before dive 1 must be soft and even (no white hotspot) and must not snap off as the dive starts.
9. Lighting: Shichi's skin should look natural (no green/cyan tint).
10. Audio: voices always clearly louder than music and effects. Expected sounds: soft riser and low impact into dive 1; a short tick on each prompt word; pops on the three highlights; a pop with the "?"; whoosh into dive 2; near-silence during BEFORE; riser + whoosh + impact at the flip to AFTER; pop on the title spring; sparkle and impact during "sound hits"; ding with the "!"; sparkle on "save & try". Report clipping, harsh or too-loud effects, sounds >0.1 s off their picture event, and any moment a voice is masked.
11. Pacing: nothing on screen completely static for more than ~1.2 s (cursors, playhead, embers or camera drift should keep the frame alive).
12. Ending: the last frame should flow back into the first without a visible jump or an audio click.

## Output format
A table with columns: Timestamp (mm:ss.ff) | Severity (Blocker / Major / Minor) | Category (safe-zone, caption, lip-sync, framing, text accuracy, typing, transition, lighting, audio, pacing, other) | What you see/hear | What it should be.
Then "Top 3 fixes" in priority order, and a one-line verdict: "Ready to post" or "Needs fixes".
If you cannot verify something (e.g. exact audio timing), say so instead of guessing.
