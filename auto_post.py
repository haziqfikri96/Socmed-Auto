#!/usr/bin/env python3
"""
Socmed-Auto: TikTok Auto-Poster

Usage:
    python auto_post.py                     # Post once now (random niche)
    python auto_post.py --niche ai_tech     # Post with specific niche
    python auto_post.py --dry-run           # Generate video only, no upload
    python auto_post.py --schedule          # Run daily scheduler (2 posts/day)
    python auto_post.py --schedule 3        # Run daily scheduler (3 posts/day)

Niches available: ai_tech, productivity, money
"""

import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from socmed_auto.scheduler.pipeline import run_daily_schedule, run_post


def main():
    parser = argparse.ArgumentParser(description="TikTok Auto-Poster")
    parser.add_argument("--niche", choices=["ai_tech", "productivity", "money"])
    parser.add_argument("--topic", type=str, help="Custom topic override")
    parser.add_argument("--dry-run", action="store_true", help="Generate video only, skip upload")
    parser.add_argument("--schedule", nargs="?", const=2, type=int, metavar="N",
                        help="Run daily scheduler with N posts per day (default 2)")
    args = parser.parse_args()

    if args.schedule:
        run_daily_schedule(posts_per_day=args.schedule)
        return

    result = run_post(
        niche=args.niche,
        topic=args.topic,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 50)
    if args.dry_run:
        print(f"Video saved: {result['video_path']}")
        print(f"Title: {result['content']['title']}")
        print(f"Hashtags: {' '.join('#' + t for t in result['content']['hashtags'][:8])}")
    else:
        print(f"Posted to TikTok! Publish ID: {result['publish_id']}")
        print(f"Title: {result['content']['title']}")


if __name__ == "__main__":
    main()
