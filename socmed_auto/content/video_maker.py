"""
TikTok video maker — kinetic-word style with floating UI cards, light-mode aesthetic.
Matches the product-demo / Apple-promo look: clean gray bg, large centered words,
niche-specific UI mockup cards drifting at the edges.
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Light-mode: (bg, text, accent)
PALETTES = [
    ("#EAEAEA", "#111111", "#2563EB"),   # blue
    ("#EAEAEA", "#111111", "#16A34A"),   # green
    ("#EAEAEA", "#111111", "#D97706"),   # amber
    ("#EAEAEA", "#111111", "#7C3AED"),   # purple
    ("#EAEAEA", "#111111", "#DC2626"),   # red
    ("#EAEAEA", "#111111", "#0891B2"),   # cyan
]

CARD_DATA = {
    "ai_tech": [
        ("code", "script.py",
         ["import anthropic", "client = Client()", "msg = client.chat(", "  model='claude'", ")"]),
        ("stat", "Time Saved", "12.5 hrs", "per week with AI"),
        ("stat", "Tasks Done", "47", "automated today"),
        ("todo", "AI Workflow",
         ["Write prompt", "Review output", "Refine & ship", "Save template"]),
    ],
    "productivity": [
        ("todo", "Today",
         ["Deep work 2hrs", "Inbox zero", "Review goals", "Learn 30 min"]),
        ("stat", "Focus Score", "87%", "+12% this week"),
        ("stat", "Done Today", "23 / 25", "tasks completed"),
        ("note", "2-min Rule", ["If it takes < 2min", "do it RIGHT NOW"]),
    ],
    "money": [
        ("stat", "Portfolio", "$12,450", "+$340 today"),
        ("stat", "Savings Rate", "32%", "Goal: 40%"),
        ("todo", "Investments",
         ["Index funds 60%", "Bonds 20%", "REITs 10%", "Cash 10%"]),
        ("stat", "Side Income", "$850", "this month"),
    ],
    "default": [
        ("stat", "Score", "98%", "above average"),
        ("stat", "Completed", "47 tasks", "this week"),
        ("todo", "Quick Tips",
         ["Start small", "Be consistent", "Track progress", "Celebrate wins"]),
        ("note", "Key Insight", ["One small habit", "changes everything"]),
    ],
}


def _hex(c):
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def _ease_out(t):
    t = max(0.0, min(1.0, float(t)))
    return 1 - (1 - t) ** 3


# ── Card rendering ────────────────────────────────────────────────────────────

def _shadow_layer(w, h, radius, blur=16, opacity=35):
    s = Image.new("RGBA", (w + blur * 2, h + blur * 2), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle(
        [blur, blur, w + blur, h + blur], radius=radius, fill=(0, 0, 0, opacity)
    )
    return s.filter(ImageFilter.GaussianBlur(radius=blur // 2))


def _stat_card(label, value, sub, accent):
    w, h, r = 540, 220, 24
    out = Image.new("RGBA", (w + 36, h + 36), (0, 0, 0, 0))
    out.alpha_composite(_shadow_layer(w, h, r), (0, 0))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(255, 255, 255, 250))
    ac = _hex(accent)
    d.rectangle([24, 0, 100, 5], fill=(*ac, 255))
    d.text((26, 22),  label.upper(),  font=ImageFont.truetype(FONT_REGULAR, 26), fill=(140, 140, 140, 220))
    d.text((26, 56),  value,          font=ImageFont.truetype(FONT_BOLD,    68), fill=(15, 15, 15, 255))
    d.text((26, 148), sub,            font=ImageFont.truetype(FONT_REGULAR, 30), fill=(*ac, 230))
    out.alpha_composite(card, (18, 18))
    return out


def _code_card(title, lines, accent):
    w, h, r = 600, 290, 20
    out = Image.new("RGBA", (w + 36, h + 36), (0, 0, 0, 0))
    out.alpha_composite(_shadow_layer(w, h, r, blur=20, opacity=28), (0, 0))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(22, 22, 30, 248))
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (40, 201, 64)]):
        d.ellipse([18 + i * 24, 13, 32 + i * 24, 27], fill=(*col, 255))
    d.text((90, 11), title, font=ImageFont.truetype(FONT_REGULAR, 22), fill=(160, 160, 180, 180))
    d.line([(0, 42), (w, 42)], fill=(60, 60, 80, 140), width=1)
    code_cols = [(100, 180, 255), (200, 150, 255), (255, 220, 100), (100, 220, 150), (255, 180, 100)]
    fc = ImageFont.truetype(FONT_REGULAR, 26)
    for i, line in enumerate(lines[:5]):
        d.text((22, 54 + i * 44), line, font=fc, fill=(*code_cols[i % 5], 230))
    out.alpha_composite(card, (18, 18))
    return out


def _todo_card(title, items, accent):
    w, h, r = 500, 300, 24
    out = Image.new("RGBA", (w + 36, h + 36), (0, 0, 0, 0))
    out.alpha_composite(_shadow_layer(w, h, r), (0, 0))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(255, 255, 255, 250))
    ac = _hex(accent)
    d.text((24, 18), title, font=ImageFont.truetype(FONT_BOLD, 30), fill=(30, 30, 30, 255))
    d.line([(24, 56), (w - 24, 56)], fill=(210, 210, 210, 180), width=1)
    fi = ImageFont.truetype(FONT_REGULAR, 26)
    fb = ImageFont.truetype(FONT_BOLD, 16)
    for i, item in enumerate(items[:4]):
        y = 70 + i * 54
        done = i < 2
        bx, by = 24, y + 2
        if done:
            d.rounded_rectangle([bx, by, bx + 24, by + 24], radius=6, fill=(*ac, 240))
            d.text((bx + 4, by + 3), "✓", font=fb, fill=(255, 255, 255, 255))
        else:
            d.rounded_rectangle([bx, by, bx + 24, by + 24], radius=6, outline=(*ac, 100), width=2)
        col = (60, 60, 60, 255) if done else (140, 140, 140, 255)
        d.text((58, y), item.lstrip("✓ "), font=fi, fill=col)
    out.alpha_composite(card, (18, 18))
    return out


def _note_card(label, lines, accent):
    w, h, r = 480, 220, 22
    out = Image.new("RGBA", (w + 32, h + 32), (0, 0, 0, 0))
    out.alpha_composite(_shadow_layer(w, h, r, blur=14, opacity=28), (0, 0))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    ac = _hex(accent)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(*ac, 235))
    d.text((26, 20), label, font=ImageFont.truetype(FONT_REGULAR, 26), fill=(255, 255, 255, 180))
    fv = ImageFont.truetype(FONT_BOLD, 40)
    for i, line in enumerate(lines[:3]):
        d.text((26, 60 + i * 54), line, font=fv, fill=(255, 255, 255, 255))
    out.alpha_composite(card, (16, 16))
    return out


def _build_cards(niche, accent):
    """Pre-render card images + define their floating params."""
    data = CARD_DATA.get(niche, CARD_DATA["default"])
    renderers = {"stat": _stat_card, "code": _code_card, "todo": _todo_card, "note": _note_card}

    raw = []
    for item in data[:4]:
        kind = item[0]
        fn = renderers.get(kind)
        if fn:
            raw.append(fn(*item[1:], accent))

    # (base_x, base_y, amp_x, amp_y, period_s, rotation_deg, alpha)
    layouts = [
        (-160, 220,  70,  45, 9.0,  -7, 0.72),  # upper-left
        (WIDTH - 480, 140, -55, 50, 11.0, 6, 0.68),  # upper-right
        (-170, HEIGHT - 680, 65, -50, 8.0,  5, 0.68),  # lower-left
        (WIDTH - 430, HEIGHT - 620, -65,  40, 10.0, -8, 0.72),  # lower-right
    ]

    cards = []
    for img, (bx, by, ax, ay, period, angle, alpha) in zip(raw, layouts):
        rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)
        cards.append(dict(img=rotated, bx=bx, by=by, ax=ax, ay=ay, period=period, alpha=alpha))
    return cards


def _card_xy(card, t):
    x = card["bx"] + card["ax"] * math.sin(2 * math.pi * t / card["period"])
    y = card["by"] + card["ay"] * math.cos(2 * math.pi * t / (card["period"] * 0.65))
    return int(x), int(y)


# ── Beat (kinetic text) schedule ─────────────────────────────────────────────

def _build_beats(content, audio_dur):
    """Return [(start_pct, end_pct, text, is_cta), …] covering 0–1."""
    hook = content.get("hook", "")
    points = content.get("points", [])[:3]

    # Hook: 2 words at a time
    hw = hook.split()
    hook_chunks = [" ".join(hw[i:i + 2]) for i in range(0, len(hw), 2)]

    # Points: first 4 words each
    pt_chunks = [" ".join(pt.split()[:4]) for pt in points]

    cta = "Follow for more"
    all_chunks = hook_chunks + pt_chunks + [cta]
    n = len(all_chunks)

    n_hook = len(hook_chunks)
    n_pts  = len(pt_chunks)
    hook_frac = 0.44
    pts_frac  = 0.42
    cta_frac  = 0.14

    beats = []
    for i, chunk in enumerate(hook_chunks):
        s = (i / n_hook) * hook_frac
        e = ((i + 1) / n_hook) * hook_frac
        beats.append((s, e, chunk, False))
    for i, chunk in enumerate(pt_chunks):
        s = hook_frac + (i / max(1, n_pts)) * pts_frac
        e = hook_frac + ((i + 1) / max(1, n_pts)) * pts_frac
        beats.append((s, e, chunk, False))
    s_cta = hook_frac + pts_frac
    beats.append((s_cta, 1.0, cta, True))

    return beats


def _beat_alpha(pct, start, end):
    span = max(0.001, end - start)
    pos  = (pct - start) / span
    if pos < 0.18:
        return _ease_out(pos / 0.18)
    if pos > 0.78:
        return _ease_out((1.0 - pos) / 0.22)
    return 1.0


def _get_beat(pct, beats):
    for start, end, text, is_cta in beats:
        if start <= pct < end:
            return text, is_cta, _beat_alpha(pct, start, end)
    return "", False, 0.0


# ── Text layers ───────────────────────────────────────────────────────────────

def _wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if font.getlength(test) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _make_beat_layer(text, is_cta, text_hex, accent_hex):
    """RGBA full-canvas layer for one kinetic beat."""
    n = len(text.split())
    size = 190 if n == 1 else 160 if n == 2 else 128 if n == 3 else 96
    font = ImageFont.truetype(FONT_BOLD, size)

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    lines = _wrap(text, font, WIDTH - 100)
    bb = font.getbbox("Ag")
    lh = bb[3] - bb[1] + 18
    total_h = lh * len(lines)

    # Vertical center; for CTA push up slightly
    cy = HEIGHT // 2 - (80 if is_cta else 0)
    y  = cy - total_h // 2

    col = _hex(accent_hex) if is_cta else _hex(text_hex)
    for line in lines:
        w_px = font.getlength(line)
        x = (WIDTH - w_px) / 2
        draw.text((x, y), line, font=font, fill=(*col, 255))
        y += lh

    # CTA: subtitle line below
    if is_cta:
        fsub = ImageFont.truetype(FONT_REGULAR, 46)
        sub  = "for tips like this 👆"
        sw   = fsub.getlength(sub)
        draw.text(((WIDTH - sw) / 2, cy + total_h // 2 + 32), sub,
                  font=fsub, fill=(*_hex(text_hex), 190))

    return layer


def _make_vignette(bg_hex):
    """Top + bottom gradient in bg color to fade off-screen card edges."""
    rgb  = _hex(bg_hex)
    vig  = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)
    h    = 320
    for y in range(h):
        a = int(240 * (1 - y / h) ** 1.8)
        draw.line([(0, y),            (WIDTH, y)],            fill=(*rgb, a))
        draw.line([(0, HEIGHT - 1 - y), (WIDTH, HEIGHT - 1 - y)], fill=(*rgb, a))
    return vig


def _make_wm(text_hex, accent_hex):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)
    font  = ImageFont.truetype(FONT_REGULAR, 32)
    wm    = "@socmed_auto"
    w_px  = font.getlength(wm)
    draw.text(((WIDTH - w_px) / 2, HEIGHT - 52), wm,
              font=font, fill=(*_hex(text_hex), 70))
    return layer


# ── Compositing ───────────────────────────────────────────────────────────────

def _comp(base, layer, alpha=1.0, ox=0, oy=0):
    if alpha <= 0 or layer is None:
        return base
    if ox == 0 and oy == 0 and alpha >= 1.0:
        result = base.convert("RGBA")
        result.alpha_composite(layer)
        return result.convert("RGB")
    sx0 = max(0, -ox);  sy0 = max(0, -oy)
    dx0 = max(0,  ox);  dy0 = max(0,  oy)
    cw  = min(layer.width  - sx0, WIDTH  - dx0)
    ch  = min(layer.height - sy0, HEIGHT - dy0)
    if cw <= 0 or ch <= 0:
        return base
    region = layer.crop((sx0, sy0, sx0 + cw, sy0 + ch))
    if alpha < 1.0:
        r, g, b, a = region.split()
        region = Image.merge("RGBA", (r, g, b, a.point(lambda p: int(p * alpha))))
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    canvas.paste(region, (dx0, dy0), region.split()[3])
    result = base.convert("RGBA")
    result.alpha_composite(canvas)
    return result.convert("RGB")


# ── TTS ───────────────────────────────────────────────────────────────────────

def _generate_tts(content, output_path):
    hook  = content.get("hook", "")
    pts   = content.get("points", [])[:3]
    cta   = content.get("cta", "Follow for more tips like this")
    script = ". ".join(p.rstrip(".") for p in [hook] + pts + [cta] if p) + "."
    gTTS(script, lang="en", slow=False).save(output_path)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


# ── Main ─────────────────────────────────────────────────────────────────────

def create_video(content, output_path, palette_idx=0, duration_secs=None):
    """Render an MP4 from content dict. Returns output_path."""
    frames_dir = Path(output_path).parent / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    p = PALETTES[palette_idx % len(PALETTES)]
    bg_hex, text_hex, accent_hex = p
    niche = content.get("niche", "default")

    audio_path = str(frames_dir / "voice.mp3")
    audio_dur  = _generate_tts(content, audio_path)
    total_secs = audio_dur + 1.0
    total_frames = int(total_secs * FPS)

    # ── Pre-render all static assets ─────────────────────────────────────
    bg      = Image.new("RGB", (WIDTH, HEIGHT), _hex(bg_hex))
    cards   = _build_cards(niche, accent_hex)
    vignette = _make_vignette(bg_hex)
    wm_lyr  = _make_wm(text_hex, accent_hex)

    beats = _build_beats(content, audio_dur)
    beat_cache = {}
    for _, _, text, is_cta in beats:
        if text not in beat_cache:
            beat_cache[text] = _make_beat_layer(text, is_cta, text_hex, accent_hex)

    # ── Frame loop ────────────────────────────────────────────────────────
    for fi in range(total_frames):
        t   = fi / FPS
        pct = t / total_secs

        frame = bg.copy()

        # Floating UI cards
        for card in cards:
            cx, cy = _card_xy(card, t)
            frame = _comp(frame, card["img"], alpha=card["alpha"], ox=cx, oy=cy)

        # Vignette fades cards at top/bottom edges
        frame = _comp(frame, vignette)

        # Kinetic word
        beat_text, is_cta, text_alpha = _get_beat(pct, beats)
        if beat_text and text_alpha > 0:
            frame = _comp(frame, beat_cache[beat_text], alpha=text_alpha)

        # Watermark
        frame = _comp(frame, wm_lyr, alpha=0.9)

        # Fade in
        fade = min(1.0, _ease_out(t / max(0.001, total_secs * 0.04)))
        if fade < 1.0:
            frame = Image.blend(Image.new("RGB", (WIDTH, HEIGHT), _hex(bg_hex)), frame, fade)

        frame.save(frames_dir / f"frame_{fi:05d}.png")

    # ── FFmpeg ────────────────────────────────────────────────────────────
    subprocess.run(
        ["ffmpeg", "-y",
         "-framerate", str(FPS),
         "-i", str(frames_dir / "frame_%05d.png"),
         "-i", audio_path,
         "-c:v", "libx264", "-preset", "fast", "-crf", "22",
         "-c:a", "aac", "-b:a", "128k",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest",
         output_path],
        check=True, capture_output=True,
    )

    for f in frames_dir.glob("*.png"):
        f.unlink()
    for f in frames_dir.glob("*.mp3"):
        f.unlink()
    frames_dir.rmdir()

    return output_path
