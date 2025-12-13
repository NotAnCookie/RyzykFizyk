from fastapi import APIRouter
from schemas.trivia_dto import TriviaRequestDTO, TriviaResultDTO
from mappers.trivia_mapper import dto_to_domain, domain_to_dto
from services.trivia_generator.src.generator.trivia_generator import TriviaGenerator

router = APIRouter(
    prefix="/trivia",
    tags=["Trivia"]
)

generator = TriviaGenerator()


@router.post("/", response_model=TriviaResultDTO)
async def generate_trivia(request: TriviaRequestDTO):
    domain_request = dto_to_domain(request)
    result = generator.generate_trivia(domain_request)

    return domain_to_dto(result)
