from pydantic import BaseModel
from enums import *
from typing import Optional


class TriviaRequestDTO(BaseModel):
    question_text: str
    language: Language


class SourceMetadataDTO(BaseModel):
    url: Optional[str] = None


class TriviaResultDTO(BaseModel):
    trivia: str
    source: Optional[SourceMetadataDTO] = None
