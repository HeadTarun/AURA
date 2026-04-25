# Task 07 — Implement /career Endpoint

**Estimated time:** 45 minutes  
**Depends on:** Task 01 (project setup)

---

## Goal

Implement `modules/career.py` with `get_career_guidance(goal, completed_topics, level) -> dict`.  
Wire it into `POST /career` in `main.py`.

---

## Input to module

```python
get_career_guidance(
    goal="SSC CGL",
    completed_topics=["Ratio and Proportion", "Percentage"],
    level="beginner"
)
```

---

## Output

```json
{
  "recommended_roles": ["string", "string", "string"],
  "skills_required": ["string", "string", "string", "string"],
  "next_steps": ["string", "string", "string"],
  "learning_path": ["string", "string", "string", "string"],
  "estimated_time_months": 6,
  "difficulty_level": "beginner | intermediate | advanced",
  "market_demand": "low | medium | high"
}
```

---

## Files to Create/Modify

- `modules/career.py` — full implementation
- `main.py` — wire `POST /career`

---

## Exact Function: modules/career.py

```python
import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REQUIRED_FIELDS = [
    "recommended_roles", "skills_required", "next_steps",
    "learning_path", "estimated_time_months", "difficulty_level", "market_demand"
]

CAREER_PROMPT = """You are a career counselor helping a student in India plan their career.

Career Goal: {goal}
Current Level: {level}
Topics Already Studied: {topics}

Give structured career guidance for this specific goal.

Respond ONLY with a JSON object. No text before or after. No markdown.

Required JSON:
{{
  "recommended_roles": ["role 1", "role 2", "role 3"],
  "skills_required": ["skill 1", "skill 2", "skill 3", "skill 4"],
  "next_steps": ["concrete action 1", "concrete action 2", "concrete action 3"],
  "learning_path": ["topic to study 1", "topic 2", "topic 3", "topic 4"],
  "estimated_time_months": 6,
  "difficulty_level": "beginner",
  "market_demand": "high"
}}"""

CAREER_FALLBACK = {
    "recommended_roles": ["Entry-level Analyst", "Junior Associate", "Government Trainee"],
    "skills_required": ["Quantitative Aptitude", "Reasoning", "English Proficiency", "General Awareness"],
    "next_steps": [
        "Complete your current study plan",
        "Attempt full-length mock tests",
        "Review weak areas weekly"
    ],
    "learning_path": [
        "Strengthen arithmetic fundamentals",
        "Study domain-specific topics",
        "Practice applied problems",
        "Attempt mock exams"
    ],
    "estimated_time_months": 6,
    "difficulty_level": "beginner",
    "market_demand": "medium"
}


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
    return True


def _call_llm(prompt: str) -> dict | None:
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return None


def get_career_guidance(goal: str, completed_topics: list, level: str) -> dict:
    topics_str = ", ".join(completed_topics) if completed_topics else "none yet"
    prompt = CAREER_PROMPT.format(goal=goal, level=level, topics=topics_str)
    
    # Attempt 1
    data = _call_llm(prompt)
    if data and validate_career(data):
        return data
    
    # Attempt 2
    data = _call_llm(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No other text.")
    if data and validate_career(data):
        return data
    
    return CAREER_FALLBACK
```

---

## Wire into main.py

Replace the `POST /career` stub:

```python
from modules.career import get_career_guidance

@app.post("/career")
def career(req: CareerRequest):
    result = get_career_guidance(req.goal, req.completed_topics, req.level)
    return result
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
  "recommended_roles": ["SSC CGL Tier 1 Qualified Officer", "Income Tax Inspector", "Auditor"],
  "skills_required": ["Quantitative Aptitude", "English Language", "General Intelligence", "General Awareness"],
  "next_steps": [
    "Complete the full syllabus within your target timeline",
    "Attempt 2 full mock tests per week",
    "Focus on current affairs for last 6 months"
  ],
  "learning_path": ["Number System", "Algebra", "Geometry", "Comprehension"],
  "estimated_time_months": 6,
  "difficulty_level": "intermediate",
  "market_demand": "high"
}
```

**No session required test:**
```bash
curl -X POST http://localhost:8000/career \
  -H "Content-Type: application/json" \
  -d '{"goal": "Data Analyst"}'
```

Expected: valid Career JSON (no error even without `completed_topics`)

---

## Done When

- `POST /career` returns valid Career JSON
- Response has all 7 required fields
- `difficulty_level` is one of `beginner / intermediate / advanced`
- `market_demand` is one of `low / medium / high`
- `estimated_time_months` is an integer
- No session is required (endpoint works standalone)
- LLM failure → fallback JSON returned, no 500 error
