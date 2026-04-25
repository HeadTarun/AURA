from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.quiz_engine import generate_quiz
from app.services.session_store import load_session, save_session

router = APIRouter(tags=["quiz"])


class QuizRequest(BaseModel):
    student_id: str = Field(min_length=1)


@router.post("/quiz")
def quiz(req: QuizRequest) -> dict[str, Any]:
    session = load_session(req.student_id)
    topic = (session.get("current_topic") or "").strip()
    if not topic:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "session_not_found",
                "message": "Call /learn first to start a session",
            },
        )

    result = generate_quiz(topic, session.get("level", "beginner"))
    session["pending_quiz"] = result
    save_session(session)

    return result
