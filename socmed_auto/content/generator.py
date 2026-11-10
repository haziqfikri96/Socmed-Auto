"""AI-powered TikTok content generation using Claude."""

import json
import random

import anthropic

NICHES = {
    "ai_tech": {
        "topics": [
            "AI tools that save you hours",
            "ChatGPT prompts that actually work",
            "Free AI tools most people don't know about",
            "How AI is changing jobs in 2025",
            "Python tricks every developer should know",
            "Tools to automate your workflow",
        ],
        "hashtags": [
            "AI", "AITools", "Tech", "ChatGPT", "MachineLearning",
            "TechTips", "Automation", "FutureOfWork", "Coding", "Python",
        ],
        "tone": "informative and slightly mind-blowing — like sharing a secret",
    },
    "productivity": {
        "topics": [
            "Morning routines of successful people",
            "One habit that changes everything",
            "Stop wasting time on these things",
            "The 2-minute rule for procrastination",
            "How to focus in a distracted world",
            "Apps that make you 10x more productive",
        ],
        "hashtags": [
            "Productivity", "LifeHacks", "MorningRoutine", "Success",
            "Mindset", "SelfImprovement", "TimeManagement", "GrowthMindset",
        ],
        "tone": "motivating and direct — like a friend giving honest advice",
    },
    "money": {
        "topics": [
            "Side hustles that actually make money",
            "What nobody tells you about saving",
            "How to start investing with $100",
            "Passive income myths vs reality",
            "Financial habits before you turn 30",
            "Apps that pay you to do simple tasks",
        ],
        "hashtags": [
            "Finance", "MoneyTips", "Investing", "SideHustle", "PassiveIncome",
            "FinancialFreedom", "MoneyMindset", "WealthBuilding",
        ],
        "tone": "straightforward and empowering — no fluff",
    },
}


def generate_content(
    client: anthropic.Anthropic,
    niche: str = "ai_tech",
    topic: str | None = None,
) -> dict:
    """Generate a TikTok script + metadata. Returns dict with title, script, hashtags."""
    cfg = NICHES.get(niche, NICHES["ai_tech"])
    chosen_topic = topic or random.choice(cfg["topics"])

    prompt = f"""Create a TikTok video script for this topic: "{chosen_topic}"

Niche: {niche}
Tone: {cfg["tone"]}

Requirements:
- Hook in first 2 seconds (a bold statement or question)
- 3-5 punchy points (max 15 words each)
- Clear call to action at end ("Follow for more tips like this")
- Total spoken duration: 20-30 seconds
- NO copyrighted references, music cues, or brand names
- Safe for all audiences (TikTok Community Guidelines compliant)

Return JSON only:
{{
  "title": "Short catchy title for the video caption (max 100 chars)",
  "hook": "Opening line (spoken in first 2 seconds)",
  "points": ["point 1", "point 2", "point 3"],
  "cta": "Call to action line",
  "on_screen_text": "Main text to show on screen (max 60 chars, the key message)",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

    resp = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    content = json.loads(raw.strip())

    # Merge in niche hashtags
    all_tags = list(dict.fromkeys(content.get("hashtags", []) + cfg["hashtags"]))
    content["hashtags"] = all_tags[:20]
    content["niche"] = niche
    content["topic"] = chosen_topic
    return content
