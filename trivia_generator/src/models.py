from typing import Optional
from pydantic import BaseModel
from enums import *

class TriviaRequest(BaseModel):
    question_text: str
    language : Language

class SourceMetadata(BaseModel):
    url: Optional[str]

class TriviaResult(BaseModel):
    trivia: str
    source: Optional[SourceMetadata] = None