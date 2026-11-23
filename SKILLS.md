# Video-creator skills installed (Claude Code, Shichi.AI TikTok pipeline)

Checked on disk on 19 Nov 2026. Re-check in a new container with `ls ~/.claude/skills`.

## Core engine: HyperFrames (HTML → MP4, local, free). Used on every video
- **hyperframes**: entry point; routes a request to the right workflow
- **hyperframes-core**: composition rules (data-* timing, clips, tracks, sub-compositions)
- **hyperframes-cli**: init / lint / validate / inspect / snapshot / preview / render
- **hyperframes-animation**: motion recipes, transitions, GSAP / Three.js / Lottie adapters
- **hyperframes-creative**: creative direction, palettes, typography, beat planning
- **hyperframes-media**: TTS voiceover, music, transcription, captions
- **hyperframes-registry**: install ready-made blocks/components
- **remotion-to-hyperframes**: port Remotion projects to HyperFrames

## Motion design & direction. Used on the tutorials
- **motionmaxxing**: motion-director rules and automatic quality gates (G0–G5: render exists, no empty frames, short ending, no page chrome); no slide/deck layouts
- **video-shotcraft**: 124 camera/shot recipes, cinematic pacing, sound phrasing (riser → impact → sparkle)
- **motion-graphics**: short kinetic type / logo stings / lower-thirds
- **gsap-core, gsap-timeline, gsap-plugins, gsap-utils, gsap-performance**: GSAP animation
- **framer-motion, lottie-bodymovin, svg-character-animation**: other animation systems

## 3D (characters Shichi + Quill are low-poly Three.js)
- **threejs-fundamentals, threejs-animation, threejs-lighting, threejs-materials, threejs-shaders, threejs-postprocessing** (+ more `threejs-*` skills)
- **3dviz-pro-max**: 3D explainers and scientific visualisation
- **anatomy**: isometric technical diagrams
- **lowpoly-style, chibi-style, cartoon-style**: art-direction guides
- **Blender**: blender-modeler, animation, lighting, rendering, camera-cinematography (+ MCP for Blender: Blender 4.5 LTS headless in the cloud via `tools/blender_mcp.sh`, Blender 5.3 on the user's PC)

## Audio
- **elevenlabs, text-to-speech, sound-effects, speech-to-text**: voices (Will = Shichi, Laura = Quill), SFX, transcription
- **music, acestep**: background music / soundtracks

## Editing & analysis
- **ffmpeg**: cutting, mixing, frame grabs, loudness
- **video-edit, video-toolkit**: general editing
- **video-understand**, **watch** (project skill in `.claude/skills/watch`): analyse videos, extract frames/transcripts
- **reverse-any-video**: break down a reference video's structure
- **video-download**: fetch reference videos

## Workflows (ready-made video types)
- **create-video**, **music-to-video** (beat-synced), **slideshow**, **website-to-video**, **synthetic-screen-recording**, **playwright-recording**, **manim-composer** (math animation), **dream-loop** (surreal loops)

## AI video generation (paid / need API keys; not used, all our video is rendered locally)
- ai-video-gen, heygen, avatar-video, seedance-2-5, kling-official, ltx2, minimax-h3, gemini-omni, atlas-cloud, media-use

## Not installed in the current container
- **editor-v1** (NextPhase documentary-style editor): listed in CLAUDE.md but missing after a container reset; re-install from the Google Drive zip before use.

## Tools in the environment
- HyperFrames 0.9.30 (pinned), Node.js 22, FFmpeg, headless Chromium, Blender 4.5 LTS
- Render workflow: drafts by default (`tools/hf_render.sh`), master quality only on request
- TikTok: drafts sent to the inbox via `tiktok_draft.py` (no direct posting)
