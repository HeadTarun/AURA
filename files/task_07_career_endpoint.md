# Task 07 — Implement /career Endpoint

**Estimated time:** 45 minutes  
**Depends on:** Task 01, Task 03  
**Files to create/modify:**
- `backend/app/services/career.py` ← create
- `backend/app/api/routes/career.py` ← replace stub

---

## Goal

Implement `get_career_guidance(goal, completed_topics, level) -> dict` and wire it into `POST /career`.  
No session required. No RAG. Single `call_llm` call.

---

## Step 1: Implement career.py

**File:** `backend/app/services/career.py`

```python
# backend/app/services/career.py

from backend.app.services.llm_client import call_llm

CAREER_PROMPT = """
You are a career counselor helping a student in India plan their career path.

Career Goal: {goal}
Current Student Level: {level}
Topics Already Studied: {topics}

Provide structured, actionable career guidance specific to this goal.

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON:
{{
  "recommended_roles": ["role 1", "role 2", "role 3"],
  "skills_required": ["skill 1", "skill 2", "skill 3", "skill 4"],
  "next_steps": ["concrete action 1", "concrete action 2", "concrete action 3"],
  "learning_path": ["topic to study 1", "topic 2", "topic 3", "topic 4"],
  "estimated_time_months": 6,
  "difficulty_level": "beginner",
  "market_demand": "high"
}}
"""

CAREER_FALLBACK = {
    "recommended_roles": ["Entry-level Analyst", "Junior Associate", "Government Trainee"],
    "skills_required": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "English Proficiency",
        "General Awareness"
    ],
    "next_steps": [
        "Complete your current study plan",
        "Attempt full-length mock tests weekly",
        "Review weak areas after each mock test"
    ],
    "learning_path": [
        "Strengthen arithmetic fundamentals",
        "Study domain-specific topics for the exam",
        "Practice applied problems daily",
        "Attempt mock exams under timed conditions"
    ],
    "estimated_time_months": 6,
    "difficulty_level": "beginner",
    "market_demand": "medium"
}

REQUIRED_FIELDS = [
    "recommended_roles", "skills_required", "next_steps",
    "learning_path", "estimated_time_months", "difficulty_level", "market_demand"
]


def validate_career(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False
    if data.get("difficulty_level") not in ["beginner", "intermediate", "advanced"]:
        return False
    if data.get("market_demand") not in ["low", "medium", "high"]:
        return False
    if not isinstance(data.get("estimated_time_months"), int):
        return False
    for list_field in ["recommended_roles", "skills_required", "next_steps", "learning_path"]:
        if not isinstance(data.get(list_field), list) or len(data[list_field]) == 0:
            return False
    return True


def get_career_guidance(goal: str, completed_topics: list, level: str) -> dict:
    """
    Returns Career JSON. Never raises an exception.
    Uses Gemini (primary) → Groq (fallback) → CAREER_FALLBACK.
    """
    topics_str = ", ".join(completed_topics) if completed_topics else "none yet"
    prompt = CAREER_PROMPT.format(goal=goal, level=level, topics=topics_str)

    data = call_llm(prompt, CAREER_FALLBACK, max_tokens=1024)

    if validate_career(data):
        return data

    return CAREER_FALLBACK
```

---

## Step 2: Wire POST /career

**File:** `backend/app/api/routes/career.py`

```python
# backend/app/api/routes/career.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.app.services.career import get_career_guidance

router = APIRouter()


class CareerRequest(BaseModel):
    goal: str
    completed_topics: List[str] = []
    level: str = "beginner"


@router.post("/career")
def career(req: CareerRequest):
    return get_career_guidance(req.goal, req.completed_topics, req.level)
```

---

## curl Test

```bash
curl -X POST http://localhost:8000/career \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "SSC CGL",
    "completed_topics": ["Ratio and Proportion", "Percentage"],
    "level": "beginner"
  }'
```

**Expected response shape:**
```json
{
  "recommended_roles": ["SSC CGL Officer", "Income Tax Inspector", "Auditor"],
  "skills_required": ["Quantitative Aptitude", "English Language", "General Intelligence", "General Awareness"],
  "next_steps": [
    "Complete the full syllabus within your timeline",
    "Attempt 2 full mock tests per week",
    "Focus on current affairs for the last 6 months"
  ],
  "learning_path": ["Number System", "Algebra", "Geometry", "Comprehension"],
  "estimated_time_months": 6,
  "difficulty_level": "intermediate",
  "market_demand": "high"
}
```

**Minimal request test (no completed_topics):**
```bash
curl -X POST http://localhost:8000/career \
  -H "Content-Type: application/json" \
  -d '{"goal": "Data Analyst"}'
```
**Expected:** Valid Career JSON, no error.

**Fallback test (bad API keys):**  
Expected: `CAREER_FALLBACK` dict returned, HTTP 200, no 500.

---

## Done When

- `POST /career` returns all 7 required fields
- `difficulty_level` is one of `beginner / intermediate / advanced`
- `market_demand` is one of `low / medium / high`
- `estimated_time_months` is an integer
- No session required — works standalone
- LLM failure → fallback JSON, no HTTP 500
