from schemas.trivia_dto import TriviaRequestDTO, TriviaResultDTO, SourceMetadataDTO
from services.trivia_generator.src.models import TriviaRequest, TriviaResult, SourceMetadata


def dto_to_domain(dto: TriviaRequestDTO) -> TriviaRequest:

    return TriviaRequest(
        question_text=dto.question_text,
        language=dto.language
    )


def domain_to_dto(result: TriviaResult) -> TriviaResultDTO:
    source_dto = (
        SourceMetadataDTO(url=result.source.url)
        if result.source
        else None
    )

    return TriviaResultDTO(
        trivia=result.trivia,
        source=source_dto
    )

