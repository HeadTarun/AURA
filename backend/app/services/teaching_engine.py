<<<<<<< HEAD
# backend/app/services/teaching_engine.py

from app.services.llm_client import call_llm

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
    "concept", "explanation_in_simple", "real_world_examples",
    "key_points", "step_by_step", "common_mistakes",
    "difficulty", "estimated_time_min", "confidence_score",
]


def validate_teaching(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False
    if data.get("difficulty") not in ["beginner", "intermediate", "advanced"]:
        return False
    if not isinstance(data.get("estimated_time_min"), int):
        return False
    if not isinstance(data.get("confidence_score"), (int, float)):
        return False
    return True


def get_teaching_fallback(topic: str, level: str) -> dict:
    return {
        "concept": f"Introduction to {topic}",
        "explanation_in_simple": (
            f"{topic} is a fundamental concept. "
            "Study the provided materials for a full explanation."
        ),
        "real_world_examples": [
            "Used in daily calculations",
            "Applied in comparing quantities",
        ],
        "key_points": [
            "Understand the core definition",
            "Practice with worked examples",
            "Review key formulas",
        ],
        "step_by_step": [
            "Read the definition carefully",
            "Study one worked example",
            "Solve a practice problem",
        ],
        "common_mistakes": [
            "Confusing the formula variables",
            "Forgetting to include units",
        ],
        "difficulty": level,
        "estimated_time_min": 10,
        "confidence_score": 0.5,
    }


def generate_lesson(topic: str, level: str, context: str) -> dict:
    """
    Generate a structured lesson using Gemini (primary) or Groq (fallback).
    Context is RAG-retrieved text from rag_pipeline.retrieve().
    Returns Teaching JSON dict. Never raises an exception.
    """
    if not topic:
        return get_teaching_fallback("Unknown Topic", level)

    ctx = context if context else "No additional context available. Use your general knowledge."
    prompt = TEACHING_PROMPT.format(topic=topic, level=level, context=ctx)
    fallback = get_teaching_fallback(topic, level)

    data = call_llm(prompt, fallback, max_tokens=1024)

    if validate_teaching(data):
        return data

    return fallback
=======
# teaching_engine.py — Core teaching loop: explanation, examples, Socratic follow-ups
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
