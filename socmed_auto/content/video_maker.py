"""Create TikTok-ready MP4 videos with TTS voiceover and cinematic motion effects."""

import subprocess
from pathlib import Path

import numpy as np
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# (top-left bg, top-right bg, bottom-left bg, bottom-right bg, text, accent)
PALETTES = [
    ("#0F0C29", "#302B63", "#1a0533", "#6B21A8", "#FFFFFF", "#C084FC"),
    ("#000428", "#004E92", "#001528", "#0EA5E9", "#FFFFFF", "#38BDF8"),
    ("#0a0a0a", "#1a1a2e", "#0d1117", "#1E3A5F", "#FFFFFF", "#F59E0B"),
    ("#0a0a0a", "#0f2027", "#1a1a1a", "#134e4a", "#FFFFFF", "#34D399"),
    ("#1a0000", "#450a0a", "#200122", "#7f1d1d", "#FFFFFF", "#F87171"),
    ("#0a0a1a", "#1e1b4b", "#0f0f1f", "#312e81", "#F3F4F6", "#818CF8"),
]


def _hex(c):
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def _ease_out(t):
    t = max(0.0, min(1.0, float(t)))
    return 1 - (1 - t) ** 3


# ── Background ───────────────────────────────────────────────────────────────

def _mesh_gradient(tl, tr, bl, br):
    """4-corner bilinear gradient via numpy — richer than a linear sweep."""
    c = [np.array(_hex(h), dtype=np.float32) for h in (tl, tr, bl, br)]
    xs = np.linspace(0.0, 1.0, WIDTH, dtype=np.float32)
    ys = np.linspace(0.0, 1.0, HEIGHT, dtype=np.float32)
    top = c[0] * (1 - xs[:, None]) + c[1] * xs[:, None]           # (W, 3)
    btm = c[2] * (1 - xs[:, None]) + c[3] * xs[:, None]           # (W, 3)
    grid = top[None] * (1 - ys[:, None, None]) + btm[None] * ys[:, None, None]  # (H, W, 3)
    return Image.fromarray(grid.astype(np.uint8))


def _add_glow(img_rgba, cx, cy, radius, color_hex, alpha=80):
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*_hex(color_hex), alpha),
    )
    img_rgba.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius=radius // 2)))


def _build_background(p):
    """Pre-render: mesh gradient + bokeh glows + frosted-glass content card."""
    bg = _mesh_gradient(p[0], p[1], p[2], p[3]).convert("RGBA")
    _add_glow(bg, int(WIDTH * 0.82), int(HEIGHT * 0.13), 480, p[5], alpha=70)
    _add_glow(bg, int(WIDTH * 0.18), int(HEIGHT * 0.73), 400, p[5], alpha=50)
    _add_glow(bg, int(WIDTH * 0.5),  int(HEIGHT * 0.45), 300, p[5], alpha=25)

    img = bg.convert("RGB")

    # Frosted-glass card over the content region
    cx, cy = 30, 160
    cw, ch = WIDTH - 60, HEIGHT - 310
    region = img.crop((cx, cy, cx + cw, cy + ch))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=22))
    card_mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(card_mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=56, fill=255)
    img.paste(blurred, (cx, cy), card_mask)

    # Dark tint on the card
    tint = Image.new("RGBA", (cw, ch), (8, 6, 24, 130))
    temp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    temp.paste(tint, (cx, cy), card_mask)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(temp)

    # Thin accent border on the card
    border = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border)
    bdraw.rounded_rectangle(
        [cx, cy, cx + cw - 1, cy + ch - 1],
        radius=56, outline=(*_hex(p[5]), 60), width=2,
    )
    img_rgba.alpha_composite(border)

    return img_rgba.convert("RGB")


# ── Text helpers ─────────────────────────────────────────────────────────────

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


def _centered_text_layer(text, cy, font, color, max_w=WIDTH - 100, spacing=22):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    lines = _wrap(text, font, max_w)
    bb = font.getbbox("Ag")
    lh = bb[3] - bb[1] + spacing
    y = cy - lh * len(lines) // 2
    for line in lines:
        w = font.getlength(line)
        x = (WIDTH - w) / 2
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=color)
        y += lh
    return img


def _point_layer(idx, text, font_num, font_pt, accent, text_col):
    """Small RGBA image for one numbered bullet. Returns (image, height)."""
    max_text_w = WIDTH - 250
    lines = _wrap(text, font_pt, max_text_w)
    bb = font_pt.getbbox("Ag")
    lh = bb[3] - bb[1] + 16
    total_h = lh * len(lines)
    badge = 64
    row_h = max(total_h, badge) + 32
    img_w = WIDTH - 100

    img = Image.new("RGBA", (img_w, row_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Left accent bar
    draw.rectangle([0, 10, 7, row_h - 10], fill=(*_hex(accent), 255))

    # Number circle badge
    bx, by = 22, (row_h - badge) // 2
    draw.ellipse([bx, by, bx + badge, by + badge], fill=(*_hex(accent), 220))
    ns = str(idx + 1)
    nb = font_num.getbbox(ns)
    draw.text(
        (bx + (badge - (nb[2] - nb[0])) // 2 - nb[0],
         by + (badge - (nb[3] - nb[1])) // 2 - nb[1]),
        ns, font=font_num, fill=(0, 0, 0, 255),
    )

    # Point text
    tx = bx + badge + 24
    ty = (row_h - total_h) // 2
    for line in lines:
        draw.text((tx + 2, ty + 2), line, font=font_pt, fill=(0, 0, 0, 160))
        draw.text((tx, ty), line, font=font_pt, fill=(*_hex(text_col), 255))
        ty += lh

    return img, row_h


# ── Compositing ───────────────────────────────────────────────────────────────

def _comp(base, layer, alpha=1.0, ox=0, oy=0):
    """Composite layer (RGBA) onto base (RGB) at offset (ox, oy) with alpha scale."""
    if alpha <= 0 or layer is None:
        return base

    # Fast path: no offset, full alpha
    if ox == 0 and oy == 0 and alpha >= 1.0:
        result = base.convert("RGBA")
        result.alpha_composite(layer)
        return result.convert("RGB")

    # Clip to canvas bounds
    sx0 = max(0, -ox);  sy0 = max(0, -oy)
    dx0 = max(0,  ox);  dy0 = max(0,  oy)
    cw = min(layer.width  - sx0, WIDTH  - dx0)
    ch = min(layer.height - sy0, HEIGHT - dy0)
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
    hook = content.get("hook", "")
    pts = content.get("points", [])[:3]
    cta = content.get("cta", "Follow for more tips like this")
    script = ". ".join(p.rstrip(".") for p in [hook] + pts + [cta] if p) + "."
    gTTS(script, lang="en", slow=False).save(output_path)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


# ── Main render ───────────────────────────────────────────────────────────────

def create_video(content, output_path, palette_idx=0, duration_secs=None):
    """Render an MP4 from content dict. Returns output_path."""
    frames_dir = Path(output_path).parent / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    p = PALETTES[palette_idx % len(PALETTES)]
    hook = content.get("hook", "")
    main_text = content.get("on_screen_text", content.get("title", ""))
    points = content.get("points", [])[:3]

    audio_path = str(frames_dir / "voice.mp3")
    audio_dur = _generate_tts(content, audio_path)
    total_secs = audio_dur + 1.5
    total_frames = int(total_secs * FPS)

    # ── Pre-render all static layers (done once) ──────────────────────────
    bg = _build_background(p)

    fhook  = ImageFont.truetype(FONT_BOLD,    86)
    fmain  = ImageFont.truetype(FONT_BOLD,    70)
    fpoint = ImageFont.truetype(FONT_REGULAR, 52)
    fnum   = ImageFont.truetype(FONT_BOLD,    40)
    fsmall = ImageFont.truetype(FONT_REGULAR, 40)

    hook_lyr = _centered_text_layer(hook,      330, fhook, p[5], max_w=WIDTH - 130, spacing=24)
    main_lyr = _centered_text_layer(main_text, 660, fmain, p[4], max_w=WIDTH - 100, spacing=26)
    cta_lyr  = _centered_text_layer("Follow for more tips  👆", 1790, fsmall, p[5])
    wm_lyr   = _centered_text_layer("@socmed_auto", 1858, fsmall, p[4])

    # Accent divider line
    div_img = Image.new("RGBA", (WIDTH - 180, 3), (0, 0, 0, 0))
    ImageDraw.Draw(div_img).rectangle([0, 0, WIDTH - 181, 2], fill=(*_hex(p[5]), 190))

    # Points
    pt_layers, pt_ys = [], []
    y_cur = 930
    for i, pt in enumerate(points):
        lyr, h = _point_layer(i, pt, fnum, fpoint, p[5], p[4])
        pt_layers.append(lyr)
        pt_ys.append(y_cur)
        y_cur += h + 18

    # ── Frame loop ─────────────────────────────────────────────────────────
    for fi in range(total_frames):
        t = fi / FPS
        pct = t / total_secs

        fade = min(1.0, _ease_out(t / max(0.001, total_secs * 0.05)))
        zoom = 1.03 - 0.03 * min(1.0, pct)

        frame = bg.copy()

        # Hook: slides down from -55 → 0, fades in over first 12%
        hk_a  = _ease_out(pct / 0.12)
        hk_dy = int((1 - _ease_out(pct / 0.12)) * -55)
        frame = _comp(frame, div_img,  alpha=hk_a, ox=90, oy=500 + hk_dy)
        frame = _comp(frame, hook_lyr, alpha=hk_a, oy=hk_dy)

        # Main text: slides up from +65 → 0, appears at 25%
        mr = (pct - 0.25) / 0.15
        ma = _ease_out(mr)
        m_dy = int((1 - _ease_out(max(0.0, min(1.0, mr)))) * 65)
        frame = _comp(frame, main_lyr, alpha=ma, oy=m_dy)

        # Points: slide in from right, staggered, start at 50%
        for i, (pl, py) in enumerate(zip(pt_layers, pt_ys)):
            pr = (pct - (0.50 + i * 0.10)) / 0.14
            pa = _ease_out(pr)
            if pa <= 0:
                continue
            slide_x = int((1 - _ease_out(max(0.0, min(1.0, pr)))) * (WIDTH + 220))
            frame = _comp(frame, pl, alpha=min(1.0, pa), ox=50 + slide_x, oy=py)

        # Progress bar
        draw = ImageDraw.Draw(frame)
        bw = int((WIDTH - 160) * min(1.0, pct))
        draw.rectangle([(80, HEIGHT - 55), (WIDTH - 80, HEIGHT - 42)], fill=(255, 255, 255, 20))
        if bw > 0:
            draw.rectangle([(80, HEIGHT - 55), (80 + bw, HEIGHT - 42)], fill=p[5])

        # CTA + watermark
        frame = _comp(frame, cta_lyr, alpha=_ease_out((pct - 0.85) / 0.1))
        frame = _comp(frame, wm_lyr,  alpha=0.4)

        # Global fade-in (first ~5% of video)
        if fade < 1.0:
            black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
            frame = Image.blend(black, frame, fade)

        # Slow zoom-out (1.03× → 1.0×)
        if zoom != 1.0:
            nw, nh = int(WIDTH * zoom), int(HEIGHT * zoom)
            frame = frame.resize((nw, nh), Image.LANCZOS)
            left = (nw - WIDTH) // 2
            top  = (nh - HEIGHT) // 2
            frame = frame.crop((left, top, left + WIDTH, top + HEIGHT))

        frame.save(frames_dir / f"frame_{fi:05d}.png")

    # ── FFmpeg encode ─────────────────────────────────────────────────────
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    for f in frames_dir.glob("*.png"):
        f.unlink()
    for f in frames_dir.glob("*.mp3"):
        f.unlink()
    frames_dir.rmdir()

    return output_path
