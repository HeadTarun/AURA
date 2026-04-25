# Teaching Engine

**File:** `engines/teaching_engine.py`  
**Function:** `generate_lesson(topic, level, context) -> dict`  
**Called by:** `POST /learn` handler  
**Returns:** Teaching JSON (strict schema)

---

## Responsibility

1. Receive topic, level, and RAG context (retrieved chunks)
2. Build a structured prompt
3. Call LLM → force JSON output
4. Validate response against Teaching schema
5. Retry once if invalid
6. Return fallback if still invalid

---

## Input

```python
def generate_lesson(topic: str, level: str, context: str) -> dict:
```

| Param | Type | Notes |
|-------|------|-------|
| `topic` | str | e.g. `"Ratio and Proportion"` |
| `level` | str | `"beginner"`, `"intermediate"`, or `"advanced"` |
| `context` | str | Retrieved FAISS chunks joined as plain text. May be empty string if retrieval failed. |

---

## Output Schema (Teaching)

```json
{
  "concept": "string",
  "explanation_in_simple": "string",
  "real_world_examples": ["string", "string"],
  "key_points": ["string", "string", "string"],
  "step_by_step": ["string", "string", "string"],
  "common_mistakes": ["string", "string"],
  "difficulty": "beginner | intermediate | advanced",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}
```

All fields are required. No additional properties.

---

## Prompt Template

```python
TEACHING_PROMPT = """
You are an expert tutor. Generate a structured lesson for the following topic.

Topic: {topic}
Student Level: {level}
Context (use this as the primary source):
---
{context}
---

Respond ONLY with a JSON object. No explanation outside the JSON. No markdown.

JSON structure:
{{
  "concept": "one-line definition of the topic",
  "explanation_in_simple": "2-3 sentence explanation a beginner can understand",
  "real_world_examples": ["example 1", "example 2"],
  "key_points": ["point 1", "point 2", "point 3"],
  "step_by_step": ["step 1", "step 2", "step 3"],
  "common_mistakes": ["mistake 1", "mistake 2"],
  "difficulty": "{level}",
  "estimated_time_min": <integer between 5 and 30>,
  "confidence_score": <float between 0.0 and 1.0>
}}
"""
```

---

## Validation

```python
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
    if data["difficulty"] not in ["beginner", "intermediate", "advanced"]:
        return False
    if not isinstance(data["estimated_time_min"], int):
        return False
    if not isinstance(data["confidence_score"], (int, float)):
        return False
    return True
```

---

## Fallback Response

Returned if LLM fails after retry:

```python
TEACHING_FALLBACK = {
    "concept": f"Introduction to {topic}",
    "explanation_in_simple": "This is a fundamental concept. Please review your study materials for a detailed explanation.",
    "real_world_examples": ["Example 1: Apply this in daily calculations", "Example 2: Used in comparing quantities"],
    "key_points": ["Understand the definition", "Practice with examples", "Review common formulas"],
    "step_by_step": ["Step 1: Read the definition", "Step 2: Study one example", "Step 3: Try a practice problem"],
    "common_mistakes": ["Confusing the formula", "Skipping units"],
    "difficulty": level,
    "estimated_time_min": 10,
    "confidence_score": 0.5
}
```

Note: `topic` and `level` must be substituted at runtime.

---

## Full Implementation

```python
import json
import anthropic

client = anthropic.Anthropic()

TEACHING_PROMPT = """..."""  # as defined above

REQUIRED_FIELDS = [...]  # as defined above

def validate_teaching(data: dict) -> bool:
    ...  # as defined above

def generate_lesson(topic: str, level: str, context: str) -> dict:
    prompt = TEACHING_PROMPT.format(topic=topic, level=level, context=context or "No context available.")
    
    fallback = {
        "concept": f"Introduction to {topic}",
        "explanation_in_simple": "This is a fundamental concept. Please review your study materials.",
        "real_world_examples": ["Used in daily calculations", "Used in comparing quantities"],
        "key_points": ["Understand the definition", "Practice examples", "Review formulas"],
        "step_by_step": ["Read the definition", "Study one example", "Try a practice problem"],
        "common_mistakes": ["Confusing the formula", "Skipping units"],
        "difficulty": level,
        "estimated_time_min": 10,
        "confidence_score": 0.5
    }
    
    # Attempt 1
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(response.content[0].text)
        if validate_teaching(data):
            return data
    except Exception:
        pass
    
    # Attempt 2 (retry with stronger instruction)
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No other text."}]
        )
        data = json.loads(response.content[0].text)
        if validate_teaching(data):
            return data
    except Exception:
        pass
    
    # Fallback
    return fallback
```

---

## RAG Integration

The teaching engine does NOT call FAISS directly. The `/learn` route handler retrieves context and passes it as a string.

```python
# In main.py POST /learn handler:
chunks = faiss_search(topic)          # returns list[str]
context = "\n\n".join(chunks)         # join to single string
result = generate_lesson(topic, level, context)
```

If FAISS returns empty list, `context` is an empty string. The engine handles this via the prompt (`"No context available."`) and the fallback.
