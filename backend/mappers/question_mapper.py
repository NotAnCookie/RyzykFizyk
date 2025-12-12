from schemas.questions_dto import QuestionItemDTO
from services.question_generator.src.models import Question
from schemas.enums import *
import random
from services.question_generator.src.categories import AVAILABLE_CATEGORIES

def domain_to_dto(question: Question) -> QuestionItemDTO:
    return QuestionItemDTO(
        question_id=question.question_id,
        category=question.category.name,
        topic=question.topic,
        question_text=question.question_text,
        answer=question.answer,
        language=question.language.value
    )

def map_category_enum(enum_value: CategoryEnum):
    if enum_value == CategoryEnum.RANDOM:
        return random.choice(list(AVAILABLE_CATEGORIES.values()))

    return AVAILABLE_CATEGORIES[enum_value.value]
