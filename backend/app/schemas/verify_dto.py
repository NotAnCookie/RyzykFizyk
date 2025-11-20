from pydantic import BaseModel
from enums import *

class VerifyRequestDTO(BaseModel):
    question_id: str
    answer: str
    language: Language
