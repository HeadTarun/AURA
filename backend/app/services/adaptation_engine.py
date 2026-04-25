from typing import Any

from app.services.teaching_engine import normalize_level

LEVELS = ["beginner", "intermediate", "advanced"]


def upgrade_level(level: str) -> str:
    safe_level = normalize_level(level)
    idx = LEVELS.index(safe_level)
    return LEVELS[min(idx + 1, len(LEVELS) - 1)]


def downgrade_level(level: str) -> str:
    safe_level = normalize_level(level)
    idx = LEVELS.index(safe_level)
    return LEVELS[max(idx - 1, 0)]


def adapt_session(session: dict[str, Any], correct: bool, score: int) -> dict[str, Any]:
    current_level = normalize_level(session.get("level"))
    session["level"] = current_level
    session.setdefault("progress", {}).setdefault("completed_topics", [])
    session.setdefault("quiz_history", [])

    result = {
        "level_changed": False,
        "old_level": current_level,
        "new_level": current_level,
        "topic_completed": False,
        "reason": "no_change",
    }

    if correct:
        topic = (session.get("current_topic") or "").strip()
        completed = session["progress"]["completed_topics"]
        if topic and topic not in completed:
            completed.append(topic)
            result["topic_completed"] = True

    history = session["quiz_history"]
    if len(history) < 3:
        return result

    recent = history[-3:]
    recent_correct = sum(1 for entry in recent if bool(entry.get("correct")))

    if recent_correct == 3:
        new_level = upgrade_level(current_level)
        reason = "3_consecutive_correct"
    elif recent_correct == 0:
        new_level = downgrade_level(current_level)
        reason = "3_consecutive_incorrect"
    else:
        return result

    if new_level != current_level:
        session["level"] = new_level
        result.update(
            {
                "level_changed": True,
                "new_level": new_level,
                "reason": reason,
            }
        )

    return result
