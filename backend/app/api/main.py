from fastapi import APIRouter

from app.api.routes import career, evaluate, learn, login, quiz, users

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)

# AI Tutor MVP routes
api_router.include_router(learn.router)
api_router.include_router(quiz.router)
api_router.include_router(evaluate.router)
api_router.include_router(career.router)
