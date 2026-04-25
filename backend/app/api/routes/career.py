from fastapi import APIRouter

router = APIRouter(tags=["career"])


@router.post("/career")
def career() -> dict:
    return {"status": "stub"}
