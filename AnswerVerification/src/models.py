from dataclasses import dataclass
from enums import *

@dataclass
class VerificationRequest:
    question_text: str
    language: Language
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