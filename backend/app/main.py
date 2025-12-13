from fastapi import FastAPI
from app.routers import verify, session_router, trivia, questions
from services.answer_verification.src.verifier import AnswerVerifier
from services.session_manager.src.session_manager import SessionManager
from dotenv import load_dotenv
import os
from services.question_generator.src.questions_generator import QuestionGenerator
from services.trivia_generator.src.generator.trivia_generator import TriviaGenerator
from fastapi.middleware.cors import CORSMiddleware

# Generator pytań
question_generator = QuestionGenerator()

# Generator ciekawostek
trivia_service = TriviaGenerator()


load_dotenv()
#print("---------------------------------------------------------------------------------DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Quiz Backend")

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Lista dozwolonych adresów (nasz frontend)
    allow_credentials=True,
    allow_methods=["*"],        # Pozwalamy na wszystkie metody (GET, POST, OPTIONS itp.)
    allow_headers=["*"],        # Pozwalamy na wszystkie nagłówki
)

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
