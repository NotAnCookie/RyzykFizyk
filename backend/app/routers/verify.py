from fastapi import APIRouter
from pydantic import BaseModel
from services.answer_verification.src.verifier import AnswerVerifier
from services.answer_verification.src.models import VerificationRequest

router = APIRouter(prefix="/verify")

verifier = AnswerVerifier()

class VerifyRequest(BaseModel):
    question_id: str
    answer: str

@router.post("/")
def verify_endpoint(request: VerifyRequest):
    verification_request = VerificationRequest(
        question_text=request.question_id,
        numeric_answer=float(request.answer),
        language="pl"
    )
    result = verifier.verify(verification_request)
    return {"correct": result.verified_answer, "source": result.source}

