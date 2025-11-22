'''
from fastapi import APIRouter
from schemas.trivia_dto import TriviaRequestDTO
from mappers.trivia_mapper import dto_to_domain, domain_to_dto
from services.trivia_generation.src.generator import TriviaGenerator

router = APIRouter(prefix="/trivia")
generator = TriviaGenerator()


@router.post("/")
def generate_trivia(request: TriviaRequestDTO):
    domain_request = dto_to_domain(request)
    result = generator.generate_trivia(domain_request)
    return domain_to_dto(result)
'''