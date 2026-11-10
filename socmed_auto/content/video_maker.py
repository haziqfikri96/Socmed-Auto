"""
TikTok video maker — product-demo style.
Light gray bg, 2-tone kinetic text (accent verb + dark noun), floating app-UI panels.
Matches the reference: clean minimal, Apple product-promo aesthetic.
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

# (bg, text, accent) — all light-mode
PALETTES = [
    ("#E8E8E8", "#0F0F0F", "#2563EB"),
    ("#E8E8E8", "#0F0F0F", "#16A34A"),
    ("#E8E8E8", "#0F0F0F", "#D97706"),
    ("#E8E8E8", "#0F0F0F", "#7C3AED"),
    ("#E8E8E8", "#0F0F0F", "#DC2626"),
    ("#E8E8E8", "#0F0F0F", "#0891B2"),
]


def _hex(c):
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def _ease_out(t):
    t = max(0.0, min(1.0, float(t)))
    return 1 - (1 - t) ** 3


# ── App UI card panels ────────────────────────────────────────────────────────

def _shadow(w, h, r, blur=18, opacity=30):
    s = Image.new("RGBA", (w + blur * 2, h + blur * 2), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle(
        [blur, blur, w + blur, h + blur], radius=r, fill=(0, 0, 0, opacity)
    )
    return s.filter(ImageFilter.GaussianBlur(radius=blur // 2))


def _card_base(w, h, r=28):
    """White rounded card with drop shadow, returns (canvas, draw, card_img)."""
    canvas = Image.new("RGBA", (w + 36, h + 36), (0, 0, 0, 0))
    canvas.alpha_composite(_shadow(w, h, r), (0, 0))
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=r, fill=(255, 255, 255, 252)
    )
    return canvas, card


def _ios_navbar(card, draw, w, title, accent, btn_label=""):
    """Draw an iOS-style navigation bar at the top of a card."""
    ac = _hex(accent)
    # title centered
    ft = ImageFont.truetype(FONT_BOLD, 28)
    tw = ft.getlength(title)
    draw.text(((w - tw) / 2, 18), title, font=ft, fill=(20, 20, 20, 255))
    # optional right button
    if btn_label:
        fb = ImageFont.truetype(FONT_REGULAR, 26)
        bw = fb.getlength(btn_label)
        draw.text((w - bw - 20, 20), btn_label, font=fb, fill=(*ac, 230))
    # divider
    draw.line([(20, 54), (w - 20, 54)], fill=(220, 220, 220, 180), width=1)


def _stats_panel(accent):
    """Analytics panel: This Week stats with mini bar chart."""
    w, h, r = 580, 340, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    _ios_navbar(card, d, w, "This Week", accent, "See all")

    # Stat rows
    rows = [
        ("Followers", "+1,247", "↑ 18%"),
        ("Views",     "84.3K",  "↑ 32%"),
        ("Likes",     "6,891",  "↑ 24%"),
    ]
    fr = ImageFont.truetype(FONT_REGULAR, 26)
    fb = ImageFont.truetype(FONT_BOLD, 32)
    fsmall = ImageFont.truetype(FONT_REGULAR, 22)
    for i, (label, val, pct) in enumerate(rows):
        y = 70 + i * 72
        d.text((22, y), label, font=fr, fill=(110, 110, 110, 220))
        d.text((22, y + 30), val, font=fb, fill=(15, 15, 15, 255))
        pw = fsmall.getlength(pct)
        d.text((w - pw - 20, y + 34), pct, font=fsmall, fill=(*ac, 240))

    # Mini bar chart at bottom
    bar_y = 290
    heights = [60, 90, 50, 110, 75, 130, 100]
    bw, gap, br = 42, 14, 6
    total_bars = len(heights)
    bar_x = (w - (total_bars * (bw + gap) - gap)) // 2
    max_h = 115
    for i, bh in enumerate(heights):
        x0 = bar_x + i * (bw + gap)
        y0 = bar_y + max_h - int(bh * max_h / max(heights))
        col = (*ac, 220) if i == total_bars - 1 else (*ac, 80)
        d.rounded_rectangle([x0, y0, x0 + bw, bar_y + max_h], radius=br, fill=col)

    canvas.alpha_composite(card, (18, 18))
    return canvas


def _schedule_panel(accent):
    """Post scheduler panel: upcoming queue with status."""
    w, h, r = 560, 320, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    _ios_navbar(card, d, w, "Upcoming Posts", accent, "+ Add")

    posts = [
        ("10:00 AM", "AI productivity tips", "posted"),
        ("2:00 PM",  "Money mindset thread", "pending"),
        ("6:30 PM",  "Tech tools roundup",   "draft"),
    ]
    fr = ImageFont.truetype(FONT_REGULAR, 24)
    fb = ImageFont.truetype(FONT_BOLD, 24)
    fs = ImageFont.truetype(FONT_REGULAR, 20)
    for i, (time, title, status) in enumerate(posts):
        y = 68 + i * 82
        # Status dot
        dot_col = {
            "posted":  (*ac, 255),
            "pending": (255, 165, 0, 240),
            "draft":   (180, 180, 180, 220),
        }[status]
        d.ellipse([20, y + 12, 36, y + 28], fill=dot_col)
        # Content
        d.text((50, y), time, font=fs, fill=(130, 130, 130, 220))
        d.text((50, y + 24), title, font=fb, fill=(20, 20, 20, 255))
        # Status badge
        badge_colors = {"posted": (*ac, 40), "pending": (255, 165, 0, 40), "draft": (200, 200, 200, 80)}
        txt_colors   = {"posted": (*ac, 220), "pending": (200, 120, 0, 240), "draft": (140, 140, 140, 220)}
        sw = fs.getlength(status.capitalize()) + 20
        bx = w - sw - 18
        d.rounded_rectangle([bx, y + 20, bx + sw, y + 40], radius=8, fill=badge_colors[status])
        d.text((bx + 10, y + 22), status.capitalize(), font=fs, fill=txt_colors[status])
        if i < 2:
            d.line([(50, y + 72), (w - 20, y + 72)], fill=(225, 225, 225, 160), width=1)

    canvas.alpha_composite(card, (18, 18))
    return canvas


def _content_panel(accent):
    """AI content generation panel: prompt → output preview."""
    w, h, r = 600, 290, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    _ios_navbar(card, d, w, "Content AI", accent)

    # Prompt chip
    fr = ImageFont.truetype(FONT_REGULAR, 24)
    fb = ImageFont.truetype(FONT_BOLD, 24)
    prompt = "✦  Write viral TikTok script..."
    d.rounded_rectangle([18, 62, w - 18, 100], radius=10, fill=(245, 245, 245, 255))
    d.text((28, 70), prompt, font=fr, fill=(160, 160, 160, 220))

    # AI output box
    d.rounded_rectangle([18, 110, w - 18, 262], radius=14, fill=(*ac, 18))
    d.rectangle([18, 110, 22, 262], fill=(*ac, 220))  # left accent bar
    output_lines = [
        "\"Nobody told you this secret",
        "about AI automation... 🤫",
        "Here's how I went from 0 to",
        "50K followers in 30 days\"",
    ]
    fo = ImageFont.truetype(FONT_REGULAR, 23)
    for i, line in enumerate(output_lines):
        d.text((32, 118 + i * 36), line, font=fo, fill=(25, 25, 25, 240))

    canvas.alpha_composite(card, (18, 18))
    return canvas


def _account_panel(accent):
    """Account overview panel: profile stats."""
    w, h, r = 520, 240, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    # Avatar circle
    d.ellipse([22, 18, 82, 78], fill=(*ac, 230))
    fa = ImageFont.truetype(FONT_BOLD, 32)
    d.text((36, 28), "SA", font=fa, fill=(255, 255, 255, 255))

    # Handle + name
    fb = ImageFont.truetype(FONT_BOLD, 28)
    fr = ImageFont.truetype(FONT_REGULAR, 24)
    d.text((96, 20), "@socmed_auto", font=fb, fill=(15, 15, 15, 255))
    d.text((96, 52), "AI Social Media", font=fr, fill=(130, 130, 130, 220))

    # Verified badge
    bw = fr.getlength("✦ Verified") + 16
    d.rounded_rectangle([96, 82, 96 + bw, 108], radius=8, fill=(*ac, 30))
    d.text((104, 84), "✦ Verified", font=fr, fill=(*ac, 220))

    # Stat row
    d.line([(20, 120), (w - 20, 120)], fill=(220, 220, 220, 180), width=1)
    stats = [("12.4K", "Followers"), ("234", "Following"), ("892", "Posts")]
    col_w = (w - 40) // 3
    for i, (val, lbl) in enumerate(stats):
        x = 20 + i * col_w + col_w // 2
        fv = ImageFont.truetype(FONT_BOLD, 32)
        fl = ImageFont.truetype(FONT_REGULAR, 20)
        vw = fv.getlength(val)
        lw = fl.getlength(lbl)
        d.text((x - vw / 2, 132), val, font=fv, fill=(15, 15, 15, 255))
        d.text((x - lw / 2, 170), lbl, font=fl, fill=(130, 130, 130, 220))
        if i < 2:
            d.line([(20 + (i + 1) * col_w, 128), (20 + (i + 1) * col_w, 200)],
                   fill=(220, 220, 220, 150), width=1)

    canvas.alpha_composite(card, (18, 18))
    return canvas


def _todo_panel(title, items, accent):
    """Task list panel for productivity/money niches."""
    w, h, r = 520, 310, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    _ios_navbar(card, d, w, title, accent)

    fi = ImageFont.truetype(FONT_REGULAR, 26)
    fb2 = ImageFont.truetype(FONT_BOLD, 16)
    for i, item in enumerate(items[:4]):
        y = 68 + i * 58
        done = i < 2
        bx = 20
        if done:
            d.rounded_rectangle([bx, y, bx + 26, y + 26], radius=7, fill=(*ac, 240))
            d.text((bx + 4, y + 2), "✓", font=fb2, fill=(255, 255, 255, 255))
        else:
            d.rounded_rectangle([bx, y, bx + 26, y + 26], radius=7,
                                 outline=(*ac, 100), width=2)
        col = (60, 60, 60, 255) if done else (140, 140, 140, 255)
        d.text((56, y + 2), item, font=fi, fill=col)
        if i < 3:
            d.line([(56, y + 50), (w - 20, y + 50)], fill=(225, 225, 225, 150), width=1)

    canvas.alpha_composite(card, (18, 18))
    return canvas


def _finance_panel(accent):
    """Portfolio/savings panel for money niche."""
    w, h, r = 560, 290, 28
    canvas, card = _card_base(w, h, r)
    d = ImageDraw.Draw(card)
    ac = _hex(accent)

    _ios_navbar(card, d, w, "Portfolio", accent, "Details")

    # Big number
    fb = ImageFont.truetype(FONT_BOLD, 60)
    fs = ImageFont.truetype(FONT_REGULAR, 26)
    fsmall = ImageFont.truetype(FONT_REGULAR, 22)
    d.text((22, 62), "$48,250", font=fb, fill=(15, 15, 15, 255))
    d.text((22, 130), "Total Balance", font=fs, fill=(130, 130, 130, 220))
    gw = fsmall.getlength("+$1,240 (2.6%) ↑ this month")
    d.text((22, 160), "+$1,240 (2.6%) ↑ this month", font=fsmall, fill=(*ac, 240))

    # Mini sparkline
    pts = [220, 230, 215, 240, 228, 258, 245, 262, 250, 268]
    sp_x0, sp_y0, sp_w, sp_h = 22, 190, w - 44, 70
    min_p, max_p = min(pts), max(pts)
    coords = []
    for i, p in enumerate(pts):
        x = sp_x0 + int(i / (len(pts) - 1) * sp_w)
        y = sp_y0 + sp_h - int((p - min_p) / (max_p - min_p) * sp_h)
        coords.append((x, y))
    for i in range(len(coords) - 1):
        d.line([coords[i], coords[i + 1]], fill=(*ac, 220), width=3)
    d.ellipse([coords[-1][0] - 5, coords[-1][1] - 5,
               coords[-1][0] + 5, coords[-1][1] + 5], fill=(*ac, 255))

    canvas.alpha_composite(card, (18, 18))
    return canvas


CARD_BUILDERS = {
    "ai_tech": [
        lambda acc: _stats_panel(acc),
        lambda acc: _content_panel(acc),
        lambda acc: _schedule_panel(acc),
        lambda acc: _account_panel(acc),
    ],
    "productivity": [
        lambda acc: _stats_panel(acc),
        lambda acc: _todo_panel("Today's Tasks", ["Deep work block", "Inbox zero", "Review goals", "Learn 30 min"], acc),
        lambda acc: _schedule_panel(acc),
        lambda acc: _account_panel(acc),
    ],
    "money": [
        lambda acc: _finance_panel(acc),
        lambda acc: _todo_panel("Investment Plan", ["Index funds 60%", "Bonds 20%", "REITs 10%", "Cash 10%"], acc),
        lambda acc: _stats_panel(acc),
        lambda acc: _account_panel(acc),
    ],
    "default": [
        lambda acc: _stats_panel(acc),
        lambda acc: _schedule_panel(acc),
        lambda acc: _content_panel(acc),
        lambda acc: _account_panel(acc),
    ],
}


def _build_cards(niche, accent):
    """Pre-render card images + define sinusoidal floating params."""
    builders = CARD_BUILDERS.get(niche, CARD_BUILDERS["default"])
    raw = [b(accent) for b in builders]

    # (base_x, base_y, amp_x, amp_y, period_s, rotation_deg, alpha)
    layouts = [
        (-140, 180,   60,  40, 9.0,  -6, 0.75),   # upper-left
        (WIDTH - 500, 110, -50, 44, 11.0,  5, 0.72),   # upper-right
        (-150, HEIGHT - 650, 55, -44, 8.5,  4, 0.70),   # lower-left
        (WIDTH - 480, HEIGHT - 580, -60,  38, 10.0, -7, 0.74),  # lower-right
    ]
    cards = []
    for img, (bx, by, ax, ay, period, angle, alpha) in zip(raw, layouts):
        rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)
        cards.append(dict(img=rotated, bx=bx, by=by, ax=ax, ay=ay, period=period, alpha=alpha))
    return cards


def _card_xy(card, t):
    x = card["bx"] + card["ax"] * math.sin(2 * math.pi * t / card["period"])
    y = card["by"] + card["ay"] * math.cos(2 * math.pi * t / (card["period"] * 0.68))
    return int(x), int(y)


# ── Beat (kinetic text) schedule ─────────────────────────────────────────────

def _split_2tone(text):
    """Return (accent_part, normal_part).
    First word(s) = accent (action verb), rest = normal (noun).
    """
    words = text.split()
    if len(words) <= 1:
        return text, ""
    return words[0], " ".join(words[1:])


def _build_beats(content, audio_dur):
    """Return [(start_pct, end_pct, text, is_cta), …] covering 0–1."""
    hook  = content.get("hook", "")
    points = content.get("points", [])[:3]

    hw = hook.split()
    hook_chunks = [" ".join(hw[i:i + 2]) for i in range(0, len(hw), 2)]
    pt_chunks   = [" ".join(pt.split()[:4]) for pt in points]
    cta = "Follow for more"
    all_parts = hook_chunks + pt_chunks + [cta]  # noqa: F841

    n_hook = max(1, len(hook_chunks))
    n_pts  = max(1, len(pt_chunks))
    h_frac, p_frac, c_frac = 0.44, 0.42, 0.14

    beats = []
    for i, chunk in enumerate(hook_chunks):
        beats.append(((i / n_hook) * h_frac, ((i + 1) / n_hook) * h_frac, chunk, False))
    for i, chunk in enumerate(pt_chunks):
        beats.append((h_frac + (i / n_pts) * p_frac, h_frac + ((i + 1) / n_pts) * p_frac, chunk, False))
    beats.append((h_frac + p_frac, 1.0, cta, True))
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

def _pick_font_size(total_words):
    if total_words <= 1:
        return 220
    if total_words <= 2:
        return 185
    if total_words <= 3:
        return 150
    return 118


def _make_beat_layer(text, is_cta, text_hex, accent_hex):
    """RGBA full-canvas layer. 2-tone: accent verb + dark noun on same line."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)

    words = text.split()
    n     = len(words)
    ac    = _hex(accent_hex)
    tc    = _hex(text_hex)

    if is_cta:
        font = ImageFont.truetype(FONT_BOLD, 150)
        fsub = ImageFont.truetype(FONT_REGULAR, 46)
        tw   = font.getlength(text)
        bb   = font.getbbox("Ag")
        lh   = bb[3] - bb[1]
        cy   = HEIGHT // 2 - 60
        draw.text(((WIDTH - tw) / 2, cy - lh / 2), text, font=font, fill=(*ac, 255))
        sub = "for tips like this ↑"
        sw  = fsub.getlength(sub)
        draw.text(((WIDTH - sw) / 2, cy + lh / 2 + 24), sub, font=fsub,
                  fill=(*tc, 180))
        return layer

    size = _pick_font_size(n)
    font = ImageFont.truetype(FONT_BOLD, size)
    bb   = font.getbbox("Ag")
    lh   = bb[3] - bb[1] + 12

    accent_part, normal_part = _split_2tone(text)
    sp_w = font.getlength(" ")

    if n <= 1:
        # Single word centered in accent
        tw = font.getlength(text)
        cy = HEIGHT // 2
        draw.text(((WIDTH - tw) / 2, cy - lh / 2), text, font=font, fill=(*ac, 255))
        return layer

    aw = font.getlength(accent_part)
    nw = font.getlength(normal_part)
    total_w = aw + sp_w + nw
    cy = HEIGHT // 2

    if total_w <= WIDTH - 60:
        # Fits on one line: [ACCENT_VERB] [normal noun]
        x = (WIDTH - total_w) / 2
        y = cy - lh / 2
        draw.text((x, y), accent_part, font=font, fill=(*ac, 255))
        draw.text((x + aw + sp_w, y), normal_part, font=font, fill=(*tc, 255))
    else:
        # Two lines: accent on top, normal below
        y_top = cy - lh
        y_bot = cy + 6
        a_x = (WIDTH - aw) / 2
        n_x = (WIDTH - nw) / 2
        draw.text((a_x, y_top), accent_part, font=font, fill=(*ac, 255))
        draw.text((n_x, y_bot), normal_part, font=font, fill=(*tc, 255))

    return layer


def _make_vignette(bg_hex):
    rgb  = _hex(bg_hex)
    vig  = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)
    h    = 360
    for y in range(h):
        a = int(248 * (1 - y / h) ** 2.0)
        draw.line([(0, y),               (WIDTH, y)],               fill=(*rgb, a))
        draw.line([(0, HEIGHT - 1 - y),  (WIDTH, HEIGHT - 1 - y)],  fill=(*rgb, a))
    return vig


def _make_wm(text_hex):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)
    font  = ImageFont.truetype(FONT_REGULAR, 32)
    wm    = "@socmed_auto"
    w_px  = font.getlength(wm)
    draw.text(((WIDTH - w_px) / 2, HEIGHT - 52), wm, font=font,
              fill=(*_hex(text_hex), 65))
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
    hook   = content.get("hook", "")
    pts    = content.get("points", [])[:3]
    cta    = content.get("cta", "Follow for more tips like this")
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
    bg       = Image.new("RGB", (WIDTH, HEIGHT), _hex(bg_hex))
    cards    = _build_cards(niche, accent_hex)
    vignette = _make_vignette(bg_hex)
    wm_lyr   = _make_wm(text_hex)

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

        for card in cards:
            cx, cy = _card_xy(card, t)
            frame = _comp(frame, card["img"], alpha=card["alpha"], ox=cx, oy=cy)

        frame = _comp(frame, vignette)

        beat_text, is_cta, text_alpha = _get_beat(pct, beats)
        if beat_text and text_alpha > 0:
            frame = _comp(frame, beat_cache[beat_text], alpha=text_alpha)

        frame = _comp(frame, wm_lyr, alpha=0.9)

        # Fade in over first 4%
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
