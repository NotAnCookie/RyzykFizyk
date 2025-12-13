from pydantic import BaseModel
from services.answer_verification.src.enums import *

class VerificationRequest(BaseModel):
    question_text: str
    language: str
    numeric_answer: float


class SourceMetadata(BaseModel):
    title: str
    site_name: str
    url: str


class VerificationResult(BaseModel):
    verified_answer: float
    source: SourceMetadata