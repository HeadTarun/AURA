from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.adaptation_engine import adapt_session
from app.services.gamification import compute_gamification
from app.services import llm_client
from app.services.session_store import load_session, save_session

router = APIRouter(tags=["evaluate"])


class EvaluateRequest(BaseModel):
    student_id: str = Field(min_length=1)
    student_answer: str = Field(min_length=1)


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

EVAL_REQUIRED = {
    "correct",
    "feedback",
    "explanation",
    "next_level",
    "improvement_tip",
    "weak_areas",
    "score",
    "confidence",
}


def _fallback_evaluation(
    session: dict[str, Any], pending: dict[str, Any], correct: bool, score: int
) -> dict[str, Any]:
    level = session.get("level", "beginner")
    return {
        "correct": correct,
        "feedback": (
            "Well done! You answered correctly."
            if correct
            else "Good effort. Review the explanation and try another question."
        ),
        "explanation": pending.get(
            "explanation", "The correct answer follows from the lesson concept."
        ),
        "next_level": level,
        "improvement_tip": (
            "Try a slightly harder example next."
            if correct
            else "Re-read the key points, then solve one similar example."
        ),
        "weak_areas": [] if correct else [session.get("current_topic", "current topic")],
        "score": score,
        "confidence": 0.8,
    }


def _normalize_answer(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def generate_evaluation(
    session: dict[str, Any], pending: dict[str, Any], student_answer: str
) -> dict[str, Any]:
    answer = str(pending.get("answer", ""))
    correct = _normalize_answer(student_answer) == _normalize_answer(answer)
    score = 10 if correct else 0
    fallback = _fallback_evaluation(session, pending, correct, score)

    try:
        data = llm_client.call_llm(
            EVAL_PROMPT.format(
                topic=session.get("current_topic", ""),
                question=pending.get("question", ""),
                answer=answer,
                student_answer=student_answer,
                correct=correct,
                correct_lower=str(correct).lower(),
                level=session.get("level", "beginner"),
                score=score,
            ),
            fallback,
            max_tokens=512,
        )
    except Exception:
        data = fallback

    if not isinstance(data, dict) or not EVAL_REQUIRED.issubset(data.keys()):
        data = fallback

    data["correct"] = correct
    data["score"] = score
    return data


@router.post("/evaluate")
def evaluate(req: EvaluateRequest) -> dict[str, Any]:
    session = load_session(req.student_id)
    pending = session.get("pending_quiz")
    if not isinstance(pending, dict):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_pending_quiz",
                "message": "Call /quiz first before evaluating",
            },
        )

    evaluation = generate_evaluation(session, pending, req.student_answer)
    correct = bool(evaluation["correct"])
    score = int(evaluation["score"])

    session.setdefault("quiz_history", []).append(
        {
            "question": pending.get("question", ""),
            "answer": pending.get("answer", ""),
            "student_answer": req.student_answer,
            "correct": correct,
            "score": score,
        }
    )
    adapt_session(session, correct, score)
    gamification_result = compute_gamification(session, correct, score)
    session["pending_quiz"] = None
    save_session(session)

    return {
        "evaluation": evaluation,
        "gamification": gamification_result,
    }
