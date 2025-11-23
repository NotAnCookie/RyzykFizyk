from fastapi import FastAPI
from app.routers import verify, session_router
from services.answer_verification.src.verifier import AnswerVerifier
from services.session_manager.src.session_manager import SessionManager

app = FastAPI(title="Quiz Backend")


verify_service = AnswerVerifier()

session_manager = SessionManager(
    question_generator=None,
    verify_service=verify_service,
    trivia_service=None
)

# app.include_router(questions.router)
# app.include_router(trivia.router)
app.include_router(verify.router)
app.include_router(session_router.router)
