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


from schemas.question import Question as GlobalQuestion
from schemas.enums import CategoryEnum as GlobalCategory
import uuid

def map_generated_question_to_global(q) -> GlobalQuestion:
    """
    Mapuje pytanie z generatora (lokalna klasa) na globalny model Question.
    """
    return GlobalQuestion(
        id=int(uuid.uuid4().int >> 64), 
        text=q.question_text,
        category=GlobalCategory[q.category.name.upper()],
        language=q.language,
        answer=float(q.answer) if q.answer else None,
        trivia=None,
        sourceUrl=None
    )