from typing import Any

from app.services import llm_client

VALID_LEVELS = {"beginner", "intermediate", "advanced"}

TEACHING_PROMPT = """
You are an expert tutor. Generate a structured tab-based lesson for the following topic.

Topic: {topic}
Student Level: {level}
Context (base your lesson on this material):
---
{context}
---

If the context is empty, use your general knowledge about the topic.

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON (include ALL fields exactly as shown):
{{
  "concept": "one-line definition of the topic",
  "explanation_in_simple": "2-3 sentence explanation a {level} student can understand",
  "real_world_examples": ["example 1", "example 2"],
  "key_points": ["point 1", "point 2", "point 3"],
  "step_by_step": ["step 1", "step 2", "step 3"],
  "common_mistakes": ["mistake 1", "mistake 2"],
  "difficulty": "{level}",
  "estimated_time_min": 10,
  "confidence_score": 0.85,
  "tabs": [
    {{
      "title": "Overview",
      "content": "Write a clear 3-4 sentence overview of {topic} for a {level} student."
    }},
    {{
      "title": "Key Concepts",
      "content": "Explain the 3 most important concepts and ideas about {topic} in 3-5 sentences."
    }},
    {{
      "title": "Examples",
      "content": "Provide 2 concrete real-world examples that clearly illustrate {topic}."
    }},
    {{
      "title": "Step-by-Step",
      "content": "Describe a step-by-step approach to understanding or applying {topic}, with 3-4 steps."
    }},
    {{
      "title": "Common Mistakes",
      "content": "Describe 2-3 common mistakes {level} students make with {topic} and how to avoid them."
    }},
    {{
      "title": "Quiz",
      "content": "__quiz__"
    }}
  ]
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
    "tabs",
]


def normalize_level(level: str | None) -> str:
    normalized = (level or "beginner").strip().lower()
    return normalized if normalized in VALID_LEVELS else "beginner"


def _build_fallback_tabs(topic: str, level: str) -> list[dict[str, str]]:
    return [
        {
            "title": "Overview",
            "content": (
                f"{topic} is a fundamental concept worth understanding at the {level} level. "
                "Start by reading the definition carefully before moving to examples. "
                "Building a solid foundation here will make advanced topics much easier."
            ),
        },
        {
            "title": "Key Concepts",
            "content": (
                "The core idea is to understand the definition first. "
                "Next, connect that definition to a concrete example you can visualise. "
                "Finally, identify the rules or steps that make this concept work in practice."
            ),
        },
        {
            "title": "Examples",
            "content": (
                "Example 1: Used in everyday decision-making to compare or rank options. "
                "Example 2: Applied when organising or retrieving information efficiently."
            ),
        },
        {
            "title": "Step-by-Step",
            "content": (
                "Step 1: Read the concept carefully and note the key terms. "
                "Step 2: Identify the important values or ideas in the problem. "
                "Step 3: Apply the rule to a simple example to verify understanding. "
                "Step 4: Try a slightly harder variation on your own."
            ),
        },
        {
            "title": "Common Mistakes",
            "content": (
                "Mistake 1: Skipping the definition and jumping straight to practice. "
                "Mistake 2: Applying rules without carefully reading the question first. "
                "Mistake 3: Memorising steps without understanding why they work."
            ),
        },
        {
            "title": "Quiz",
            "content": "__quiz__",
        },
    ]


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
    if not all(isinstance(data.get(field), list) for field in list_fields):
        return False
    tabs = data.get("tabs")
    if not isinstance(tabs, list) or len(tabs) < 2:
        return False
    return all(
        isinstance(t, dict) and "title" in t and "content" in t for t in tabs
    )


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
        "tabs": _build_fallback_tabs(safe_topic, safe_level),
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

    prompt = TEACHING_PROMPT.format(topic=safe_topic, level=safe_level, context=ctx)

    # First attempt
    try:
        data = llm_client.call_llm(prompt, fallback, max_tokens=2048)
    except Exception:
        return fallback

    if validate_teaching(data):
        return data

    # Retry once on invalid / incomplete response
    try:
        data = llm_client.call_llm(prompt, fallback, max_tokens=2048)
    except Exception:
        return fallback

    return data if validate_teaching(data) else fallback