from typing import Any

from app.services import llm_client
from app.services.teaching_engine import normalize_level

CAREER_PROMPT = """
You are a career mentor. Create practical guidance for the learner.

Career goal: {goal}
Current level: {level}
Completed topics: {completed_topics}

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON:
{{
  "recommended_roles": ["string"],
  "skills_required": ["string"],
  "next_steps": ["string"],
  "learning_path": ["string"],
  "estimated_time_months": 6,
  "difficulty_level": "{level}",
  "market_demand": "low | medium | high"
}}
"""

REQUIRED_FIELDS = {
    "recommended_roles",
    "skills_required",
    "next_steps",
    "learning_path",
    "estimated_time_months",
    "difficulty_level",
    "market_demand",
}


def get_career_fallback(
    goal: str, completed_topics: list[str] | None, level: str
) -> dict[str, Any]:
    safe_goal = goal.strip() if goal and goal.strip() else "Career Growth"
    safe_level = normalize_level(level)
    completed = completed_topics or []
    foundation = completed[-2:] if completed else ["core fundamentals"]
    return {
        "recommended_roles": [safe_goal, f"Entry-level {safe_goal} track"],
        "skills_required": [
            "Strong fundamentals",
            "Problem solving",
            "Communication",
            "Consistent practice",
        ],
        "next_steps": [
            "Review your completed topics",
            "Practice one applied project or mock test",
            "Identify two weak areas and revise them",
        ],
        "learning_path": [
            f"Strengthen {foundation[0]}",
            "Build intermediate concepts",
            "Practice real-world problems",
            "Create a small portfolio or exam plan",
        ],
        "estimated_time_months": 6,
        "difficulty_level": safe_level,
        "market_demand": "medium",
    }


def validate_career(data: Any) -> bool:
    if not isinstance(data, dict) or not REQUIRED_FIELDS.issubset(data.keys()):
        return False
    list_fields = [
        "recommended_roles",
        "skills_required",
        "next_steps",
        "learning_path",
    ]
    if not all(isinstance(data.get(field), list) for field in list_fields):
        return False
    if data.get("difficulty_level") not in {"beginner", "intermediate", "advanced"}:
        return False
    if data.get("market_demand") not in {"low", "medium", "high"}:
        return False
    return isinstance(data.get("estimated_time_months"), int)


def generate_career_guidance(
    goal: str, completed_topics: list[str] | None = None, level: str = "beginner"
) -> dict[str, Any]:
    safe_level = normalize_level(level)
    fallback = get_career_fallback(goal, completed_topics, safe_level)

    try:
        data = llm_client.call_llm(
            CAREER_PROMPT.format(
                goal=goal,
                level=safe_level,
                completed_topics=", ".join(completed_topics or []) or "None yet",
            ),
            fallback,
            max_tokens=768,
        )
    except Exception:
        return fallback

    return data if validate_career(data) else fallback
