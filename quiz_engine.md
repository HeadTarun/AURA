# Quiz Engine

**File:** `engines/quiz_engine.py`  
**Function:** `generate_quiz(topic, level) -> dict`  
**Called by:** `POST /quiz` handler  
**Returns:** Quiz JSON (strict schema)

---

## Responsibility

1. Receive current topic and student level
2. Build prompt to generate one quiz question
3. Call LLM → force JSON output
4. Validate response against Quiz schema
5. Retry once if invalid
6. Return fallback if still invalid

---

## Input

```python
def generate_quiz(topic: str, level: str) -> dict:
```

| Param | Type | Notes |
|-------|------|-------|
| `topic` | str | e.g. `"Ratio and Proportion"` — from `session.current_topic` |
| `level` | str | `"beginner"`, `"intermediate"`, or `"advanced"` |

---

## Output Schema (Quiz)

```json
{
  "question": "string",
  "options": ["string", "string", "string", "string"],
  "answer": "string",
  "explanation": "string",
  "difficulty": "beginner | intermediate | advanced",
  "concept_tested": "string",
  "hint": "string",
  "time_limit_sec": 60
}
```

All fields required. `options` must have exactly 4 items. `answer` must be one of the options exactly.

---

## Prompt Template

```python
QUIZ_PROMPT = """
You are a quiz generator. Create one multiple-choice question on the topic below.

Topic: {topic}
Student Level: {level}

Rules:
- Question must be clear and unambiguous
- Provide exactly 4 options
- Answer must be one of the 4 options (exact string match)
- Provide a one-sentence hint that guides thinking without revealing the answer
- Explanation must explain WHY the answer is correct

Respond ONLY with a JSON object. No explanation outside the JSON. No markdown.

JSON structure:
{{
  "question": "the question text",
  "options": ["option A", "option B", "option C", "option D"],
  "answer": "the correct option (must match one of the options exactly)",
  "explanation": "why this answer is correct",
  "difficulty": "{level}",
  "concept_tested": "the specific concept this question tests",
  "hint": "a hint to guide the student without giving the answer",
  "time_limit_sec": 60
}}
"""
```

---

## Validation

```python
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
    if not isinstance(data["options"], list) or len(data["options"]) != 4:
        return False
    if data["answer"] not in data["options"]:
        return False
    if data["difficulty"] not in ["beginner", "intermediate", "advanced"]:
        return False
    return True
```

---

## Fallback Response

```python
def get_quiz_fallback(topic: str, level: str) -> dict:
    return {
        "question": f"Which of the following best describes {topic}?",
        "options": [
            "A method of comparing two quantities",
            "A way to add numbers together",
            "A technique for measuring angles",
            "A process of subtracting values"
        ],
        "answer": "A method of comparing two quantities",
        "explanation": f"{topic} is fundamentally about comparing quantities in a structured way.",
        "difficulty": level,
        "concept_tested": topic,
        "hint": "Think about what the word itself means in everyday usage.",
        "time_limit_sec": 60
    }
```

---

## Full Implementation

```python
import json
import anthropic

client = anthropic.Anthropic()

def validate_quiz(data: dict) -> bool:
    ...  # as defined above

def get_quiz_fallback(topic: str, level: str) -> dict:
    ...  # as defined above

def generate_quiz(topic: str, level: str) -> dict:
    prompt = QUIZ_PROMPT.format(topic=topic, level=level)
    
    # Attempt 1
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(response.content[0].text)
        if validate_quiz(data):
            return data
    except Exception:
        pass
    
    # Attempt 2
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No other text."}]
        )
        data = json.loads(response.content[0].text)
        if validate_quiz(data):
            return data
    except Exception:
        pass
    
    # Fallback
    return get_quiz_fallback(topic, level)
```

---

## Answer Evaluation

Answer evaluation is NOT in the quiz engine. It happens in the `/evaluate` route handler as a pure comparison:

```python
# In main.py POST /evaluate handler:
correct = (student_answer.strip().lower() == session["pending_quiz"]["answer"].strip().lower())
```

This is intentional — no LLM is used for MCQ evaluation. It is a deterministic string comparison.
