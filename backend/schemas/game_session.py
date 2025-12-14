from pydantic import BaseModel
from schemas.enums import *
from typing import Optional
from schemas.player import *
from schemas.question import *
from services.question_generator.src.categories import WikiCategory

MAX_QUESTIONS = 7

class GameSession(BaseModel):
    id: int
    player: Optional[Player] = None
    questions: list[Question]
    answers: list[PlayerAnswer]
    currentQuestion: int
    language: Language
    category: WikiCategory
    state: SessionState

