from services.answer_verification.src.models import VerificationRequest
from schemas.verify_dto import VerifyRequestDTO

def dto_to_domain(dto: VerifyRequestDTO) -> VerificationRequest:
    return VerificationRequest(
        question_text=dto.question_id,
        numeric_answer=float(dto.answer),
        language=dto.language
    )
