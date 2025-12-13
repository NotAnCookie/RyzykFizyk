from fastapi import FastAPI
from app.routers import verify, session_router, trivia, questions
from services.answer_verification.src.verifier import AnswerVerifier
from services.session_manager.src.session_manager import SessionManager
from dotenv import load_dotenv
import os
from services.question_generator.src.questions_generator import QuestionGenerator
from services.trivia_generator.src.generator.trivia_generator import TriviaGenerator

# Generator pytań
question_generator = QuestionGenerator()

# Generator ciekawostek
trivia_service = TriviaGenerator()


load_dotenv()
#print("---------------------------------------------------------------------------------DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Quiz Backend")


verify_service = AnswerVerifier()

session_manager = SessionManager(
    question_generator=question_generator,
    verify_service=verify_service,
    trivia_service=trivia_service
)

app.include_router(questions.router)
app.include_router(trivia.router)
app.include_router(verify.router)
#app.include_router(session_router.router)
app.include_router(session_router.get_session_router(session_manager))
