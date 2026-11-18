# HyperFrames tutorial Part 2: "your first real video" (DRAFT, awaiting approval)

Format: same as Part 1 (Shichi + Quill, dives into Quill's face-screen, word-by-word captions). Target ~40 s.

| # | Who | Line | On Quill's screen |
|---|---|---|---|
| 0 | dev | Part two! I installed HyperFrames. Now what? | hook: Shichi at the desk, the empty terminal glowing |
| 1 | quill | Now we make a real video. Step one: start a project. | |
| 2 | quill | Type npx hyperframes init, then a name. | `$ npx hyperframes init my-video` / `$ cd my-video` |
| 3 | dev | Then I write code? | |
| 4 | quill | Nope. Just describe it. Topic, length, style. | prompt word by word: "Using /hyperframes, make a 20-second vertical video about how volcanoes erupt. Bold text, dark theme." then `✻ Working…` |
| 5 | quill | Be specific. Vertical for TikTok, and say how long. | "vertical" and "20-second" highlight |
| 6 | dev | And if I hate the colours? | |
| 7 | quill | Open the preview. You can edit anything on the timeline, or just tell me: make it orange. | `$ npx hyperframes preview`, mini timeline, the preview turns orange on "orange" |
| 8 | dev | Rendering takes forever though. | |
| 9 | quill | Render a draft while you tweak. High quality only for the final. | `$ npx hyperframes render --quality draft` / `$ npx hyperframes render --quality high` |
| 10 | dev | Wait… that's my first video? | the volcano video plays in a 9:16 frame |
| 11 | quill | Made on your own computer. Free. | |
| 12 | quill | Part three: adding your own voice. Follow! | face-screen: `part 3 →` |

## Facts and sources
- `npx hyperframes init my-video`, `cd my-video`, `preview`, `render`: official README (github.com/heygen-com/hyperframes).
- `--quality draft | high`: `npx hyperframes@0.9.30 render --help`.
- Preview opens Studio, where everything is editable on the timeline: hyperframes-cli skill docs.
- Voiceover/captions exist (supports the Part 3 tease): hyperframes-media skill docs.
- Not shown on purpose: named workflow skills (/faceless-explainer etc.), which may need a separate `npx skills add` step.

## Open choices
- Line 11: add "no watermark"?
- Line 12: Part 3 tease vs "Comment what you made, I'll react to the best ones!"
