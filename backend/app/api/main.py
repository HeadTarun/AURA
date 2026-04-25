from fastapi import APIRouter

from app.api.routes import career, evaluate, learn, quiz

api_router = APIRouter()

try:
    from app.api.routes import login, users
except ModuleNotFoundError:
    login = None
    users = None

if login is not None:
    api_router.include_router(login.router)
if users is not None:
    api_router.include_router(users.router)

# AI Tutor MVP routes
api_router.include_router(learn.router)
api_router.include_router(quiz.router)
api_router.include_router(evaluate.router)
api_router.include_router(career.router)
