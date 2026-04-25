from typing import Any

from app.services import llm_client

VALID_LEVELS = {"beginner", "intermediate", "advanced"}

TEACHING_PROMPT = """
You are an expert tutor. Generate a structured lesson for the following topic.

Topic: {topic}
Student Level: {level}
Context (base your lesson on this material):
---
{context}
---

If the context is empty, use your general knowledge about the topic.

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON:
{{
  "concept": "one-line definition of the topic",
  "explanation_in_simple": "2-3 sentence explanation a {level} student can understand",
  "real_world_examples": ["example 1", "example 2"],
  "key_points": ["point 1", "point 2", "point 3"],
  "step_by_step": ["step 1", "step 2", "step 3"],
  "common_mistakes": ["mistake 1", "mistake 2"],
  "difficulty": "{level}",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}}
"""

REQUIRED_FIELDS = [
    "concept",
    "explanation_in_simple",
    "real_world_examples",
    "key_points",
    "step_by_step",
    "common_mistakes",
    "difficulty",
    "estimated_time_min",
    "confidence_score",
]


def normalize_level(level: str | None) -> str:
    normalized = (level or "beginner").strip().lower()
    return normalized if normalized in VALID_LEVELS else "beginner"


def validate_teaching(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if any(field not in data for field in REQUIRED_FIELDS):
        return False
    if data.get("difficulty") not in VALID_LEVELS:
        return False
    if not isinstance(data.get("estimated_time_min"), int):
        return False
    if not isinstance(data.get("confidence_score"), int | float):
        return False
    list_fields = [
        "real_world_examples",
        "key_points",
        "step_by_step",
        "common_mistakes",
    ]
    return all(isinstance(data.get(field), list) for field in list_fields)


def get_teaching_fallback(topic: str, level: str) -> dict[str, Any]:
    safe_topic = topic.strip() if topic and topic.strip() else "Unknown Topic"
    safe_level = normalize_level(level)
    return {
        "concept": f"Introduction to {safe_topic}",
        "explanation_in_simple": (
            f"{safe_topic} is an important concept. Start with the definition, "
            "then connect it to examples before solving practice questions."
        ),
        "real_world_examples": [
            "Used in everyday decision making",
            "Applied when comparing or organizing information",
        ],
        "key_points": [
            "Understand the core definition",
            "Study one clear example",
            "Practice with a small question",
        ],
        "step_by_step": [
            "Read the concept carefully",
            "Identify the important values or ideas",
            "Apply the rule to a simple example",
        ],
        "common_mistakes": [
            "Skipping the definition",
            "Applying the rule without checking the question",
        ],
        "difficulty": safe_level,
        "estimated_time_min": 10,
        "confidence_score": 0.5,
    }


def generate_lesson(topic: str, level: str, context: str = "") -> dict[str, Any]:
    safe_topic = topic.strip() if topic else ""
    safe_level = normalize_level(level)
    fallback = get_teaching_fallback(safe_topic, safe_level)
    if not safe_topic:
        return fallback

    ctx = context.strip() if context else ""
    if not ctx:
        ctx = "No additional context available. Use your general knowledge."

    try:
        data = llm_client.call_llm(
            TEACHING_PROMPT.format(topic=safe_topic, level=safe_level, context=ctx),
            fallback,
            max_tokens=1024,
        )
    except Exception:
        return fallback

    return data if validate_teaching(data) else fallback
