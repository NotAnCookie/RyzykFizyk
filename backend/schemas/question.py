from pydantic import BaseModel
from schemas.enums import *
from typing import Optional

class Question(BaseModel):
    id: int
    text: str
    category: Category
    language: Language
    answer: Optional[float] = None
    trivia: Optional[str] = None
    sourceUrl: Optional[str] = None

    def validate(self) -> bool:
        return self.answer is not None and self.trivia is not None and self.sourceUrl is not None
    