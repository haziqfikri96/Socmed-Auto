"""Social media automation agent with automatic model routing."""

import anthropic

from .model_router import ModelConfig, get_model_for_task

SYSTEM_PROMPT = """You are an expert social media manager and content strategist.
Your job is to help create, plan, and optimize social media content.
Be concise, creative, and platform-aware. Tailor tone and format to the platform specified."""


def run_task(
    task_type: str,
    platform: str,
    prompt: str,
    *,
    client: anthropic.Anthropic | None = None,
    max_tokens: int = 1024,
    effort: str | None = None,
) -> tuple[str, ModelConfig]:
    """Run a social media task with automatic model selection.

    Returns:
        (response_text, model_config_used)
    """
    client = client or anthropic.Anthropic()
    model_cfg = get_model_for_task(task_type)

    user_message = f"Platform: {platform}\nTask: {task_type}\n\n{prompt}"

    create_kwargs: dict = dict(
        model=model_cfg.model_id,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # Apply effort only where it makes a meaningful difference (medium/complex)
    if effort is not None:
        create_kwargs["output_config"] = {"effort": effort}

    response = client.messages.create(**create_kwargs)
    text = response.content[0].text
    return text, model_cfg
