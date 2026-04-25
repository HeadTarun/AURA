<<<<<<< HEAD
# backend/app/api/routes/evaluate.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_store import load_session, save_session
from app.services.gamification import compute_gamification
from app.services.adaptation_engine import adapt_session
from app.services.llm_client import call_llm
=======
from fastapi import APIRouter
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b

router = APIRouter(tags=["evaluate"])


<<<<<<< HEAD
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
def evaluate(req: EvaluateRequest) -> dict:
    # 1. Load session
    session = load_session(req.student_id)

    # 2. Validate pending quiz
    pending = session.get("pending_quiz")
    if not pending:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_pending_quiz",
                "message": "Call /quiz first before evaluating"
            }
        )

    # 3. Compare answer (case-insensitive, stripped)
    correct = req.student_answer.strip().lower() == pending["answer"].strip().lower()
    score = 10 if correct else 0

    # 4. LLM evaluation (fallback-safe)
    evaluation = generate_evaluation(session, pending, correct, score)

    # 5. Gamification (BEFORE adaptation)
    gamification_result = compute_gamification(session, correct, score)

    # 6. Append to quiz_history (MUST happen before adapt_session)
    session["quiz_history"].append({
        "question": pending["question"],
        "correct":  correct,
        "score":    score
    })

    # 7. Run adaptation (reads from quiz_history)
    adapt_session(session, correct, score)

    # 8. Clear pending quiz
    session["pending_quiz"] = None

    # 9. Save session
    save_session(session)

    # 10. Return response
    return {
        "evaluation":   evaluation,
        "gamification": gamification_result
    }
=======
@router.post("/evaluate")
def evaluate() -> dict:
    return {"status": "stub"}
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
