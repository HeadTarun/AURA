from fastapi import APIRouter

from app.services.session_store import load_session

router = APIRouter(tags=["learn"])


@router.get("/debug/session/{student_id}", tags=["debug"])
def debug_session(student_id: str) -> dict:
    return load_session(student_id)


@router.post("/learn")
def learn() -> dict:
    return {"status": "stub"}
