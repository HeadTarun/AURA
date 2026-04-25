import json
import os
from typing import Any

ALLOWED_KEYS = {
    "student_id",
    "current_topic",
    "level",
    "progress",
    "quiz_history",
    "gamification",
    "pending_quiz",
}


def _default_session(student_id: str) -> dict[str, Any]:
    return {
        "student_id": student_id,
        "current_topic": "",
        "level": "beginner",
        "progress": {"completed_topics": []},
        "quiz_history": [],
        "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
        "pending_quiz": None,
    }


def load_session(student_id: str) -> dict[str, Any]:
    """
    Load session from disk. Create default if not found.
    Never returns None. Always returns a valid session dict.
    Adds any missing keys from default schema (forward compat).
    """
    path = f"sessions/{student_id}.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            session = json.load(f)
        defaults = _default_session(student_id)
        for key, val in defaults.items():
            if key not in session:
                session[key] = val
        return session
    return _default_session(student_id)


def save_session(session: dict[str, Any]) -> None:
    """
    Persist session to disk as JSON.
    Strips any undeclared top-level keys.
    Trims quiz_history to last 100 entries.
    """
    for key in list(session.keys()):
        if key not in ALLOWED_KEYS:
            del session[key]

    session["quiz_history"] = session["quiz_history"][-100:]

    os.makedirs("sessions", exist_ok=True)
    path = f"sessions/{session['student_id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
