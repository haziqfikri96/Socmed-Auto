# QC brief for Gemini: HyperFrames tutorial Part 1 (v2 draft)

Paste everything below, together with `review.mp4`.

---

You are a strict video QC reviewer for a TikTok short. Watch the attached video (review.mp4, 1080x1920, 30 fps, 29.7 s, with audio) frame by frame and report every problem you find. Judge it against the intent below, not your own taste. Do not praise; list problems with timestamps.

## What this video is
A reply video for the TikTok channel Shichi.AI. People commented "HYPERFRAMES" on an earlier skit, and this is the promised tutorial: how to install HyperFrames (a free, open-source tool by HeyGen that turns HTML into MP4 video) in Claude Code and make a first video. It is a DRAFT render: the 3D scene is intentionally drawn at half resolution (slightly soft); text and UI are full sharpness. Do not report 3D softness.

Characters (low-poly 3D, night balcony with a desk):
- Shichi: the human developer (black hair, black "Shichi.AI" t-shirt). Voice: male. Caption colour for his active word: amber.
- Quill: a white floating robot whose face is a dark rounded screen with cyan eyes. Voice: female. Caption colour for her active word: cyan.

Core idea: the tutorial happens INSIDE Quill's face-screen. Three times, the camera dives into Quill's screen, the screen opens to fill the frame, and the terminal/prompt/preview appear on it. At the end, Quill's face-screen itself shows "part 2 →".

## Script and expected picture (timestamps approximate, ±0.2 s)
- 0.0–4.0  Quill (close-up, camera slowly pushing in): "You asked for the HyperFrames tutorial. Here it is in thirty seconds!" Her screen starts glowing cyan near the end.
- 4.0–5.0  Shichi close-up: "Okay, go."
- 5.0–13.2 DIVE 1. Quill's screen opens to full frame (dark navy terminal). Expected text, appearing in time with speech:
  - "# you need Node 22+" / "# and FFmpeg" (grey comments, word by word)
  - "$ node -v"
  - "$ ffmpeg -version"
  - "$ claude plugin marketplace add heygen-com/hyperframes" (camera pans right following the cursor; the line may be cropped by the frame edge)
  - "$ claude plugin install hyperframes@hyperframes"
  - Quill says: "First, you need Node twenty-two and FFmpeg on your computer. Then open Claude Code and add the HyperFrames marketplace. Now install the plugin."
- 13.2–14.7 Shichi close-up, happy, a "?" icon above his head: "Installed. Now what?"
- 14.7–15.5 Quill, smug shrug: "Just ask me."
- 15.5–19.7 DIVE 2. A prompt box with "> " types this text word by word in sync with Quill's voice: "Using /hyperframes, make a 10-second intro with a fade-in title", then "✻ Working…" below it.
- 19.7–21.7 Shichi, curious: "Can I see it before it renders?"
- 21.7–25.1 DIVE 3. "$ npx hyperframes preview", then a 9:16 preview window where the title "Your Intro" fades in, then "$ npx hyperframes render", then the preview collapses into a cyan file tile labelled "my-video.mp4". Quill: "Yep. Preview it in your browser, then render it to MP4."
- 25.1–26.2 Shichi shocked close-up, red "!" icon: "Wait. That's it?"
- 26.2–29.7 Quill: "That's it. Free and open source. Follow for part two!" On "part two", Quill's face-screen changes to "part 2 →". The video ends ~0.3 s after the last word (it should loop cleanly).

## Rules the video must follow (report every violation)
1. TikTok safe zones: no captions, text or important UI in the top 180 px, the bottom 320 px (y > 1600), or the right 120 px (x > 960). Exception: terminal lines may run off the right edge while the camera follows the cursor.
2. Captions: word by word, bottom area (around y 1430–1530), only the current phrase shown, active word coloured by speaker (amber Shichi, cyan Quill). Check that the caption text matches the spoken words exactly and that the highlighted word matches the word being heard (report any word that lights up >0.15 s early or late).
3. Lip-sync: whoever is speaking has a moving mouth; the listener's mouth stays closed. Faces never freeze while talking.
4. Speaker framing: the camera is on whoever is talking (inside a dive counts as Quill talking). Report any shot showing the wrong character for more than 0.8 s.
5. No page chrome: no watermark or handle in a corner, no "STEP 1"-style labels, no title cards, no progress bars, no end card.
6. Accuracy: the commands on screen must be exactly as listed above (check spelling, spacing, @ and / characters). Nothing should claim output that wasn't shown above.
7. Typing: commands and the prompt may type letter by letter; the grey "#" comment lines should appear whole word by word.
8. Transitions: each dive should feel like the camera entering Quill's screen (the screen rectangle grows to fill the frame), not a fade or a hard swap. Report any flash, black frame, frame where both the 3D scene and the terminal look broken, or jump.
9. Lighting: Shichi's skin should look natural (no green/cyan tint). Quill's screen may glow cyan.
10. Audio: voices always clearly louder than music and sound effects. Expected sounds: a soft riser before the first dive, a short silence, then a low impact when the screen fills; typing ticks while commands type; soft whooshes into dives 2 and 3; a ding when "my-video.mp4" lands; a pop with the "?" and a ding with the "!"; a sparkle on "part two". Report clipping, harsh or too-loud effects, sounds that land >0.1 s off their picture event, and any moment a voice is masked.
11. Pacing: no dead pause longer than 0.15 s between lines; nothing on screen completely static for more than ~1.2 s.
12. Ending: the last frame should flow back into the first (loop) without an obvious jump or an audio click.

## Output format
A table with columns: Timestamp (mm:ss.ff) | Severity (Blocker / Major / Minor) | Category (safe-zone, caption, lip-sync, framing, text accuracy, transition, lighting, audio, pacing, other) | What you see/hear | What it should be.
Then "Top 3 fixes" in priority order, and a one-line verdict: "Ready to post" or "Needs fixes".
If you cannot verify something (e.g. exact audio timing), say so instead of guessing.
