from fastapi import APIRouter
from pydantic import BaseModel

from app.services.session_store import load_session, save_session

router = APIRouter(tags=["learn"])


class LearnRequest(BaseModel):
    student_id: str
    topic: str


@router.get("/debug/session/{student_id}", tags=["debug"])
def debug_session(student_id: str) -> dict:
    return load_session(student_id)


@router.post("/learn")
def learn(req: LearnRequest) -> dict:
    session = load_session(req.student_id)
    session["current_topic"] = req.topic
    save_session(session)
    return {"status": "ok", "student_id": req.student_id, "current_topic": req.topic}
