#!/usr/bin/env python3
"""
Socmed-Auto: Social media automation with automatic AI model routing.

Usage:
    python main.py

Set ANTHROPIC_API_KEY in your environment or a .env file.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

import anthropic

from socmed_auto.agent import run_task
from socmed_auto.model_router import list_task_types

# ---------------------------------------------------------------------------
# Example tasks – edit or extend these to suit your needs
# ---------------------------------------------------------------------------
DEMO_TASKS = [
    {
        "task_type": "hashtag_generation",          # → Haiku (simple)
        "platform": "Instagram",
        "prompt": "Generate 10 relevant hashtags for a post about sustainable fashion.",
    },
    {
        "task_type": "post_drafting",               # → Sonnet (medium)
        "platform": "LinkedIn",
        "prompt": (
            "Draft a professional post announcing our new eco-friendly product line. "
            "Highlight innovation, sustainability, and business impact."
        ),
    },
    {
        "task_type": "strategy_development",        # → Opus (complex)
        "platform": "Multi-platform",
        "prompt": (
            "Develop a 3-month social media strategy for a sustainable fashion brand "
            "targeting Gen-Z consumers. Include content pillars, posting cadence, "
            "platform mix, and KPIs."
        ),
    },
]


def run_demo(client: anthropic.Anthropic) -> None:
    print("=" * 60)
    print("Socmed-Auto  |  Automatic Model Routing Demo")
    print("=" * 60)

    for i, task in enumerate(DEMO_TASKS, 1):
        print(f"\n[Task {i}/{len(DEMO_TASKS)}]")
        print(f"  Type    : {task['task_type']}")
        print(f"  Platform: {task['platform']}")

        result, model_cfg = run_task(
            task_type=task["task_type"],
            platform=task["platform"],
            prompt=task["prompt"],
            client=client,
        )

        print(f"  Model   : {model_cfg.model_id}  ({model_cfg.description})")
        print("-" * 60)
        print(result)
        print("-" * 60)


def show_supported_tasks() -> None:
    print("\nSupported task types (grouped by model tier):\n")
    for category, tasks in list_task_types().items():
        print(f"  {category.upper()}")
        for t in sorted(tasks):
            print(f"    - {t}")
        print()


if __name__ == "__main__":
    if "--list-tasks" in sys.argv:
        show_supported_tasks()
        sys.exit(0)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set.")
        print("Add it to your environment or create a .env file with ANTHROPIC_API_KEY=...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_demo(client)
