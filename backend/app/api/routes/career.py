from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.career import generate_career_guidance

router = APIRouter(tags=["career"])


class CareerRequest(BaseModel):
    goal: str = Field(min_length=1)
    completed_topics: list[str] = Field(default_factory=list)
    level: str = "beginner"


@router.post("/career")
def career(req: CareerRequest) -> dict[str, Any]:
    return generate_career_guidance(req.goal, req.completed_topics, req.level)
