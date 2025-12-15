from pydantic import BaseModel
from services.answer_verification.src.enums import *
from typing import Optional

class VerificationRequest(BaseModel):
    question_text: str
    language: str
    numeric_answer: float


class SourceMetadata(BaseModel):
    title: str
    site_name: str
    url: str


class VerificationResult(BaseModel):
    verified_answer: Optional[float] = None
    source: Optional[SourceMetadata] = None