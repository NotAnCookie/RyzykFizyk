# schemas/session_dto.py
from pydantic import BaseModel
from typing import Optional, List
from schemas.enums import Language

class CreateSessionDTO(BaseModel):
    player_id: int
    player_name: str
    player_email: str
    language: Language
    category: str

class QuestionDTO(BaseModel):
    id: int
    text: str
    topic: str
    category: str
    answer: Optional[float] = None
    trivia: Optional[str] = None
    sourceUrl: Optional[str] = None

class PlayerAnswerDTO(BaseModel):
    question_id: int
    value: float

class SessionSummaryDTO(BaseModel):
    session_id: int
    state: str
    total_questions: int
    all_questions: List[QuestionDTO]
    all_answers: List[PlayerAnswerDTO]


class SessionResponseDTO(BaseModel):
    session_id: int
    state: str
    current_question_index: int
    total_questions: int
    current_question: Optional[QuestionDTO] = None
    all_questions: Optional[List[QuestionDTO]] = None

