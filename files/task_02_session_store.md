# Task 02 — Session Store

**Estimated time:** 30 minutes  
**Depends on:** Task 01  
**File to create:** `backend/app/services/session_store.py`

---

## Goal

Implement `load_session()` and `save_session()` with full schema validation and forward-compatibility.

---

## Function to Implement

**File:** `backend/app/services/session_store.py`  
**Functions:** `load_session(student_id: str) -> dict`, `save_session(session: dict) -> None`

---

## Full Implementation

```python
# backend/app/services/session_store.py

import json
import os

ALLOWED_KEYS = {
    "student_id", "current_topic", "level",
    "progress", "quiz_history", "gamification", "pending_quiz"
}


def _default_session(student_id: str) -> dict:
    return {
        "student_id": student_id,
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
    Adds any missing keys from default schema (forward compat).
    """
    path = f"sessions/{student_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            session = json.load(f)
        defaults = _default_session(student_id)
        for key, val in defaults.items():
            if key not in session:
                session[key] = val
        return session
    return _default_session(student_id)


def save_session(session: dict) -> None:
    """
    Persist session to disk as JSON.
    Strips any undeclared top-level keys.
    Trims quiz_history to last 100 entries.
    """
    # Strip undeclared keys
    for key in list(session.keys()):
        if key not in ALLOWED_KEYS:
            del session[key]

    # Trim history
    session["quiz_history"] = session["quiz_history"][-100:]

    os.makedirs("sessions", exist_ok=True)
    path = f"sessions/{session['student_id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)
```

---

## curl Test

Add a temporary debug route to `backend/app/api/routes/learn.py`:

```python
# Temporary — remove after testing
from fastapi import APIRouter
from backend.app.services.session_store import load_session

router = APIRouter()

@router.get("/debug/session/{student_id}")
def debug_session(student_id: str):
    return load_session(student_id)
```

```bash
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

---

## Done When

- `load_session("new_id")` returns a valid default session
- `save_session(session)` writes `sessions/student_001.json`
- `load_session("student_001")` reads back what was saved
- `quiz_history` is trimmed to 100 entries on save
- File contains exactly the 7 declared top-level keys
