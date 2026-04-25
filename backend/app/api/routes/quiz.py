<<<<<<< HEAD
# backend/app/api/routes/quiz.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_store import load_session, save_session
from app.services.quiz_engine import generate_quiz
=======
from fastapi import APIRouter
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b

router = APIRouter(tags=["quiz"])


<<<<<<< HEAD
class QuizRequest(BaseModel):
    student_id: str


@router.post("/quiz")
def quiz(req: QuizRequest) -> dict:
    session = load_session(req.student_id)

    if not session.get("current_topic"):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "session_not_found",
                "message": "Call /learn first to start a session",
            },
        )

    result = generate_quiz(session["current_topic"], session["level"])

    session["pending_quiz"] = result
    save_session(session)

    return result
=======
@router.post("/quiz")
def quiz() -> dict:
    return {"status": "stub"}
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
