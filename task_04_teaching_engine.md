# Task 04 — Implement Teaching Engine

**Estimated time:** 60 minutes  
**Depends on:** Task 01 (project setup)

---

## Goal

Implement `engines/teaching_engine.py` with `generate_lesson(topic, level, context) -> dict`.  
Wire it into the `POST /learn` route in `main.py`.

---

## Input to engine

```python
generate_lesson(topic="Ratio and Proportion", level="beginner", context="...retrieved text...")
```

---

## Output from engine

```json
{
  "concept": "string",
  "explanation_in_simple": "string",
  "real_world_examples": ["string", "string"],
  "key_points": ["string", "string", "string"],
  "step_by_step": ["string", "string", "string"],
  "common_mistakes": ["string", "string"],
  "difficulty": "beginner",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}
```

---

## Files to Modify

- `engines/teaching_engine.py` — full implementation
- `main.py` — wire the `POST /learn` route

---

## Exact Function: engines/teaching_engine.py

```python
import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

REQUIRED_FIELDS = [
    "concept", "explanation_in_simple", "real_world_examples",
    "key_points", "step_by_step", "common_mistakes",
    "difficulty", "estimated_time_min", "confidence_score"
]

TEACHING_PROMPT = """You are an expert tutor. Generate a structured lesson for the topic below.

Topic: {topic}
Student Level: {level}
Context (base your lesson on this):
---
{context}
---

Respond ONLY with a JSON object. No text before or after. No markdown backticks.

Required JSON:
{{
  "concept": "one-line definition",
  "explanation_in_simple": "2-3 sentence simple explanation",
  "real_world_examples": ["example 1", "example 2"],
  "key_points": ["point 1", "point 2", "point 3"],
  "step_by_step": ["step 1", "step 2", "step 3"],
  "common_mistakes": ["mistake 1", "mistake 2"],
  "difficulty": "{level}",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}}"""


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


def get_fallback(topic: str, level: str) -> dict:
    return {
        "concept": f"Introduction to {topic}",
        "explanation_in_simple": f"{topic} is a fundamental concept. Study the provided materials for a full explanation.",
        "real_world_examples": ["Used in daily calculations", "Applied in comparing quantities"],
        "key_points": ["Understand the definition", "Practice with examples", "Review formulas"],
        "step_by_step": ["Read the definition", "Study one example", "Solve a practice problem"],
        "common_mistakes": ["Confusing the formula", "Forgetting units"],
        "difficulty": level,
        "estimated_time_min": 10,
        "confidence_score": 0.5
    }


def _call_llm(prompt: str) -> dict | None:
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return None


def generate_lesson(topic: str, level: str, context: str) -> dict:
    ctx = context if context else "No additional context available."
    prompt = TEACHING_PROMPT.format(topic=topic, level=level, context=ctx)
    
    # Attempt 1
    data = _call_llm(prompt)
    if data and validate_teaching(data):
        return data
    
    # Attempt 2 — reinforce JSON instruction
    data = _call_llm(prompt + "\n\nIMPORTANT: Your entire response must be a single valid JSON object only.")
    if data and validate_teaching(data):
        return data
    
    # Fallback
    return get_fallback(topic, level)
```

---

## Wire into main.py

Replace the `POST /learn` stub:

```python
from engines.teaching_engine import generate_lesson

@app.post("/learn")
def learn(req: LearnRequest):
    session = load_session(req.student_id)
    
    # Retrieve context (requires Task 03)
    # If FAISS not ready, pass empty string
    chunks = faiss_search(req.topic) if FAISS_INDEX else []
    context = "\n\n".join(chunks)
    
    # Call teaching engine
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
export ANTHROPIC_API_KEY=your_key_here

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

---

## Done When

- `POST /learn` returns valid Teaching JSON (not stub)
- Response contains all 9 required fields
- `sessions/student_001.json` exists and has `current_topic = "Ratio and Proportion"`
- If ANTHROPIC_API_KEY is wrong → fallback JSON is returned (no 500 error)
