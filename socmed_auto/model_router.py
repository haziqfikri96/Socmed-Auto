"""
Automatic model selection based on task type and complexity.

Routing logic:
  - Haiku 5.5  → fast, cheap; ideal for simple/mechanical tasks
  - Sonnet 5.5 → balanced; ideal for drafting and planning tasks
  - Opus 5.5   → most capable; ideal for strategy and complex analysis
"""

from dataclasses import dataclass
from enum import Enum


class TaskCategory(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    category: TaskCategory
    description: str


MODELS = {
    TaskCategory.SIMPLE: ModelConfig(
        model_id="claude-haiku-5-5",
        category=TaskCategory.SIMPLE,
        description="Fast and cheap for mechanical/simple tasks",
    ),
    TaskCategory.MEDIUM: ModelConfig(
        model_id="claude-sonnet-5-5",
        category=TaskCategory.MEDIUM,
        description="Balanced for drafting and planning tasks",
    ),
    TaskCategory.COMPLEX: ModelConfig(
        model_id="claude-opus-5-5",
        category=TaskCategory.COMPLEX,
        description="Most capable for strategy and deep analysis",
    ),
}

# Map each task type to a category
TASK_TYPE_MAP: dict[str, TaskCategory] = {
    # --- Simple tasks (Haiku) ---
    "hashtag_generation": TaskCategory.SIMPLE,
    "emoji_selection": TaskCategory.SIMPLE,
    "caption_formatting": TaskCategory.SIMPLE,
    "spell_check": TaskCategory.SIMPLE,
    "url_shortening_copy": TaskCategory.SIMPLE,
    "translate_post": TaskCategory.SIMPLE,
    # --- Medium tasks (Sonnet) ---
    "post_drafting": TaskCategory.MEDIUM,
    "caption_writing": TaskCategory.MEDIUM,
    "content_repurposing": TaskCategory.MEDIUM,
    "reply_drafting": TaskCategory.MEDIUM,
    "content_calendar": TaskCategory.MEDIUM,
    "ad_copy": TaskCategory.MEDIUM,
    "bio_writing": TaskCategory.MEDIUM,
    # --- Complex tasks (Opus) ---
    "strategy_development": TaskCategory.COMPLEX,
    "audience_analysis": TaskCategory.COMPLEX,
    "competitor_analysis": TaskCategory.COMPLEX,
    "campaign_planning": TaskCategory.COMPLEX,
    "long_form_content": TaskCategory.COMPLEX,
    "crisis_response": TaskCategory.COMPLEX,
    "brand_voice_guide": TaskCategory.COMPLEX,
}


def get_model_for_task(task_type: str) -> ModelConfig:
    """Return the ModelConfig for a given task type.

    Falls back to Sonnet (medium) for unrecognised task types.
    """
    category = TASK_TYPE_MAP.get(task_type, TaskCategory.MEDIUM)
    return MODELS[category]


def list_task_types() -> dict[str, list[str]]:
    """Return all supported task types grouped by category."""
    grouped: dict[str, list[str]] = {c.value: [] for c in TaskCategory}
    for task, category in TASK_TYPE_MAP.items():
        grouped[category.value].append(task)
    return grouped
