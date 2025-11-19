from dataclasses import dataclass
from services.answer_verification.src.enums import *

@dataclass
class VerificationRequest:
    question_text: str
    language: str
    numeric_answer: float

@dataclass
class SourceMetadata:
    title: str
    site_name: str
    url: str

@dataclass
class VerificationResult:
    verified_answer: float
    source: SourceMetadata