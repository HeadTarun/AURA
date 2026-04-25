# Task 04 — Implement Teaching Engine

**Estimated time:** 1 hour  
**Depends on:** Task 01, Task 02, Task 03  
**Files to create/modify:**
- `backend/app/services/teaching_engine.py` ← create
- `backend/app/api/routes/learn.py` ← replace stub

---

## Goal

Implement `generate_lesson(topic, level, context) -> dict` and wire it into `POST /learn`.  
RAG context comes from `vector_db/rag_pipeline.retrieve()` — already verified in Task 03.

---

## Step 1: Implement teaching_engine.py

**File:** `backend/app/services/teaching_engine.py`

```python
# backend/app/services/teaching_engine.py

from backend.app.services.llm_client import call_llm

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
    "difficulty", "estimated_time_min", "confidence_score"
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
            "Applied in comparing quantities"
        ],
        "key_points": [
            "Understand the core definition",
            "Practice with worked examples",
            "Review key formulas"
        ],
        "step_by_step": [
            "Read the definition carefully",
            "Study one worked example",
            "Solve a practice problem"
        ],
        "common_mistakes": [
            "Confusing the formula variables",
            "Forgetting to include units"
        ],
        "difficulty": level,
        "estimated_time_min": 10,
        "confidence_score": 0.5
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
```

---

## Step 2: Wire POST /learn

**File:** `backend/app/api/routes/learn.py`

```python
# backend/app/api/routes/learn.py

from fastapi import APIRouter
from pydantic import BaseModel
from vector_db.rag_pipeline import retrieve
from backend.app.services.teaching_engine import generate_lesson
from backend.app.services.session_store import load_session, save_session

router = APIRouter()


class LearnRequest(BaseModel):
    student_id: str
    topic: str
    level: str = "beginner"


@router.post("/learn")
def learn(req: LearnRequest):
    session = load_session(req.student_id)

    # RAG retrieval — reuse existing pipeline
    try:
        chunks = retrieve(req.topic, top_k=3)
    except Exception:
        chunks = []
    context = "\n\n".join(chunks)

    # Teaching engine
    result = generate_lesson(req.topic, req.level, context)

    # Update session
    session["current_topic"] = req.topic
    session["level"] = req.level
    save_session(session)

    return result
```

---

## curl Test

```bash
export GEMINI_API_KEY=your_key
export GROQ_API_KEY=your_key

curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001",
    "topic": "Ratio and Proportion",
    "level": "beginner"
  }'
```

**Expected response shape:**
```json
{
  "concept": "A ratio compares two quantities by division...",
  "explanation_in_simple": "...",
  "real_world_examples": ["...", "..."],
  "key_points": ["...", "...", "..."],
  "step_by_step": ["...", "...", "..."],
  "common_mistakes": ["...", "..."],
  "difficulty": "beginner",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}
```

**Fallback test (invalid API key):**
```bash
GEMINI_API_KEY=invalid GROQ_API_KEY=invalid \
  curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "topic": "Percentage", "level": "beginner"}'
```
**Expected:** Fallback JSON with `"confidence_score": 0.5` — no HTTP 500.

---

## Done When

- `POST /learn` returns all 9 required fields
- `sessions/student_001.json` has `current_topic = "Ratio and Proportion"`
- RAG context is passed when available
- Both API keys invalid → fallback JSON returned (HTTP 200, not 500)
