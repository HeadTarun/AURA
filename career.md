# Career Module

**File:** `modules/career.py`  
**Function:** `get_career_guidance(goal, completed_topics, level) -> dict`  
**Called by:** `POST /career` handler  
**Type:** Single LLM call. No RAG. No session mutation.

---

## Rules

- Single endpoint: `POST /career`
- Single LLM call per request
- No FAISS retrieval
- No session required
- Structured JSON output only

---

## Input

```python
def get_career_guidance(goal: str, completed_topics: list[str], level: str) -> dict:
```

| Param | Type | Notes |
|-------|------|-------|
| `goal` | str | Career goal e.g. `"SSC CGL"`, `"Data Analyst"` |
| `completed_topics` | list[str] | Topics already studied |
| `level` | str | Current student level |

---

## Output Schema (Career)

```json
{
  "recommended_roles": ["string"],
  "skills_required": ["string"],
  "next_steps": ["string"],
  "learning_path": ["string"],
  "estimated_time_months": 6,
  "difficulty_level": "beginner | intermediate | advanced",
  "market_demand": "low | medium | high"
}
```

All fields required.

---

## Prompt Template

```python
CAREER_PROMPT = """
You are a career counselor. A student wants to become: {goal}

Their current level: {level}
Topics they have already studied: {completed_topics}

Give them structured career guidance.

Respond ONLY with a JSON object. No explanation outside the JSON. No markdown.

JSON structure:
{{
  "recommended_roles": ["role 1", "role 2", "role 3"],
  "skills_required": ["skill 1", "skill 2", "skill 3", "skill 4"],
  "next_steps": ["action 1", "action 2", "action 3"],
  "learning_path": ["topic 1", "topic 2", "topic 3", "topic 4"],
  "estimated_time_months": <integer>,
  "difficulty_level": "beginner or intermediate or advanced",
  "market_demand": "low or medium or high"
}}
"""
```

---

## Validation

```python
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
    if data["difficulty_level"] not in ["beginner", "intermediate", "advanced"]:
        return False
    if data["market_demand"] not in ["low", "medium", "high"]:
        return False
    if not isinstance(data["estimated_time_months"], int):
        return False
    return True
```

---

## Fallback Response

```python
CAREER_FALLBACK = {
    "recommended_roles": ["Entry-level Analyst", "Junior Associate", "Trainee"],
    "skills_required": ["Communication", "Data Analysis", "Problem Solving", "Domain Knowledge"],
    "next_steps": [
        "Complete your current study plan",
        "Practice with mock tests",
        "Build a portfolio of completed topics"
    ],
    "learning_path": [
        "Strengthen fundamentals",
        "Study domain-specific topics",
        "Practice applied problems",
        "Attempt mock exams"
    ],
    "estimated_time_months": 6,
    "difficulty_level": "beginner",
    "market_demand": "medium"
}
```

---

## Full Implementation

```python
import json
import anthropic

client = anthropic.Anthropic()

def validate_career(data: dict) -> bool:
    ...  # as defined above

CAREER_FALLBACK = {...}  # as defined above

def get_career_guidance(goal: str, completed_topics: list, level: str) -> dict:
    topics_str = ", ".join(completed_topics) if completed_topics else "none yet"
    
    prompt = CAREER_PROMPT.format(
        goal=goal,
        level=level,
        completed_topics=topics_str
    )
    
    # Attempt 1
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(response.content[0].text)
        if validate_career(data):
            return data
    except Exception:
        pass
    
    # Attempt 2
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No other text."}]
        )
        data = json.loads(response.content[0].text)
        if validate_career(data):
            return data
    except Exception:
        pass
    
    return CAREER_FALLBACK
```
