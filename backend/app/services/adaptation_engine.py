<<<<<<< HEAD
# backend/app/services/adaptation_engine.py


def upgrade_level(level: str) -> str:
    levels = ["beginner", "intermediate", "advanced"]
    idx = levels.index(level)
    return levels[min(idx + 1, 2)]


def downgrade_level(level: str) -> str:
    levels = ["beginner", "intermediate", "advanced"]
    idx = levels.index(level)
    return levels[max(idx - 1, 0)]


def adapt_session(session: dict, correct: bool, score: int) -> dict:
    """
    Mutates session in-place. Returns adaptation summary.
    MUST be called AFTER quiz_history has been appended.
    No LLM calls. Pure rule-based logic.
    """
    current_level = session["level"]
    result = {
        "level_changed": False,
        "old_level": current_level,
        "new_level": current_level,
        "topic_completed": False,
        "reason": "no_change"
    }

    # Mark topic completed if correct
    if correct:
        topic = session.get("current_topic", "")
        completed = session["progress"]["completed_topics"]
        if topic and topic not in completed:
            completed.append(topic)
            result["topic_completed"] = True

    # Need at least 3 history entries to evaluate level change
    history = session["quiz_history"]
    if len(history) < 3:
        return result

    recent = history[-3:]
    recent_correct = sum(1 for h in recent if h["correct"])

    if recent_correct == 3:
        new_level = upgrade_level(current_level)
        if new_level != current_level:
            session["level"] = new_level
            result.update({"level_changed": True, "new_level": new_level,
                           "reason": "3_consecutive_correct"})

    elif recent_correct == 0:
        new_level = downgrade_level(current_level)
        if new_level != current_level:
            session["level"] = new_level
            result.update({"level_changed": True, "new_level": new_level,
                           "reason": "3_consecutive_incorrect"})

    return result
=======
# adaptation_engine.py — Adaptive learning: adjusts difficulty based on student performance
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
