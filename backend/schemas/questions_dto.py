from pydantic import BaseModel
from typing import List
from schemas.enums import CategoryEnum
from services.question_generator.src.enums import Language

class GenerateQuizRequestDTO(BaseModel):
    category: CategoryEnum
    amount: int = 7
    language: Language

class QuestionItemDTO(BaseModel):
    question_id: str
    category: str
    topic: str
    question_text: str
    answer: float
    language: str
