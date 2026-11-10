"""TikTok auto-posting pipeline — generate, render, upload."""

import os
import random
import time
from datetime import datetime
from pathlib import Path

import anthropic

from ..content.generator import generate_content
from ..content.video_maker import create_video
from ..tiktok.auth import get_valid_access_token
from ..tiktok.client import upload_video

# Default niche rotation
NICHE_ROTATION = ["ai_tech", "productivity", "money"]

VIDEOS_DIR = Path("videos")


def run_post(
    niche: str | None = None,
    topic: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Generate content, render video, and post to TikTok.

    Args:
        niche: One of ai_tech, productivity, money (random if None)
        topic: Specific topic override (random from niche if None)
        dry_run: If True, skip upload and just return the video path

    Returns:
        Result dict with video_path, content, publish_id
    """
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")

    # 1. Pick niche
    chosen_niche = niche or random.choice(NICHE_ROTATION)
    print(f"[{datetime.now():%H:%M}] Niche: {chosen_niche}")

    # 2. Generate content with Claude
    ai_client = anthropic.Anthropic()
    content = generate_content(ai_client, niche=chosen_niche, topic=topic)
    print(f"[{datetime.now():%H:%M}] Topic: {content['topic']}")
    print(f"[{datetime.now():%H:%M}] Hook: {content['hook']}")

    # 3. Render video
    VIDEOS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = str(VIDEOS_DIR / f"tiktok_{timestamp}.mp4")
    palette_idx = random.randint(0, 5)
    create_video(content, video_path, palette_idx=palette_idx)
    print(f"[{datetime.now():%H:%M}] Rendered: {video_path}")

    if dry_run:
        print("[DRY RUN] Skipping upload.")
        return {"video_path": video_path, "content": content, "publish_id": None}

    # 4. Upload to TikTok
    access_token = get_valid_access_token(client_key, client_secret)
    publish_id = upload_video(
        access_token=access_token,
        video_path=video_path,
        title=content["title"],
        hashtags=content["hashtags"],
    )
    print(f"[{datetime.now():%H:%M}] Published! ID: {publish_id}")

    return {"video_path": video_path, "content": content, "publish_id": publish_id}


def run_daily_schedule(posts_per_day: int = 2) -> None:
    """Post N times per day. Spaces posts evenly (e.g. 2 posts = 9am + 7pm)."""
    import schedule

    niches = NICHE_ROTATION * posts_per_day
    times = ["09:00", "19:00", "12:00", "15:00"][:posts_per_day]

    for i, t in enumerate(times):
        niche = niches[i % len(niches)]
        schedule.every().day.at(t).do(run_post, niche=niche)
        print(f"Scheduled post at {t} ({niche})")

    print(f"\nRunning scheduler — {posts_per_day} posts/day")
    while True:
        schedule.run_pending()
        time.sleep(60)
