'''
from services.trivia_generation.src.models import(
    TriviaRequest,
    TriviaResult,
    SourceMetadata
)
from schemas.trivia_dto import (
    TriviaRequestDTO,
    TriviaResultDTO,
    SourceMetadataDTO,
)
from schemas.enums import *


def dto_to_domain(dto: TriviaRequestDTO) -> TriviaRequest:
    return TriviaRequest(
        question_text=dto.question_text,
        language=Language(dto.language.value)
    )


def domain_to_dto(result: TriviaResult) -> TriviaResultDTO:
    return TriviaResultDTO(
        trivia=result.trivia,
        source=SourceMetadataDTO(
            url=result.source.url
        ) if result.source else None
    )
'''
