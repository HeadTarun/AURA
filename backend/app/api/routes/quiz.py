from fastapi import APIRouter

router = APIRouter(tags=["quiz"])


@router.post("/quiz")
def quiz() -> dict:
    return {"status": "stub"}
