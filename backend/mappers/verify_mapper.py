from services.answer_verification.src.models import VerificationRequest
from schemas.verify_dto import VerifyRequestDTO

def dto_to_domain(dto: VerifyRequestDTO) -> VerificationRequest:
    return VerificationRequest(
        question_text=dto.question_id,
        numeric_answer=dto.answer,
        language=dto.language
    )

def domain_to_dto(domain: VerificationRequest) -> VerifyRequestDTO:
    return VerifyRequestDTO(
        question_id=domain.question_text,
        answer=str(domain.numeric_answer),
        language=domain.language,
    )
