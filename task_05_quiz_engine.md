# Task 05 — Implement Quiz Engine

**Estimated time:** 60 minutes  
**Depends on:** Task 01, Task 02

---

## Goal

Implement `engines/quiz_engine.py` with `generate_quiz(topic, level) -> dict`.  
Wire it into the `POST /quiz` route in `main.py`.

---

## Input to engine

```python
generate_quiz(topic="Ratio and Proportion", level="beginner")
```

---

## Output from engine

```json
{
  "question": "string",
  "options": ["string", "string", "string", "string"],
  "answer": "string",
  "explanation": "string",
  "difficulty": "beginner",
  "concept_tested": "string",
  "hint": "string",
  "time_limit_sec": 60
}
```

`answer` MUST be one of the 4 options exactly (string match).

---

## Files to Modify

- `engines/quiz_engine.py` — full implementation
- `main.py` — wire the `POST /quiz` route

---

## Exact Function: engines/quiz_engine.py

```python
import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REQUIRED_FIELDS = [
    "question", "options", "answer", "explanation",
    "difficulty", "concept_tested", "hint", "time_limit_sec"
]

QUIZ_PROMPT = """You are a quiz generator. Create one multiple-choice question.

Topic: {topic}
Student Level: {level}

Rules:
- Provide EXACTLY 4 answer options
- The answer field must be one of the 4 options (copy it exactly)
- Hint guides thinking without revealing the answer
- Explanation explains why the answer is correct

Respond ONLY with a JSON object. No text before or after. No markdown.

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
    return True


def get_fallback(topic: str, level: str) -> dict:
    return {
        "question": f"What is the primary purpose of {topic}?",
        "options": [
            "To compare two quantities by division",
            "To add numbers sequentially",
            "To measure angles in geometry",
            "To subtract values from a set"
        ],
        "answer": "To compare two quantities by division",
        "explanation": f"{topic} is fundamentally about comparing quantities in a structured, mathematical way.",
        "difficulty": level,
        "concept_tested": topic,
        "hint": "Think about what the word itself implies in everyday mathematics.",
        "time_limit_sec": 60
    }


def _call_llm(prompt: str) -> dict | None:
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
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


def generate_quiz(topic: str, level: str) -> dict:
    prompt = QUIZ_PROMPT.format(topic=topic, level=level)
    
    # Attempt 1
    data = _call_llm(prompt)
    if data and validate_quiz(data):
        return data
    
    # Attempt 2
    data = _call_llm(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. The answer field must exactly match one of the 4 options.")
    if data and validate_quiz(data):
        return data
    
    return get_fallback(topic, level)
```

---

## Wire into main.py

Replace the `POST /quiz` stub:

```python
from engines.quiz_engine import generate_quiz

@app.post("/quiz")
def quiz(req: QuizRequest):
    session = load_session(req.student_id)
    
    if not session.get("current_topic"):
        raise HTTPException(
            status_code=404,
            detail={"error": "session_not_found", "message": "Call /learn first to start a session"}
        )
    
    result = generate_quiz(session["current_topic"], session["level"])
    
    # Store in session for evaluation
    session["pending_quiz"] = result
    save_session(session)
    
    return result
```

---

## curl Test

First call `/learn`, then call `/quiz`:

```bash
# Step 1: Start a session
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001", "topic": "Ratio and Proportion", "level": "beginner"}'

# Step 2: Get a quiz
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

**Error test (no session):**
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "no_session_yet"}'
```
**Expected:** HTTP 404 with `{"error": "session_not_found", ...}`

---

## Done When

- `POST /quiz` returns valid Quiz JSON
- Response has all 8 required fields
- `options` has exactly 4 items
- `answer` is one of the options (exact string)
- `sessions/student_001.json` has `pending_quiz` populated
- Calling `/quiz` without prior `/learn` returns HTTP 404
