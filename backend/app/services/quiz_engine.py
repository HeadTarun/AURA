<<<<<<< HEAD
# backend/app/services/quiz_engine.py

from app.services.llm_client import call_llm

QUIZ_PROMPT = """You are a quiz generator. Create one multiple-choice question.

Topic: {topic}
Student Level: {level}

Rules:
- Provide EXACTLY 4 answer options
- The answer field must be one of the 4 options (copy it exactly)
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
    "question", "options", "answer", "explanation",
    "difficulty", "concept_tested", "hint", "time_limit_sec",
]


def validate_quiz(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False
    options = data.get("options", [])
    if not isinstance(options, list) or len(options) != 4:
        return False
    if data.get("answer") not in options:
        return False
    if data.get("difficulty") not in ["beginner", "intermediate", "advanced"]:
        return False
    if not isinstance(data.get("time_limit_sec"), int):
        return False
    return True


def get_quiz_fallback(topic: str, level: str) -> dict:
    return {
        "question": f"What is the primary purpose of {topic}?",
        "options": [
            "To compare two quantities by division",
            "To add numbers sequentially",
            "To measure angles in geometry",
            "To subtract values from a set",
        ],
        "answer": "To compare two quantities by division",
        "explanation": (
            f"{topic} is fundamentally about comparing quantities "
            "in a structured, mathematical way."
        ),
        "difficulty": level,
        "concept_tested": topic,
        "hint": "Think about what the word itself implies in everyday mathematics.",
        "time_limit_sec": 60,
    }


def generate_quiz(topic: str, level: str) -> dict:
    """
    Generate a single MCQ using Gemini (primary) or Groq (fallback).
    Returns a validated Quiz JSON dict. Never raises an exception.
    """
    if not topic:
        return get_quiz_fallback("Unknown Topic", level)

    prompt = QUIZ_PROMPT.format(topic=topic, level=level)
    fallback = get_quiz_fallback(topic, level)

    data = call_llm(prompt, fallback, max_tokens=512)

    if validate_quiz(data):
        return data

    return fallback
=======
# quiz_engine.py — Quiz generation, evaluation and feedback
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
