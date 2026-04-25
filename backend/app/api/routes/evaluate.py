from fastapi import APIRouter

router = APIRouter(tags=["evaluate"])


@router.post("/evaluate")
def evaluate() -> dict:
    return {"status": "stub"}
