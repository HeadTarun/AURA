# Task 02 — Session Store

**Estimated time:** 30 minutes  
**Depends on:** Task 01

---

## Goal

Implement `load_session()` and `save_session()` with full schema validation. Replace stubs in `main.py`.

---

## Input

`student_id` string (any value)

---

## Output

A valid `StudentSession` dict loaded from `sessions/{student_id}.json` or initialized fresh if file doesn't exist.

---

## Files to Modify

`main.py` — replace the stub session helpers with the full implementation below.

---

## Exact Function

```python
import json
import os

DEFAULT_SESSION_TEMPLATE = {
    "current_topic": "",
    "level": "beginner",
    "progress": {"completed_topics": []},
    "quiz_history": [],
    "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
    "pending_quiz": None
}

def load_session(student_id: str) -> dict:
    """
    Load session from disk. Create default if not found.
    Never returns None. Always returns a valid session dict.
    """
    path = f"sessions/{student_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            session = json.load(f)
        # Ensure all keys exist (forward compat)
        for key, val in DEFAULT_SESSION_TEMPLATE.items():
            if key not in session:
                session[key] = val
        return session
    
    session = {"student_id": student_id}
    session.update(DEFAULT_SESSION_TEMPLATE.copy())
    session["progress"] = {"completed_topics": []}
    session["quiz_history"] = []
    session["gamification"] = {"xp": 0, "streak": 0, "level": 1, "badges": []}
    return session

def save_session(session: dict) -> None:
    """
    Save session dict to disk as JSON.
    Trims quiz_history to last 100 entries before saving.
    """
    os.makedirs("sessions", exist_ok=True)
    # Trim history
    session["quiz_history"] = session["quiz_history"][-100:]
    path = f"sessions/{session['student_id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)
```

---

## curl Test

Add a temporary debug route to `main.py`:

```python
@app.get("/debug/session/{student_id}")
def debug_session(student_id: str):
    return load_session(student_id)
```

Test:

```bash
# New session
curl http://localhost:8000/debug/session/student_001
```

**Expected:**
```json
{
  "student_id": "student_001",
  "current_topic": "",
  "level": "beginner",
  "progress": {"completed_topics": []},
  "quiz_history": [],
  "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
  "pending_quiz": null
}
```

```bash
# Verify persistence
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001", "topic": "Ratio", "level": "beginner"}'

# Session file should exist now
ls sessions/
```

---

## Done When

- `load_session("new_id")` returns a valid default session
- `save_session(session)` writes a file to `sessions/`
- `load_session("existing_id")` reads back what was saved
- `quiz_history` is trimmed to 100 on save
