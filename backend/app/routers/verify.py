from fastapi import APIRouter
from schemas.verify_dto import VerifyRequestDTO
from mappers.verify_mapper import dto_to_domain
from services.answer_verification.src.verifier import AnswerVerifier

router = APIRouter(
    prefix="/verify",
    tags=["Verification"]  
)
verifier = AnswerVerifier()

@router.post("/")
def verify_endpoint(request: VerifyRequestDTO):
    domain_request = dto_to_domain(request)
    result = verifier.verify(domain_request)

    return {
        "correct": result.verified_answer,
        "source": result.source
    }
