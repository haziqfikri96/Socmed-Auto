# NOTE: HyperFrames tutorial (Part 1), v2

## The one idea
The tutorial happens **inside Quill's face**. Quill's face is a screen, so the camera dives through it three times, and the terminal, the Claude Code prompt and the preview all live on Quill's own screen. At the end, the same screen says `part 2 →`. Cover-the-logo test: no other channel's character has a face that is the product UI.

## Skills used
- hyperframes, hyperframes-cli, hyperframes-core: the composition contract, lint / validate / inspect / snapshot, draft render.
- motionmaxxing: the idea, the never-ship list, the craft laws, and G0–G5 (`look.py`, `lint.mjs`).
- video-shotcraft: one hero action arc (the first dive), holds after a landing, the riser → silence → impact sound phrase.
- threejs-lighting: Quill's screen as a short-range cyan point light that swells before the dive and lights Quill only.
- Not used, with the reason: remotion and OpenMontage (different engine and pipeline); Blender MCP (a Cycles insert would break the one low-poly world); dream-loop, anatomy and 3dviz-pro-max (different genres).

## Beats and what each buys
| t | beat | buys: the viewer… |
|---|---|---|
| 0–4.0 | Quill hook, the screen starts to glow | believes it really is 30 s |
| 4.0–5.0 | Shichi "Okay, go." | has someone to follow along with |
| 5.0–13.2 | **dive 1**: requirements, then two install commands typed in time with speech | sees the exact commands (hero beat) |
| 13.2–14.7 | Shichi "Installed. Now what?" | feels the "now what?" |
| 14.7–19.7 | dive 2: the prompt types word by word as Quill says it | learns that using it means just asking |
| 19.7–21.7 | Shichi's question | wonders whether he can check first |
| 21.7–25.1 | dive 3: preview → the title fades in → render → the preview collapses into `my-video.mp4` | sees the whole loop end in a file |
| 25.1–26.2 | Shichi "Wait. That's it?" | shares the surprise |
| 26.2–29.7 | Quill; his screen turns into `part 2 →` | knows there's a part 2 |

## Real vs illustrative
- Real: all commands and requirements, checked against the official HyperFrames README (the two `claude plugin` commands, Node.js 22+, FFmpeg, `npx hyperframes preview` / `render`, prompting with `/hyperframes`).
- No invented command output is shown. "✻ Working…" is the style of Claude Code's working indicator, not a captured screen. The preview is a stand-in for what the spoken prompt asks for (a fade-in title).
- The characters and the balcony are our own low-poly models; nothing is generated.

## Gates (quoted from the scripts, draft render `review.mp4`)
- G0 render exists: **PASS**, 29.73 s, matches the expected 29.70 s; audio stream present.
- G2 no empty frame: **PASS**, no run of more than 3 flat frames.
- G3 end hold / CTA share: **PASS**, end hold 0.00 s (it ends in motion, on purpose), final shot 1.60 s = 5 % of the film.
- G5 no page chrome: **PASS** (`lint.mjs`). The first run failed D1/T1 on the terminal; the comment lines were changed to arrive whole word by word, and the screen is marked `data-ui="terminal"` (letter typing stays only in the commands and the prompt, which are product input).
- G1 proof readable and G4 one hero per frame: judged by eye on the sheet. Terminal text is 64 px (0.033 H, but magnified and cropped by the frame edge, with the camera following the caret); one hero per frame.
- Audio: integrated -14.5 LUFS, true peak -1.4 dBFS (loudnorm to -14 added to `make_audio.py`).

## What I'd still improve
- Mean motion is 3.2/255, below the human band (4.4–9.8). The terminal beats are calm by design (a slow push and the caret), but a stronger move while typing would lift it.
- Only 6 of 13 cuts land within ±80 ms of a sound onset; several cuts are 90–110 ms before the next word. Nudging the cuts 3 frames later would tighten the sync.
- The 9:16 preview could show more of a real composition than a single fading title.
