"""Create TikTok-ready MP4 videos with TTS voiceover and motion effects."""

import subprocess
from pathlib import Path

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FPS = 30

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

PALETTES = [
    ("#0F0C29", "#302B63", "#FFFFFF", "#A78BFA"),
    ("#000428", "#004E92", "#FFFFFF", "#60A5FA"),
    ("#1a1a2e", "#16213e", "#FFFFFF", "#F59E0B"),
    ("#0a0a0a", "#1a1a1a", "#FFFFFF", "#34D399"),
    ("#200122", "#6f0000", "#FFFFFF", "#F87171"),
    ("#0d0d0d", "#1f1f1f", "#F3F4F6", "#818CF8"),
]


def _hex(c):
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def _gradient_image(color1, color2):
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = _hex(color1)
    r2, g2, b2 = _hex(color2)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def _wrap_text(text, font, max_width):
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


def _draw_centered_text(draw, text, y_center, font, color, max_width=WIDTH - 120, line_spacing=20):
    lines = _wrap_text(text, font, max_width)
    bbox = font.getbbox("Ag")
    line_h = bbox[3] - bbox[1] + line_spacing
    total_h = line_h * len(lines)
    y = y_center - total_h // 2
    for line in lines:
        w = font.getlength(line)
        x = (WIDTH - w) / 2
        # Drop shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 160))
        draw.text((x, y), line, font=font, fill=color)
        y += line_h
    return y


def _generate_tts(content, output_path):
    """Generate TTS MP3. Returns duration in seconds."""
    hook = content.get("hook", "")
    points = content.get("points", [])[:3]
    cta = content.get("cta", "Follow for more tips like this")

    parts = [hook] + points + [cta]
    script = ". ".join(p.rstrip(".") for p in parts if p) + "."

    gTTS(script, lang="en", slow=False).save(output_path)

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _ease_out(t):
    return 1 - (1 - t) ** 3


def make_frame(hook, main_text, points, palette_idx, alpha=1.0, show_points_count=0,
               point_reveal_pct=0.0, zoom=1.0):
    p = PALETTES[palette_idx % len(PALETTES)]
    img = _gradient_image(p[0], p[1])
    draw = ImageDraw.Draw(img)

    # Card overlay
    overlay = Image.new("RGBA", (WIDTH - 80, HEIGHT - 300), (0, 0, 0, 140))
    img.paste(overlay, (40, 150), overlay)

    font_hook = ImageFont.truetype(FONT_BOLD, 60)
    font_main = ImageFont.truetype(FONT_BOLD, 76)
    font_point = ImageFont.truetype(FONT_REGULAR, 50)
    font_small = ImageFont.truetype(FONT_REGULAR, 40)
    font_num = ImageFont.truetype(FONT_BOLD, 50)

    # Hook
    _draw_centered_text(draw, hook, 300, font_hook, p[3], max_width=WIDTH - 160)

    # Accent line
    draw.line([(160, 450), (WIDTH - 160, 450)], fill=p[3], width=4)

    # Main text
    _draw_centered_text(draw, main_text, 620, font_main, p[2], max_width=WIDTH - 100)

    # Points with numbers
    y = 870
    for i, pt in enumerate(points[:show_points_count]):
        num = f"{i + 1}."
        nw = font_num.getlength(num)
        # Number in accent color
        draw.text((120, y), num, font=font_num, fill=p[3])
        # Point text
        lines = _wrap_text(pt, font_point, WIDTH - 280)
        line_y = y
        for line in lines:
            draw.text((120 + nw + 20, line_y), line, font=font_point, fill=p[2])
            line_y += 68
        y = line_y + 16

    # Progress bar at very bottom
    bar_w = int((WIDTH - 160) * min(1.0, point_reveal_pct))
    draw.rectangle([(80, HEIGHT - 80), (WIDTH - 80, HEIGHT - 60)], fill=(255, 255, 255, 30))
    if bar_w > 0:
        draw.rectangle([(80, HEIGHT - 80), (80 + bar_w, HEIGHT - 60)], fill=p[3])

    # CTA
    cta_text = "Follow for more  👆"
    cw = font_small.getlength(cta_text)
    draw.text(((WIDTH - cw) / 2, HEIGHT - 180), cta_text, font=font_small, fill=p[3])

    # Watermark
    wm = "@socmed_auto"
    wm_w = font_small.getlength(wm)
    draw.text(((WIDTH - wm_w) / 2, HEIGHT - 120), wm, font=font_small, fill=(255, 255, 255, 100))

    # Fade in
    if alpha < 1.0:
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        img = Image.blend(black, img, alpha)

    # Subtle zoom out (starts zoomed in, slowly pulls back)
    if zoom != 1.0:
        new_w = int(WIDTH * zoom)
        new_h = int(HEIGHT * zoom)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - WIDTH) // 2
        top = (new_h - HEIGHT) // 2
        img = img.crop((left, top, left + WIDTH, top + HEIGHT))

    return img


def create_video(content, output_path, palette_idx=0, duration_secs=None):
    """Render an MP4 from content dict. Returns output_path."""
    frames_dir = Path(output_path).parent / "_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    hook = content.get("hook", "")
    main_text = content.get("on_screen_text", content.get("title", ""))
    points = content.get("points", [])[:3]

    # Generate TTS voiceover
    audio_path = str(frames_dir / "voice.mp3")
    audio_duration = _generate_tts(content, audio_path)
    total_secs = audio_duration + 1.5
    total_frames = int(total_secs * FPS)

    # Animation timeline (% of total duration):
    # 0–5%:   fade in
    # 5–30%:  hook only
    # 30–55%: hook + main text
    # 55–90%: points reveal one by one
    # 90–100%: all visible + CTA highlight
    n_points = len(points)

    for f_idx in range(total_frames):
        t = f_idx / FPS
        pct = t / total_secs

        alpha = min(1.0, _ease_out(t / (total_secs * 0.05)))
        zoom = 1.03 - 0.03 * min(1.0, t / total_secs)  # slow zoom out

        show = 0
        if pct > 0.55 and n_points > 0:
            reveal_pct = (pct - 0.55) / 0.35
            show = min(n_points, int(reveal_pct * n_points) + 1)

        progress = pct

        frame = make_frame(hook, main_text, points, palette_idx, alpha, show, progress, zoom)
        frame.save(frames_dir / f"frame_{f_idx:05d}.png")

    # Encode with FFmpeg + audio
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Cleanup frames
    for f in frames_dir.glob("*.png"):
        f.unlink()
    for f in frames_dir.glob("*.mp3"):
        f.unlink()
    frames_dir.rmdir()

    return output_path
