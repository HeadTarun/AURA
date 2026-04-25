from typing import Any

from app.services import llm_client
from app.services.teaching_engine import VALID_LEVELS, normalize_level

QUIZ_PROMPT = """You are a quiz generator. Create one multiple-choice question.

Topic: {topic}
Student Level: {level}

Rules:
- Provide EXACTLY 4 answer options
- The answer field must be one of the 4 options, copied exactly
- Hint guides thinking without revealing the answer
- Explanation explains why the answer is correct

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON:
{{
  "question": "the question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Option B",
  "explanation": "why Option B is correct",
  "difficulty": "{level}",
  "concept_tested": "specific concept being tested",
  "hint": "a hint without revealing the answer",
  "time_limit_sec": 60
}}"""

REQUIRED_FIELDS = [
    "question",
    "options",
    "answer",
    "explanation",
    "difficulty",
    "concept_tested",
    "hint",
    "time_limit_sec",
]


def validate_quiz(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if any(field not in data for field in REQUIRED_FIELDS):
        return False
    options = data.get("options")
    if not isinstance(options, list) or len(options) != 4:
        return False
    if not all(isinstance(option, str) and option.strip() for option in options):
        return False
    if data.get("answer") not in options:
        return False
    if data.get("difficulty") not in VALID_LEVELS:
        return False
    return isinstance(data.get("time_limit_sec"), int)


def get_quiz_fallback(topic: str, level: str) -> dict[str, Any]:
    safe_topic = topic.strip() if topic and topic.strip() else "Unknown Topic"
    safe_level = normalize_level(level)
    return {
        "question": f"What is the best first step when learning {safe_topic}?",
        "options": [
            "Understand the core definition",
            "Skip directly to advanced problems",
            "Memorize unrelated facts",
            "Ignore examples and practice",
        ],
        "answer": "Understand the core definition",
        "explanation": (
            "A clear definition gives you the base needed to understand examples "
            "and solve questions correctly."
        ),
        "difficulty": safe_level,
        "concept_tested": safe_topic,
        "hint": "Think about what helps you build a strong foundation.",
        "time_limit_sec": 60,
    }


def generate_quiz(topic: str, level: str) -> dict[str, Any]:
    safe_topic = topic.strip() if topic else ""
    safe_level = normalize_level(level)
    fallback = get_quiz_fallback(safe_topic, safe_level)
    if not safe_topic:
        return fallback

    try:
        data = llm_client.call_llm(
            QUIZ_PROMPT.format(topic=safe_topic, level=safe_level),
            fallback,
            max_tokens=512,
        )
    except Exception:
        return fallback

    return data if validate_quiz(data) else fallback
