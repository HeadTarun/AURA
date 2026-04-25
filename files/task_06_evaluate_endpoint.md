# Task 06 — Implement /evaluate Endpoint

**Estimated time:** 1.5 hours  
**Depends on:** Task 02, Task 05  
**Files to create/modify:**
- `backend/app/services/adaptation_engine.py` ← create
- `backend/app/services/gamification.py` ← create
- `backend/app/api/routes/evaluate.py` ← replace stub

---

## Goal

Wire together: answer comparison → LLM evaluation → gamification → adaptation → session save → response.

---

## Step 1: Create adaptation_engine.py

**File:** `backend/app/services/adaptation_engine.py`

```python
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
```

---

## Step 2: Create gamification.py

**File:** `backend/app/services/gamification.py`

```python
# backend/app/services/gamification.py

XP_PER_CORRECT = 10
XP_PER_WRONG   = 0
STREAK_BONUS   = {3: 5, 5: 10, 10: 20}
XP_THRESHOLDS  = {1: 0, 2: 100, 3: 250, 4: 500, 5: 900,
                  6: 1400, 7: 2000, 8: 2800, 9: 3800, 10: 5000}


def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level


def compute_gamification(session: dict, correct: bool, score: int) -> dict:
    """
    Pure function. Mutates session["gamification"] in-place.
    Call BEFORE adapt_session (so completed_topics reflect correct badge state).
    Returns gamification dict for the /evaluate HTTP response.
    """
    gami = session["gamification"]

    xp_earned = XP_PER_CORRECT if correct else XP_PER_WRONG

    if correct:
        gami["streak"] += 1
    else:
        gami["streak"] = 0

    # Streak bonus — only on exact milestone
    for threshold, bonus in sorted(STREAK_BONUS.items()):
        if gami["streak"] == threshold:
            xp_earned += bonus

    gami["xp"] += xp_earned
    gami["level"] = compute_level(gami["xp"])

    badges_earned = []
    completed_count = len(session["progress"]["completed_topics"])

    def award(badge_id: str, condition: bool):
        if condition and badge_id not in gami["badges"]:
            gami["badges"].append(badge_id)
            badges_earned.append(badge_id)

    award("first_lesson",  completed_count >= 1)
    award("streak_3",      gami["streak"] >= 3)
    award("streak_7",      gami["streak"] >= 7)
    award("perfect_quiz",  score == 10)
    award("ten_topics",    completed_count >= 10)

    return {
        "xp":            gami["xp"],
        "xp_earned":     xp_earned,
        "streak":        gami["streak"],
        "level":         gami["level"],
        "badges":        gami["badges"],
        "badges_earned": badges_earned
    }
```

---

## Step 3: Wire POST /evaluate

**File:** `backend/app/api/routes/evaluate.py`

```python
# backend/app/api/routes/evaluate.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.session_store import load_session, save_session
from backend.app.services.gamification import compute_gamification
from backend.app.services.adaptation_engine import adapt_session
from backend.app.services.llm_client import call_llm

router = APIRouter()


class EvaluateRequest(BaseModel):
    student_id: str
    student_answer: str


EVAL_PROMPT = """
A student answered a quiz question. Evaluate their performance.

Topic: {topic}
Question: {question}
Correct Answer: {answer}
Student's Answer: {student_answer}
Was the student correct: {correct}

Respond ONLY with a valid JSON object. No text before or after. No markdown fences.

Required JSON:
{{
  "correct": {correct_lower},
  "feedback": "encouraging 1-2 sentence feedback for the student",
  "explanation": "explain why the correct answer is right",
  "next_level": "{level}",
  "improvement_tip": "one specific actionable tip to improve",
  "weak_areas": [],
  "score": {score},
  "confidence": 0.9
}}
"""

EVAL_FALLBACK_CORRECT = {
    "correct": True,
    "feedback": "Well done! You answered correctly.",
    "explanation": "The correct answer follows from the core definition of the concept.",
    "next_level": "beginner",
    "improvement_tip": "Try applying this concept to more complex problems.",
    "weak_areas": [],
    "score": 10,
    "confidence": 0.8
}

EVAL_FALLBACK_WRONG = {
    "correct": False,
    "feedback": "Good effort! Review the concept and try again.",
    "explanation": "The correct answer follows from the core definition of the concept.",
    "next_level": "beginner",
    "improvement_tip": "Re-read the lesson explanation and focus on key points.",
    "weak_areas": [],
    "score": 0,
    "confidence": 0.8
}

EVAL_REQUIRED = [
    "correct", "feedback", "explanation", "next_level",
    "improvement_tip", "weak_areas", "score", "confidence"
]


def generate_evaluation(session: dict, pending: dict, correct: bool, score: int) -> dict:
    fallback = dict(EVAL_FALLBACK_CORRECT if correct else EVAL_FALLBACK_WRONG)
    fallback["correct"] = correct
    fallback["score"] = score
    fallback["next_level"] = session["level"]

    prompt = EVAL_PROMPT.format(
        topic=session["current_topic"],
        question=pending["question"],
        answer=pending["answer"],
        student_answer="(submitted answer)",
        correct=correct,
        correct_lower=str(correct).lower(),
        level=session["level"],
        score=score
    )

    data = call_llm(prompt, fallback, max_tokens=512)

    # Basic validation
    if isinstance(data, dict) and all(k in data for k in EVAL_REQUIRED):
        data["correct"] = correct   # enforce server-side truth
        data["score"]   = score
        return data

    return fallback


@router.post("/evaluate")
def evaluate(req: EvaluateRequest):
    session = load_session(req.student_id)

    pending = session.get("pending_quiz")
    if not pending:
        raise HTTPException(
            status_code=400,
            detail={"error": "no_pending_quiz", "message": "Call /quiz first before evaluating"}
        )

    # 1. Compare answer (case-insensitive, stripped)
    correct = req.student_answer.strip().lower() == pending["answer"].strip().lower()
    score = 10 if correct else 0

    # 2. LLM evaluation
    evaluation = generate_evaluation(session, pending, correct, score)

    # 3. Gamification (pure function — before adapt_session)
    gamification_result = compute_gamification(session, correct, score)

    # 4. Append to quiz_history (MUST happen before adapt_session)
    session["quiz_history"].append({
        "question": pending["question"],
        "correct": correct,
        "score": score
    })

    # 5. Adaptation (reads from quiz_history)
    adapt_session(session, correct, score)

    # 6. Clear pending quiz
    session["pending_quiz"] = None

    # 7. Save session
    save_session(session)

    return {
        "evaluation": evaluation,
        "gamification": gamification_result
    }
```

---

## curl Test (Full Flow)

```bash
# 1. Learn
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "topic": "Percentage", "level": "beginner"}'

# 2. Quiz — copy the "answer" field from response
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1"}'

# 3. Evaluate with correct answer (paste actual answer from step 2)
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "student_answer": "75%"}'
```

**Expected response shape:**
```json
{
  "evaluation": {
    "correct": true,
    "feedback": "Excellent! You understood the concept.",
    "explanation": "3/4 × 100 = 75%",
    "next_level": "beginner",
    "improvement_tip": "Try compound percentage problems next.",
    "weak_areas": [],
    "score": 10,
    "confidence": 0.95
  },
  "gamification": {
    "xp": 10,
    "xp_earned": 10,
    "streak": 1,
    "level": 1,
    "badges": ["first_lesson"],
    "badges_earned": ["first_lesson"]
  }
}
```

**Error test (no pending quiz):**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "student_answer": "anything"}'
```
**Expected:** HTTP 400 `{"error": "no_pending_quiz", ...}`

---

## Done When

- `POST /evaluate` returns `evaluation` + `gamification` fields
- Correct answer → `score: 10`, `correct: true`
- Wrong answer → `score: 0`, `correct: false`, `streak: 0`
- `session["pending_quiz"]` is `null` after evaluate
- `session["quiz_history"]` grows by 1 entry per call
- 3 correct in a row → `session["level"]` upgrades on the 3rd call
- No HTTP 500 under any LLM failure condition
