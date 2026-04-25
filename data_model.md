# Data Model

Single source of truth: `StudentSession`  
Storage: flat JSON files at `sessions/{student_id}.json`  
No database. No ORM. No migrations.

---

## StudentSession Schema (STRICT)

```json
{
  "student_id": "string",
  "current_topic": "string",
  "level": "beginner | intermediate | advanced",
  "progress": {
    "completed_topics": ["string"]
  },
  "quiz_history": [
    {
      "question": "string",
      "correct": true,
      "score": 10
    }
  ],
  "gamification": {
    "xp": 0,
    "streak": 0,
    "level": 1,
    "badges": []
  },
  "pending_quiz": null
}
```

### Field Definitions

| Field | Type | Rules |
|-------|------|-------|
| `student_id` | string | Required. Unique. Client-provided. |
| `current_topic` | string | Set by `/learn`. Read by `/quiz`. |
| `level` | enum | `"beginner"`, `"intermediate"`, `"advanced"`. Default: `"beginner"`. |
| `progress.completed_topics` | string[] | Append-only. Topic strings added after successful `/evaluate`. |
| `quiz_history` | object[] | Append-only. Max 100 entries (drop oldest). |
| `quiz_history[].question` | string | The question text. |
| `quiz_history[].correct` | boolean | Whether student answered correctly. |
| `quiz_history[].score` | integer | Score for this question (0 or 10). |
| `gamification.xp` | integer | Cumulative. Never decreases. |
| `gamification.streak` | integer | Incremented per correct answer in a session. |
| `gamification.level` | integer | 1–10. Computed from XP thresholds. |
| `gamification.badges` | string[] | Badge IDs. Static list. Append-only. |
| `pending_quiz` | object \| null | Set by `/quiz`. Cleared by `/evaluate`. |

---

## pending_quiz Schema

Stored in session between `/quiz` and `/evaluate` calls.

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

---

## Session File Operations

```python
# Load session (create if not exists)
def load_session(student_id: str) -> dict:
    path = f"sessions/{student_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {
        "student_id": student_id,
        "current_topic": "",
        "level": "beginner",
        "progress": {"completed_topics": []},
        "quiz_history": [],
        "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
        "pending_quiz": None
    }

# Save session
def save_session(session: dict) -> None:
    os.makedirs("sessions", exist_ok=True)
    path = f"sessions/{session['student_id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)
```

---

## XP → Level Thresholds

```python
XP_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 900,
    6: 1400,
    7: 2000,
    8: 2800,
    9: 3800,
    10: 5000
}

def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level
```

---

## Badge IDs (Static List)

```python
BADGES = {
    "first_lesson":   {"id": "first_lesson",   "label": "First Step",    "condition": "completed_topics >= 1"},
    "streak_3":       {"id": "streak_3",        "label": "On Fire",       "condition": "streak >= 3"},
    "streak_7":       {"id": "streak_7",        "label": "Week Warrior",  "condition": "streak >= 7"},
    "perfect_quiz":   {"id": "perfect_quiz",    "label": "Perfect Score", "condition": "score == 10 on last quiz"},
    "ten_topics":     {"id": "ten_topics",      "label": "Explorer",      "condition": "completed_topics >= 10"},
}
```

Badge logic is evaluated inside `compute_gamification()` only. No other code touches badges.

---

## No Other Models

There is no `LearningRoadmap`, `TopicNode`, `WeaknessMap`, `DailyLog`, or `QuizAttempt` model.  
These are removed from the MVP.  
All state lives in `StudentSession`.
