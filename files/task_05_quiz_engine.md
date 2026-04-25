# Task 05 — Implement Quiz Engine

**Estimated time:** 1 hour  
**Depends on:** Task 01, Task 02, Task 03  
**Files to create/modify:**
- `backend/app/services/quiz_engine.py` ← create
- `backend/app/api/routes/quiz.py` ← replace stub

---

## Goal

Implement `generate_quiz(topic, level) -> dict` and wire it into `POST /quiz`.

---

## Step 1: Implement quiz_engine.py

**File:** `backend/app/services/quiz_engine.py`

```python
# backend/app/services/quiz_engine.py

from backend.app.services.llm_client import call_llm

QUIZ_PROMPT = """
You are a quiz generator. Create exactly one multiple-choice question.

Topic: {topic}
Student Level: {level}

Rules:
- Provide EXACTLY 4 answer options
- The "answer" field must be copied exactly from one of the 4 options (exact string match)
- Hint must guide thinking without revealing the answer
- Explanation must explain WHY the answer is correct

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
}}
"""

REQUIRED_FIELDS = [
    "question", "options", "answer", "explanation",
    "difficulty", "concept_tested", "hint", "time_limit_sec"
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
            "To subtract values from a set"
        ],
        "answer": "To compare two quantities by division",
        "explanation": f"{topic} is fundamentally about comparing quantities in a structured way.",
        "difficulty": level,
        "concept_tested": topic,
        "hint": "Think about what the concept name implies in everyday mathematics.",
        "time_limit_sec": 60
    }


def generate_quiz(topic: str, level: str) -> dict:
    """
    Generate one MCQ using Gemini (primary) or Groq (fallback).
    Returns Quiz JSON dict. Never raises an exception.
    """
    if not topic:
        return get_quiz_fallback("General Mathematics", level)

    prompt = QUIZ_PROMPT.format(topic=topic, level=level)
    fallback = get_quiz_fallback(topic, level)

    data = call_llm(prompt, fallback, max_tokens=512)

    if validate_quiz(data):
        return data

    return fallback
```

---

## Step 2: Wire POST /quiz

**File:** `backend/app/api/routes/quiz.py`

```python
# backend/app/api/routes/quiz.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.quiz_engine import generate_quiz
from backend.app.services.session_store import load_session, save_session

router = APIRouter()


class QuizRequest(BaseModel):
    student_id: str


@router.post("/quiz")
def quiz(req: QuizRequest):
    session = load_session(req.student_id)

    if not session.get("current_topic"):
        raise HTTPException(
            status_code=404,
            detail={"error": "session_not_found", "message": "Call /learn first to start a session"}
        )

    result = generate_quiz(session["current_topic"], session["level"])

    session["pending_quiz"] = result
    save_session(session)

    return result
```

---

## curl Test

```bash
# Step 1: Start session
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001", "topic": "Ratio and Proportion", "level": "beginner"}'

# Step 2: Get quiz
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001"}'
```

**Expected response shape:**
```json
{
  "question": "If A:B = 3:5 and A = 12, what is B?",
  "options": ["15", "20", "18", "25"],
  "answer": "20",
  "explanation": "Since A:B = 3:5 and A=12, B = 12 × (5/3) = 20",
  "difficulty": "beginner",
  "concept_tested": "Ratio calculation",
  "hint": "Use cross multiplication to find the missing value",
  "time_limit_sec": 60
}
```

**Error test (no prior /learn):**
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "brand_new_student"}'
```
**Expected:** HTTP 404 `{"error": "session_not_found", "message": "Call /learn first to start a session"}`

---

## Done When

- `POST /quiz` returns all 8 required fields
- `options` has exactly 4 items
- `answer` is one of the 4 options (exact string)
- `sessions/student_001.json` has `pending_quiz` populated
- No prior `/learn` → HTTP 404 with correct error body
- Fallback quiz returned when both LLMs fail (no HTTP 500)
