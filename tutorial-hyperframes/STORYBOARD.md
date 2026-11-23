# HyperFrames tutorial (Part 1), v2: storyboard

Skills applied: hyperframes, hyperframes-cli, hyperframes-core (contract and gates), motionmaxxing (idea, never-ship list, craft laws, G0–G5),
video-shotcraft (camera language: one hero action arc, hold after a landing, riser → impact → sparkle sound phrase), threejs-lighting (the screen as a light source).
Not used, with the reason: remotion skills and OpenMontage (a different render engine and an AI-footage pipeline; this film is HyperFrames code);
Blender MCP (the world is the low-poly Three.js balcony, and a Cycles insert would break "one world"); dream-loop, anatomy, 3dviz-pro-max (different genres).

## PAGE
- **Problem:** people commented HYPERFRAMES on the skit and want to know how to start.
- **Audience:** Claude Code users on TikTok, sound often off.
- **Goal:** they can install it and make their first video after one viewing.
- **Emotion:** "that's it?", with the surprise that it's this short.

## Inventory (the brand is the channel: Shichi + Quill)
- Logo shape: Quill's rounded face-screen. Core control: the terminal / Claude Code prompt. Material: low-poly flat-shaded, night balcony.
- Key verb: *ask*. Success moment: a rendered MP4. Voice: Quill cheeky and fast, Shichi a sceptical dev.
- Colour logic: the screen navy `#0a1220`, Quill's eye cyan `#5eead4` (the one accent, meaning "Quill is acting"), Shichi amber `#F59E0B` (his words only).
- They would never: show a slide, a corner watermark, or a stat.

## The idea
**The tutorial happens inside Quill's face.** Quill's face is a screen, so the camera dives through it, and the terminal, the prompt and the preview are Quill's own screen.
Cover the logo: no other channel's character has a face that *is* the product UI. Other ideas considered: a UI documentary over a floating terminal card (the generic default)
and a typographic essay (it loses the characters the audience came for).

## Film shape
hook → dive (proof) → reaction → dive (proof) → reaction → dive (proof) → reaction → small close on the same screen. Proof is about 65% of the running time.

| # | t (s) | role | buys: the viewer… | picture (text covered) | entry / exit / handoff |
|---|---|---|---|---|---|
| 1 | 0–4.0 | hook | believes it really is 30 s | Quill close-up, already moving; the screen brightens on "Here it is" | starts mid-dolly; the screen light rises into the dive |
| 2 | 4.05–4.98 | turn | sees someone ready to follow along | Shichi close-up, typing pose | cut on motion |
| 3 | 4.98–13.18 | **proof (hero)** | sees the exact commands | the camera dives *through Quill's screen*; the terminal fills the frame; requirements, then two install commands typed in time with speech; the camera pans along the line | **riser → silence → impact** as the screen fills; exits with the portal pulling back, cut on motion |
| 4 | 13.21–14.69 | turn | feels the "now what?" | Shichi close-up, happy, ? emote | cut |
| 5 | 14.71–19.70 | proof | learns that "using it" means just asking | Quill shrugs, then dives again: the Claude Code prompt types word by word **as Quill says it** | soft whoosh in, cut out |
| 6 | 19.72–21.72 | turn | wonders about checking before rendering | Shichi curious | cut |
| 7 | 21.70–25.06 | proof | sees preview → render → a file | dive: `npx hyperframes preview` → a live 9:16 preview of the fade-in title → `npx hyperframes render` → an `my-video.mp4` tile lands (from oversize, decelerating) | ding on the landing |
| 8 | 25.08–26.19 | turn | shares the surprise | Shichi shock close-up, ! emote (the film's one spring) | cut |
| 9 | 26.21–29.72 | cta | knows there's a part 2 | Quill cheeky; on "part two" his own screen shows `part 2 →` in his eye glyph style; ends on Quill's wink, hold ≈0.6 s | quieter than the start |

Hero (screenshot-worthy) moment: the first dive at ~5.1 s, when Quill's screen opens into the full-frame terminal.

## Rules applied
- No corner mark, tracked-caps labels, counters, kicker titles, checkmark cards, tag pills or end card (motionmaxxing "Never ship").
- Captions run word by word at speech rhythm (sound-off viewers), with the active word in the speaker's colour and no speaker badge; they sit inside TikTok's safe zone (bottom ≤ 1600 px).
- Entries decelerate (expo-out), with no bounce except the single "!" spring. Nothing fades between scenes: the portal unmasks.
- Terminal type is magnified (≥ 0.04 H scaled to the frame width) and cropped by the frame edge; the camera follows the caret.
- No invented output: commands are the real README commands, and their output isn't faked. The preview shows exactly what the spoken prompt asks for.
- One accent with one meaning: cyan = Quill acting.
