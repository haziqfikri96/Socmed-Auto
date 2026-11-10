"""Create TikTok-ready MP4 videos from text content using Pillow + FFmpeg."""

import os
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# TikTok vertical format
WIDTH, HEIGHT = 1080, 1920
FPS = 30

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Gradient palettes (start_color, end_color, text_color, accent_color)
PALETTES = [
    ("#0F0C29", "#302B63", "#FFFFFF", "#A78BFA"),   # Deep purple
    ("#000428", "#004E92", "#FFFFFF", "#60A5FA"),   # Ocean blue
    ("#1a1a2e", "#16213e", "#FFFFFF", "#F59E0B"),   # Dark gold
    ("#0a0a0a", "#1a1a1a", "#FFFFFF", "#34D399"),   # Dark green
    ("#200122", "#6f0000", "#FFFFFF", "#F87171"),   # Dark red
    ("#0d0d0d", "#1f1f1f", "#F3F4F6", "#818CF8"),   # Dark indigo
]


def _gradient_image(color1: str, color2: str) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.getlength(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_center: int,
    font: ImageFont.FreeTypeFont,
    color: str,
    max_width: int = WIDTH - 120,
    line_spacing: int = 20,
) -> int:
    """Draw word-wrapped text centered at y_center. Returns bottom y."""
    lines = _wrap_text(text, font, max_width)
    bbox = font.getbbox("Ag")
    line_h = bbox[3] - bbox[1] + line_spacing
    total_h = line_h * len(lines)
    y = y_center - total_h // 2
    for line in lines:
        w = font.getlength(line)
        draw.text(((WIDTH - w) / 2, y), line, font=font, fill=color)
        y += line_h
    return y


def make_frame(
    hook: str,
    main_text: str,
    points: list[str],
    palette_idx: int,
    alpha: float = 1.0,
    show_points_count: int = 0,
) -> Image.Image:
    p = PALETTES[palette_idx % len(PALETTES)]
    img = _gradient_image(p[0], p[1])
    draw = ImageDraw.Draw(img)

    # Semi-transparent overlay card
    overlay = Image.new("RGBA", (WIDTH - 80, HEIGHT - 300), (0, 0, 0, 120))
    img.paste(overlay, (40, 150), overlay)

    font_hook = ImageFont.truetype(FONT_BOLD, 62)
    font_main = ImageFont.truetype(FONT_BOLD, 80)
    font_point = ImageFont.truetype(FONT_REGULAR, 52)
    font_small = ImageFont.truetype(FONT_REGULAR, 42)

    # Hook text at top
    _draw_centered_text(draw, hook, 320, font_hook, p[3], max_width=WIDTH - 160)

    # Divider line
    draw.line([(160, 480), (WIDTH - 160, 480)], fill=p[3], width=3)

    # Main headline
    _draw_centered_text(draw, main_text, 650, font_main, p[2], max_width=WIDTH - 120)

    # Points (reveal progressively)
    y = 900
    for i, pt in enumerate(points[:show_points_count]):
        bullet = f"• {pt}"
        lines = _wrap_text(bullet, font_point, WIDTH - 200)
        for line in lines:
            w = font_point.getlength(line)
            draw.text(((WIDTH - w) / 2, y), line, font=font_point, fill=p[2])
            y += 72

    # CTA at bottom
    cta = "👆 Follow for more"
    w = font_small.getlength(cta)
    draw.text(((WIDTH - w) / 2, HEIGHT - 220), cta, font=font_small, fill=p[3])

    # Watermark
    wm = "@socmed_auto"
    wm_w = font_small.getlength(wm)
    draw.text(((WIDTH - wm_w) / 2, HEIGHT - 140), wm, font=font_small, fill="#ffffff80")

    if alpha < 1.0:
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        img = Image.blend(black, img, alpha)

    return img


def create_video(
    content: dict,
    output_path: str,
    palette_idx: int = 0,
    duration_secs: int = 25,
) -> str:
    """Render an MP4 from content dict. Returns output_path."""
    frames_dir = Path(output_path).parent / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    hook = content.get("hook", "")
    main_text = content.get("on_screen_text", content.get("title", ""))
    points = content.get("points", [])[:3]
    total_frames = duration_secs * FPS

    # Animation timeline:
    # 0-1s: fade in
    # 1-5s: hook only
    # 5-10s: hook + main text
    # 10-end: hook + main text + points (1 per 4s)

    for f_idx in range(total_frames):
        t = f_idx / FPS

        alpha = min(1.0, t / 0.8)
        show = 0
        if t > 10:
            show = min(len(points), int((t - 10) / 4) + 1)

        frame = make_frame(hook, main_text, points, palette_idx, alpha, show)
        frame.save(frames_dir / f"frame_{f_idx:05d}.png")

    # Encode with FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Cleanup frames
    for f in frames_dir.glob("*.png"):
        f.unlink()
    frames_dir.rmdir()

    return output_path
