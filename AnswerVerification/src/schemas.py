from dataclasses import dataclass

@dataclass
class VerificationRequest:
    question_text: str
    language: str  # "PL" or "EN"
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