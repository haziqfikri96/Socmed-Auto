# QC brief for Gemini: HyperFrames tutorial Part 2 (draft)

Paste everything below, together with `review.mp4` from tutorial-part2.

---

You are a strict video QC reviewer for a TikTok short. Watch the attached video (1080x1920, 30 fps, 33.65 s, with audio) frame by frame and report every problem you find. Judge it against the intent below, not your own taste. Do not praise; list problems with timestamps.

## What this video is
Part 2 of a tutorial series on the TikTok channel Shichi.AI. Part 1 showed how to install HyperFrames (a free, open-source tool by HeyGen that turns HTML into MP4 video) in Claude Code. Part 2 shows how to make your first real video: start a project, describe the video to Claude, preview and edit it, and render it. It is a DRAFT render: the 3D scene is intentionally drawn at half resolution (slightly soft); text and UI are full sharpness. Do not report 3D softness.

Characters (low-poly 3D, night balcony with a desk):
- Shichi: the human developer (black hair, black "Shichi.AI" t-shirt). Male voice. Caption colour for his active word: amber.
- Quill: a white floating robot whose face is a dark rounded screen with cyan eyes. Female voice. Caption colour for her active word: cyan.

Core idea: the steps happen INSIDE Quill's face-screen. Four times, the camera dives into Quill's screen, the screen opens to fill the frame, and a terminal / Claude Code prompt / preview appears on it. At the end, Quill's face-screen itself shows "your turn →".

## Script and expected picture (timestamps ±0.2 s)
- 0.25–2.70  Shichi (camera already slowly pushing in): "Part two! I installed HyperFrames. Now what?"
- 3.06–6.07  Quill close-up: "Now we make a real video. Step one: start a project." Her screen starts glowing cyan near the end.
- 6.12–8.61  DIVE 1. Quill: "Type npx hyperframes init, then a name." Screen text, typed:
  - "$ npx hyperframes init my-video" (≈6.4–7.8 s)
  - "$ cd my-video" (≈7.9–8.15 s)
  - then the terminal holds completely still until the camera pulls out (≈8.2–8.4 s).
- 8.64–9.70  Shichi close-up, "?" icon: "Then I write code?"
- 10.01–10.33 Quill, smug: "Nope."
- 10.33–15.95 DIVE 2. Grey line "# in Claude Code" above a prompt box with "> ". The prompt types in during "Just describe it. Topic, length, style.":
  "Using /hyperframes, make a 20-second vertical video about how volcanoes erupt. Bold text, dark theme."
  Quill: "Be specific. Vertical for TikTok, and say how long." The word "vertical" gets a cyan highlight at ≈13.9 s (when she says "Vertical") and "20-second" at ≈15.4 s (when she says "long").
- 15.97–17.18 Shichi close-up, worried, sweat drop: "And if I hate the colours?"
- 17.39–22.23 DIVE 3. "$ npx hyperframes preview" types (≈17.55–18.3 s). At ≈18.4 s a 9:16 preview ("HOW VOLCANOES ERUPT" over a dark volcano picture) and a timeline panel below it (three tracks of clips with a moving cyan playhead) slide in. Quill: "Open the preview. You can edit anything on the timeline, or just tell me: make it orange." At ≈21.56 s (on "orange") the preview background and the timeline clips turn orange.
- 22.25–23.68 Shichi, arms crossed, unimpressed: "Rendering takes forever though."
- 23.95–27.17 DIVE 4. Quill: "Render a draft while you tweak. High quality only for the final." Screen text, typed, with a hanging indent on the second line of each command:
  - "$ npx hyperframes render" / "--quality draft" (≈24.3–25.4 s)
  - "$ npx hyperframes render" / "--quality high" (≈25.5–26.5 s)
  - then the terminal holds completely still until the pull-back (≈26.6–27.0 s).
- 27.19–28.49 Shichi, star eyes, sparkle icon: "Wait... that's my first video?" A 9:16 mini video ("HOW VOLCANOES ERUPT", erupting volcano with a pulsing lava glow) plays above his head.
- 28.83–30.56 Quill: "Made on your own computer. Free."
- 30.80–33.25 Quill: "Comment what you made, I'll react to the best ones!" At ≈30.8 s her face-screen changes to "your turn →". The video ends at 33.65 s.

## Rules the video must follow (report every violation)
1. TikTok safe zones: no captions, text or important UI in the top 180 px, the bottom 320 px (y > 1600), or the right 120 px (x > 960). All terminal lines, the prompt box and the preview/timeline must sit inside x 80–940 px.
2. Captions: word by word, bottom area (around y 1430–1530), only the current phrase shown, active word coloured by speaker (amber Shichi, cyan Quill). Caption text must match the spoken words exactly; the highlighted word must match the word being heard (report >0.15 s early or late). A caption must disappear when the speaker stops, not linger into the next shot.
3. Lip-sync: whoever is speaking opens and closes their mouth with the syllables (closed / small / wide); the listener's mouth stays closed. Mouths close when the voice stops.
4. Speaker framing: the camera is on whoever is talking (inside a dive counts as Quill talking). Report any shot showing the wrong character for more than 0.8 s.
5. No page chrome: no watermark or handle in a corner, no "STEP 1"-style labels, no title cards, no progress bars, no end card.
6. Accuracy: on-screen commands must be exactly: "npx hyperframes init my-video", "cd my-video", "npx hyperframes preview", "npx hyperframes render --quality draft", "npx hyperframes render --quality high". Check spelling, spaces and double hyphens. The prompt text must match exactly.
7. Typing: commands and the prompt may type letter by letter, always left to right and in order (a line must never appear all at once or out of order). Nothing typed should be cut off before the camera pulls out.
8. Transitions: each dive should feel like the camera entering Quill's screen (the screen rectangle grows to fill the frame), not a fade or a hard swap. Report any flash, black frame, frame where both the 3D scene and the terminal look broken, or jump.
9. Lighting: Shichi's skin should look natural (no green/cyan tint). Quill's screen may glow cyan.
10. Audio: voices always clearly louder than music and effects. Expected sounds: a soft riser before the first dive, a short silence, then a low impact as the screen fills; typing ticks while commands type; soft whooshes into dives 2–4; small pops when "vertical" and "20-second" highlight and when the preview opens; a ding on "orange"; a pop with the "?", a gulp with the sweat drop, a sparkle with the star eyes and on "your turn". Report clipping, harsh or too-loud effects, sounds >0.1 s off their picture event, and any moment a voice is masked.
11. Pacing: no dead pause longer than 0.15 s between lines; nothing on screen completely static for more than ~1.2 s, except the two intentional still holds at the end of dives 1 and 4.

## Output format
A table with columns: Timestamp (mm:ss.ff) | Severity (Blocker / Major / Minor) | Category (safe-zone, caption, lip-sync, framing, text accuracy, typing, transition, lighting, audio, pacing, other) | What you see/hear | What it should be.
Then "Top 3 fixes" in priority order, and a one-line verdict: "Ready to post" or "Needs fixes".
If you cannot verify something (e.g. exact audio timing), say so instead of guessing.
