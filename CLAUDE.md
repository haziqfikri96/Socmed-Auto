# Socmed-Auto — Project Context

Auto-posting TikTok video pipeline. Generates kinetic product-demo videos from AI-written scripts,
uploads via TikTok API. All video rendering is local — no paid AI APIs for video.

## Git

- Repo: `haziqfikri96/socmed-auto`
- Working branch: `claude/lucid-ritchie-xvwgs7`
- Push with: `git push -u origin claude/lucid-ritchie-xvwgs7`

## Architecture

```
auto_post.py              # CLI entry: --dry-run --niche ai_tech
socmed_auto/
  content/
    video_maker.py        # Main video renderer (PIL/Pillow + FFmpeg + HyperFrames hook)
    generator.py          # Claude API: topic/hook/script generation
  platform/
    tiktok.py             # TikTok upload client
.env                      # ANTHROPIC_API_KEY, TIKTOK_CLIENT_KEY/SECRET — NEVER commit
videos/                   # Gitignored output directory
hook-effect/              # HyperFrames kinetic hook project (3s intro, 1080×1920)
```

## Video Style — Product-Demo Aesthetic

Matches reference video: clean minimal, Apple product-promo look.

**Palette** (light-mode only):
- Background: `#E8E8E8`
- Text dark: `#0F0F0F`
- Accent (rotates per palette): `#2563EB` / `#16A34A` / `#D97706` / `#7C3AED` / `#DC2626` / `#0891B2`

**Two-tone kinetic text** (`_split_2tone` in `video_maker.py`):
- First word = accent color (action verb)
- Remaining words = dark (`#0F0F0F`) on same line
- Both measured with `font.getlength()`, centered as a unit

**App UI cards** (iOS-style panels, not abstract):
- `_stats_panel` — analytics with bar chart
- `_schedule_panel` — Upcoming Posts with time/title/badge
- `_content_panel` — Content AI with prompt chip
- `_account_panel` — avatar, handle, follow stats
- `_finance_panel` — portfolio value + sparkline
- `_todo_panel` — checklist with checkboxes

**Fonts**: LiberationSans-Bold / LiberationSans-Regular (system fonts)

## HyperFrames Hook Effect

Located at `hook-effect/` — a 3-second kinetic intro prepended to every video.

**Composition**: `hook-effect/index.html`
- 1080×1920 portrait (TikTok 9:16)
- Montserrat 900, `#E8E8E8` bg, `#2563EB` accent bar
- GSAP: accent bar sweeps → "YOUR" slams white on bar → noun lines punch up → sub-label fades → exit wipe
- `data-composition-id="hook"`, `data-duration="3"`

**Integration in `video_maker.py`**:
- `HOOK_PROJECT_DIR` = project root / `hook-effect/`
- `_render_hook(hook_text, accent_hex, out_path)` patches HTML dynamically, calls `npx hyperframes@0.9.30 render`
- FFmpeg concat: `hook.mp4` + `main_body.mp4` → final output
- Fallback: if hook render fails, uses main body only

**Commands**:
```bash
cd hook-effect
npm run check          # lint + validate
npx hyperframes@0.9.30 snapshot --at 0.3,1.0,2.0
npx hyperframes@0.9.30 render --quality high --output hook.mp4
```

## Installed Skills

### editor-v1 (NextPhase Editor V1)
Installed at: `~/.claude/skills/editor-v1/`
Source: Google Drive folder `19QyjPktZgEzqNoGO2hfyHma_9h27B65G` → `NextPhase-EditorV1.zip`

What it does: Turns a talking-head recording into a fast documentary-style edit.
- Real evidence images found online for every spoken line
- Re-coloured (teal split, B&W, amber, negative flashes)
- Named devices: tile-flash reveals, cut-out (you in front of changing world), card pop, 3D wall, datamosh
- Click SFX on every cut, music bed that cuts under punchline
- Renders with HyperFrames (HTML → MP4), free, local

**Setup status** (all ✅, cost $0):
- Python venv: `~/.cache/editor-v1/venv` (numpy, opencv, pillow, soundfile)
- GSAP 3.14.2: `~/.claude/skills/editor-v1/assets/vendor/gsap.min.js`
- Sound kit: 22 sounds in `~/.claude/skills/editor-v1/sfx/ev1kit/`
- Node.js 22, FFmpeg + VP9, HyperFrames 0.9.30, Chrome, yt-dlp — all present
- **Cut-out device (PyTorch ~1 GB)**: NOT installed — user has not confirmed yet

**How to use** (in a new session):
```
"Edit ~/Desktop/my-video.mov with editor-v1"
"Edit my latest recording in the editor v1 style, use ~/Music/track.mp3 as the bed"
"Plan the editor-v1 edit of ~/Desktop/take2.mov but don't build yet, I want to see the sources first"
```

### watch (bradautomates/claude-video)
Installed at: `/home/user/Socmed-Auto/.claude/skills/watch/`
Cloned from: `https://github.com/bradautomates/claude-video`

What it does: Analyses video files — extracts frames with ffmpeg, pulls captions/transcript.
- Local engine configured, backend=none, detail=balanced
- Run: `python3 .claude/skills/watch/scripts/watch.py "<path>" --question "<question>"`

### hyperframes + related
Built-in project skills (auto-loaded from `hook-effect/CLAUDE.md`):
- `hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-cli`
- `hyperframes-creative`, `hyperframes-media`, `hyperframes-registry`

## Key Commands

```bash
# Generate + dry-run a video (no upload)
python auto_post.py --dry-run --niche ai_tech

# Niches available: ai_tech, productivity, money (+ "default")

# Render hook only (for testing)
cd hook-effect && npx hyperframes@0.9.30 render --quality high --output hook.mp4

# Check hook composition
cd hook-effect && npm run check

# Git status + push
git status
git push -u origin claude/lucid-ritchie-xvwgs7
```

## Environment

- Python 3.13, Node.js 22.23.4, FFmpeg 6.1.1
- HyperFrames 0.9.30 (pinned)
- Chrome for Testing 153.0.8010.12 at `/opt/pw-browsers/chromium`
- yt-dlp 2026.10.26
- VP9 encoder: present in ffmpeg

## Security Rules

- **NEVER commit `.env`** — contains ANTHROPIC_API_KEY, TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
- **NEVER commit `videos/`** — gitignored
- User email `haziqfikri6796@gmail.com` — private, never send externally

## What Was Built This Session

1. **video_maker.py** — completely rewritten to product-demo style:
   - Two-tone kinetic text (accent verb + dark noun, same line)
   - iOS-style app UI panels (stats, schedule, content AI, account, finance)
   - Light gray `#E8E8E8` background, 6-palette rotation

2. **hook-effect/** — HyperFrames kinetic hook intro:
   - 3s animated intro, all checks pass
   - Dynamically patched with hook text + accent color at render time
   - FFmpeg-concatenated before main body → ~21s total video

3. **editor-v1 skill** — installed from Google Drive, all deps set up, preview rendered successfully

## Video content rules (set by the user)

- **No sources on screen.** Never put source or citation text in a video (no "Source: NASA", study names, survey dates). Sources go in the TikTok description, which is supplied alongside each video.
- **No affiliate or product promos.** Videos are fun facts with accurate, verified information.
- Verify every figure against a primary source before building, and keep a note of the sources for the description.

## Current work (November 2026) — fact videos and TikTok drafts

Work lives on branch `claude/showcase-video` until it is merged into `main`.

**Video projects** (each is a HyperFrames project; render with `npx hyperframes@0.9.30 render --quality high --output ../videos/<name>.mp4` from inside the folder; rendered MP4s are gitignored):
- `fun-facts-space/` — 23s, three space facts
- `fun-facts-ocean/` — 60s, five ocean facts
- `earth-hole/` — 37.5s, one-question 3D short with word-by-word captions

**Audio**: narration and sound effects come from ElevenLabs (key stored as a network secret for `api.elevenlabs.io`; send header `xi-api-key: proxy-injected`). Tools: `tools/make_voiceover_elevenlabs.py`, `tools/make_voiceover_timed.py`, `tools/make_sfx_elevenlabs.py`; reusable effects are in `sfx/elevenlabs/`. Each project's `make_audio.py` builds its `assets/mix.wav` (run with `~/.cache/editor-v1/venv/bin/python`, or any Python with numpy and soundfile).

**Posting to TikTok — drafts only**:
- The user reviews every video first. Only after they approve, send it with `python tiktok_draft.py videos/<file>.mp4`. This puts a draft in their TikTok inbox; they add the caption and post it in the app. Never use direct posting.
- Credentials come from environment variables `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` (sandbox app "auto-poster") and `TIKTOK_REFRESH_TOKEN`. Never print them.
- The API cannot set a caption on a draft, so always give the user the description text (with the sources) to paste.
- The draft upload had not yet been tested against TikTok when this note was written.

## Host character (use the user's exact art)

The user wants their own character, exactly as in their art, in videos from now on, not a generic dummy and not a re-drawn version.
- **Use `characters/puppet/`**: a 2D cut-out puppet made from the front view of `characters/reference-sheet.jpg` (the user's Gemini character sheet: black side-part hair, black "Shichi.AI" tee, khaki chinos, navy sneakers). The art is used pixel for pixel; only the joints move.
  - Files: part PNGs, `rig.js` (generated joints and boxes), `puppet.js` (API), `full.png` (whole cut-out), `cut_parts.py` (re-slices the parts from `full.png`; needs numpy and pillow).
  - API: `createPuppet(container, { base, height })` → `{ el, rig, pose, blend, face, place }`. Poses: idle, wave, waveL, point, pointL, armsUp, cheer, star, fall, handOnChest, handOnChestL. `face({ blink, talk })` (0..1) for blinking and lip flaps. `place({ x, y, scale, squash, rotate, flip })`, where x, y is the point between the feet. Angles are degrees, positive = clockwise. Pose field `front: ["R"]` puts that arm in front of the shirt.
  - Parts are DOM `<img>` layers, so HyperFrames waits for them to load. Copy the puppet folder into each project (HyperFrames serves only the project folder); skip `full.png` and `cut_parts.py`.
  - Limits: it faces the camera only (no turning or side views), and the hands keep their open shape (no peace sign).
- `characters/avatar.js` is an older, simplified Three.js 3D model of the character. The user rejected it as not exact; use it only if they ask for a true 3D scene.
- Preview: `character-preview/`, a 10s puppet demo (pop-in, wave with "Hi!", point, jump, hand on chest, cheer).
