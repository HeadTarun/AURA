from fastapi import APIRouter

router = APIRouter(tags=["learn"])


@router.post("/learn")
def learn() -> dict:
    return {"status": "stub"}
