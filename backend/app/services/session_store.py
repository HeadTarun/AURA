import json
import os
import re
from typing import Any

SESSION_DIR = os.getenv("SESSION_DIR", os.path.join(os.getcwd(), "sessions"))

ALLOWED_KEYS = {
    "student_id",
    "current_topic",
    "level",
    "progress",
    "quiz_history",
    "gamification",
    "pending_quiz",
}


def _safe_student_id(student_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", (student_id or "").strip())
    return safe or "anonymous"


def _default_session(student_id: str) -> dict[str, Any]:
    return {
        "student_id": _safe_student_id(student_id),
        "current_topic": "",
        "level": "beginner",
        "progress": {"completed_topics": []},
        "quiz_history": [],
        "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
        "pending_quiz": None,
    }


def _session_path(student_id: str) -> str:
    os.makedirs(SESSION_DIR, exist_ok=True)
    return os.path.join(SESSION_DIR, f"{_safe_student_id(student_id)}.json")


def _repair_session(session: dict[str, Any], student_id: str) -> dict[str, Any]:
    defaults = _default_session(student_id)
    if not isinstance(session, dict):
        return defaults

    repaired = {key: session.get(key, defaults[key]) for key in ALLOWED_KEYS}
    repaired["student_id"] = _safe_student_id(str(repaired.get("student_id") or student_id))

    if repaired["level"] not in {"beginner", "intermediate", "advanced"}:
        repaired["level"] = "beginner"
    if not isinstance(repaired["progress"], dict):
        repaired["progress"] = defaults["progress"]
    if not isinstance(repaired["progress"].get("completed_topics"), list):
        repaired["progress"]["completed_topics"] = []
    if not isinstance(repaired["quiz_history"], list):
        repaired["quiz_history"] = []
    if not isinstance(repaired["gamification"], dict):
        repaired["gamification"] = defaults["gamification"]
    for key, value in defaults["gamification"].items():
        repaired["gamification"].setdefault(key, value)
    if not isinstance(repaired["gamification"].get("badges"), list):
        repaired["gamification"]["badges"] = []

    return repaired


def load_session(student_id: str) -> dict[str, Any]:
    path = _session_path(student_id)
    if not os.path.exists(path):
        return _default_session(student_id)

    try:
        with open(path, encoding="utf-8") as session_file:
            raw = json.load(session_file)
    except (OSError, json.JSONDecodeError):
        return _default_session(student_id)

    return _repair_session(raw, student_id)


def save_session(session: dict[str, Any]) -> None:
    repaired = _repair_session(session, str(session.get("student_id", "")))
    repaired["quiz_history"] = repaired["quiz_history"][-100:]

    path = _session_path(repaired["student_id"])
    with open(path, "w", encoding="utf-8") as session_file:
        json.dump(repaired, session_file, indent=2)

    session.clear()
    session.update(repaired)
