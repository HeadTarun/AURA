# Task 06 — Implement /evaluate Endpoint

**Estimated time:** 90 minutes  
**Depends on:** Task 02 (sessions), Task 05 (quiz engine)

---

## Goal

Implement the full `POST /evaluate` route. This wires together:
1. Answer comparison (rule-based, no LLM)
2. Evaluation JSON generation (LLM)
3. Gamification computation (pure function)
4. Adaptation engine (rule-based)
5. Session save

---

## Files to Create/Modify

- `engines/adaptation_engine.py` — create
- `modules/gamification.py` — create
- `main.py` — wire `POST /evaluate`

---

## Step 1: Create engines/adaptation_engine.py

```python
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
    No LLM calls. Pure rule-based logic.
    """
    result = {
        "level_changed": False,
        "old_level": session["level"],
        "new_level": session["level"],
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
    
    # Need 3+ history entries to adapt level
    history = session["quiz_history"]
    if len(history) < 3:
        return result
    
    recent = history[-3:]
    recent_correct = sum(1 for h in recent if h["correct"])
    
    if recent_correct == 3:
        new_level = upgrade_level(session["level"])
        if new_level != session["level"]:
            session["level"] = new_level
            result["level_changed"] = True
            result["new_level"] = new_level
            result["reason"] = "3_consecutive_correct"
    elif recent_correct == 0:
        new_level = downgrade_level(session["level"])
        if new_level != session["level"]:
            session["level"] = new_level
            result["level_changed"] = True
            result["new_level"] = new_level
            result["reason"] = "3_consecutive_incorrect"
    
    return result
```

---

## Step 2: Create modules/gamification.py

```python
XP_PER_CORRECT = 10
XP_PER_WRONG   = 0
STREAK_BONUS = {3: 5, 5: 10, 10: 20}
XP_THRESHOLDS = {1:0, 2:100, 3:250, 4:500, 5:900, 6:1400, 7:2000, 8:2800, 9:3800, 10:5000}

def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level

def compute_gamification(session: dict, correct: bool, score: int) -> dict:
    """
    Pure function. Mutates session["gamification"] in-place.
    Returns gamification result dict.
    """
    gami = session["gamification"]
    
    xp_earned = XP_PER_CORRECT if correct else XP_PER_WRONG
    
    if correct:
        gami["streak"] += 1
    else:
        gami["streak"] = 0
    
    # Streak bonus — only on exact milestone
    for threshold, bonus in STREAK_BONUS.items():
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

## Step 3: Wire POST /evaluate in main.py

```python
import anthropic as _anthropic
import json as _json

from engines.adaptation_engine import adapt_session
from modules.gamification import compute_gamification

_llm_client = _anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

EVAL_PROMPT = """A student answered a quiz question. Evaluate their performance.

Topic: {topic}
Question: {question}
Correct Answer: {answer}
Student's Answer: {student_answer}
Was correct: {correct}

Respond ONLY with a JSON object. No text before or after.

Required JSON:
{{
  "correct": {correct_bool},
  "feedback": "encouraging 1-2 sentence feedback",
  "explanation": "explain why the correct answer is right",
  "next_level": "beginner or intermediate or advanced",
  "improvement_tip": "one specific tip to improve",
  "weak_areas": ["area 1"],
  "score": {score},
  "confidence": 0.8
}}"""

EVAL_FALLBACK = {
    "correct": False,
    "feedback": "Good effort! Review the concept and try again.",
    "explanation": "The correct answer follows from the core definition of the concept.",
    "next_level": "beginner",
    "improvement_tip": "Re-read the explanation and focus on key points.",
    "weak_areas": [],
    "score": 0,
    "confidence": 0.5
}

def generate_evaluation(topic, question, answer, student_answer, correct) -> dict:
    score = 10 if correct else 0
    prompt = EVAL_PROMPT.format(
        topic=topic, question=question, answer=answer,
        student_answer=student_answer, correct=correct,
        correct_bool=str(correct).lower(), score=score
    )
    for attempt in range(2):
        try:
            resp = _llm_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt + ("\n\nJSON only." if attempt else "")}]
            )
            text = resp.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"): text = text[4:]
            data = _json.loads(text)
            required = ["correct","feedback","explanation","next_level","improvement_tip","weak_areas","score","confidence"]
            if all(k in data for k in required):
                return data
        except Exception:
            pass
    fallback = dict(EVAL_FALLBACK)
    fallback["correct"] = correct
    fallback["score"] = 10 if correct else 0
    return fallback

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    session = load_session(req.student_id)
    
    pending = session.get("pending_quiz")
    if not pending:
        raise HTTPException(
            status_code=400,
            detail={"error": "no_pending_quiz", "message": "Call /quiz first before evaluating"}
        )
    
    # 1. Compare answer (case-insensitive strip)
    correct = req.student_answer.strip().lower() == pending["answer"].strip().lower()
    score = 10 if correct else 0
    
    # 2. Generate evaluation (LLM)
    evaluation = generate_evaluation(
        topic=session["current_topic"],
        question=pending["question"],
        answer=pending["answer"],
        student_answer=req.student_answer,
        correct=correct
    )
    
    # 3. Gamification (pure function — BEFORE adaptation so completed_topics is updated)
    gamification = compute_gamification(session, correct, score)
    
    # 4. Append to history
    session["quiz_history"].append({
        "question": pending["question"],
        "correct": correct,
        "score": score
    })
    
    # 5. Adaptation
    adaptation = adapt_session(session, correct, score)
    
    # 6. Clear pending quiz
    session["pending_quiz"] = None
    
    # 7. Save
    save_session(session)
    
    return {
        "evaluation": evaluation,
        "gamification": gamification
    }
```

---

## curl Test (Full Flow)

```bash
# 1. Learn
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "topic": "Percentage", "level": "beginner"}'

# 2. Quiz — note the answer from the response
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1"}'

# 3. Evaluate (use actual answer from quiz response above)
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"student_id": "s1", "student_answer": "75%"}'
```

**Expected response shape:**
```json
{
  "evaluation": {
    "correct": true,
    "feedback": "Excellent! You understood the concept perfectly.",
    "explanation": "3/4 × 100 = 75%",
    "next_level": "intermediate",
    "improvement_tip": "Try applying this to compound problems next.",
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

---

## Done When

- `POST /evaluate` returns `evaluation` + `gamification` fields
- Correct answer → `score: 10`, `correct: true`
- Wrong answer → `score: 0`, `correct: false`, `streak: 0`
- `session.pending_quiz` is `null` after evaluate
- `session.quiz_history` grows by 1 entry
- 3 correct in a row → `session.level` upgrades
