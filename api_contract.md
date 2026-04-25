# API Contract

Base URL: `http://localhost:8000`  
All requests: `Content-Type: application/json`  
All responses: JSON

---

## POST /learn

**Purpose:** Retrieve a lesson for a topic. Creates session if not exists.

### Request

```json
{
  "student_id": "string",
  "topic": "string",
  "level": "beginner | intermediate | advanced"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `student_id` | Yes | Any unique string |
| `topic` | Yes | e.g. `"Ratio and Proportion"` |
| `level` | No | Default: `"beginner"` |

### Response

```json
{
  "concept": "string",
  "explanation_in_simple": "string",
  "real_world_examples": ["string"],
  "key_points": ["string"],
  "step_by_step": ["string"],
  "common_mistakes": ["string"],
  "difficulty": "beginner | intermediate | advanced",
  "estimated_time_min": 10,
  "confidence_score": 0.85
}
```

### curl

```bash
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001",
    "topic": "Ratio and Proportion",
    "level": "beginner"
  }'
```

---

## POST /quiz

**Purpose:** Generate one quiz question for the current topic.

### Request

```json
{
  "student_id": "string"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `student_id` | Yes | Must have an active session (call `/learn` first) |

### Response

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

**Note:** `answer` is included in the response for this MVP demo. In production, omit it and validate server-side only.

### curl

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001"
  }'
```

### Error (no active session)

```json
{
  "error": "session_not_found",
  "message": "Call /learn first to start a session"
}
```
HTTP 404

---

## POST /evaluate

**Purpose:** Submit student's answer, get evaluation + gamification update.

### Request

```json
{
  "student_id": "string",
  "student_answer": "string"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `student_id` | Yes | Must have a `pending_quiz` in session |
| `student_answer` | Yes | Must match one of the quiz options exactly |

### Response

```json
{
  "evaluation": {
    "correct": true,
    "feedback": "string",
    "explanation": "string",
    "next_level": "beginner | intermediate | advanced",
    "improvement_tip": "string",
    "weak_areas": ["string"],
    "score": 10,
    "confidence": 0.9
  },
  "gamification": {
    "xp": 120,
    "xp_earned": 10,
    "streak": 3,
    "level": 2,
    "badges": ["first_lesson"],
    "badges_earned": ["streak_3"]
  }
}
```

### curl

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001",
    "student_answer": "20"
  }'
```

### Error (no pending quiz)

```json
{
  "error": "no_pending_quiz",
  "message": "Call /quiz first before evaluating"
}
```
HTTP 400

---

## POST /career

**Purpose:** Get career guidance based on goal and completed topics.

### Request

```json
{
  "goal": "string",
  "completed_topics": ["string"],
  "level": "beginner | intermediate | advanced"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `goal` | Yes | e.g. `"SSC CGL"`, `"Data Analyst"`, `"Software Engineer"` |
| `completed_topics` | No | Default: `[]` |
| `level` | No | Default: `"beginner"` |

### Response

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

### curl

```bash
curl -X POST http://localhost:8000/career \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "SSC CGL",
    "completed_topics": ["Ratio and Proportion", "Percentage"],
    "level": "beginner"
  }'
```

---

## Error Response Format (All Endpoints)

```json
{
  "error": "error_code",
  "message": "Human-readable description"
}
```

| HTTP Code | When |
|-----------|------|
| 400 | Bad request (e.g. no pending quiz on /evaluate) |
| 404 | Session not found |
| 422 | Validation error (missing/wrong-type fields) |
| 500 | LLM failure after retry (fallback used — this should not return 500, use fallback instead) |
