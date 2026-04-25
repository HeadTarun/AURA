# Adaptation Engine

**File:** `engines/adaptation_engine.py`  
**Function:** `adapt_session(session, correct, score) -> dict`  
**Called by:** `POST /evaluate` handler  
**Returns:** Updated session (mutates in-place + returns adaptation summary)

---

## Responsibility

1. Read quiz result (correct/incorrect, score)
2. Look at recent quiz history in session
3. Adjust `session.level` if pattern warrants it
4. Mark topic as completed if correct
5. Return adaptation summary (what changed)

---

## Input

```python
def adapt_session(session: dict, correct: bool, score: int) -> dict:
```

| Param | Type | Notes |
|-------|------|-------|
| `session` | dict | Full StudentSession object (mutated in-place) |
| `correct` | bool | Whether the student answered correctly |
| `score` | int | Points for this answer (0 or 10) |

**Returns:** `adaptation_result` dict (see below)

---

## Logic (Rule-Based, No LLM)

```python
def adapt_session(session: dict, correct: bool, score: int) -> dict:
    history = session["quiz_history"]
    current_level = session["level"]
    adaptation_result = {
        "level_changed": False,
        "old_level": current_level,
        "new_level": current_level,
        "topic_completed": False,
        "reason": "no_change"
    }
    
    # Mark topic completed if correct
    if correct:
        topic = session["current_topic"]
        if topic and topic not in session["progress"]["completed_topics"]:
            session["progress"]["completed_topics"].append(topic)
            adaptation_result["topic_completed"] = True
    
    # Need at least 3 history entries to adapt level
    if len(history) < 3:
        return adaptation_result
    
    # Look at last 3 results
    recent = history[-3:]
    recent_correct = sum(1 for h in recent if h["correct"])
    
    # Upgrade level: 3/3 correct at current level
    if recent_correct == 3:
        new_level = upgrade_level(current_level)
        if new_level != current_level:
            session["level"] = new_level
            adaptation_result["level_changed"] = True
            adaptation_result["new_level"] = new_level
            adaptation_result["reason"] = "3_consecutive_correct"
    
    # Downgrade level: 0/3 correct at current level
    elif recent_correct == 0:
        new_level = downgrade_level(current_level)
        if new_level != current_level:
            session["level"] = new_level
            adaptation_result["level_changed"] = True
            adaptation_result["new_level"] = new_level
            adaptation_result["reason"] = "3_consecutive_incorrect"
    
    return adaptation_result


def upgrade_level(level: str) -> str:
    levels = ["beginner", "intermediate", "advanced"]
    idx = levels.index(level)
    return levels[min(idx + 1, 2)]


def downgrade_level(level: str) -> str:
    levels = ["beginner", "intermediate", "advanced"]
    idx = levels.index(level)
    return levels[max(idx - 1, 0)]
```

---

## Adaptation Result Schema

```json
{
  "level_changed": false,
  "old_level": "beginner",
  "new_level": "beginner",
  "topic_completed": true,
  "reason": "no_change | 3_consecutive_correct | 3_consecutive_incorrect"
}
```

---

## Rules Summary

| Condition | Action |
|-----------|--------|
| Last 3 answers all correct | Upgrade level (beginner→intermediate→advanced) |
| Last 3 answers all incorrect | Downgrade level (advanced→intermediate→beginner) |
| Mixed results | No change |
| Fewer than 3 history entries | No change |
| Current answer correct | Append topic to `completed_topics` |

---

## Edge Cases

| Case | Handling |
|------|----------|
| Already at `"advanced"` and 3/3 correct | Stay at `"advanced"`, `level_changed = false` |
| Already at `"beginner"` and 0/3 correct | Stay at `"beginner"`, `level_changed = false` |
| Topic already in `completed_topics` | Do not add again |
| `quiz_history` has fewer than 3 entries | Return early, no level change |

---

## No LLM Calls

The adaptation engine uses ONLY rule-based logic.  
No LLM. No prompts. No retries. No fallback needed.  
It is a deterministic pure function that mutates `session` in-place.
