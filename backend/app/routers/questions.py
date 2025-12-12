from fastapi import APIRouter, HTTPException
from typing import List

from schemas.questions_dto import GenerateQuizRequestDTO, QuestionItemDTO
from mappers.question_mapper import domain_to_dto, map_category_enum
from services.question_generator.src.questions_generator import generate_question

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/generate-quiz")
async def generate_quiz(request: GenerateQuizRequestDTO):

    #category = map_category_enum(request.category)
    category_enum = request.category

    generated = []
    attempts = 0

    while len(generated) < request.amount and attempts < 20:
        attempts += 1
        try:
            q = generate_question(category_enum, request.language)

            if q is None:
                continue

            if any(existing["question_text"] == q.question_text for existing in generated):
                continue

            generated.append({
                "question_text": q.question_text,
                "answer": q.answer,
                "topic": q.topic,
                "category": q.category.name,
                "language": q.language.value
            })

        # except Exception:
        #     continue
        except Exception as e:
            print("ERROR WHILE GENERATING:", e)
            raise e

    if not generated:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

    return generated

# @router.post("/generate", response_model=List[QuestionItemDTO])
# async def generate_quiz(request: GenerateQuizRequestDTO):
#     generated = []
#     attempts = 0

#     while len(generated) < request.amount and attempts < 20:
#         attempts += 1
#         q = generate_question(request.category, request.language)
#         if q:
#             if any(item.question_id == q.question_id for item in generated):
#                 continue
#             generated.append(q)

#     if not generated:
#         raise HTTPException(status_code=500, detail="Failed to generate quiz")

#     return [domain_to_dto(q) for q in generated]



# from fastapi import APIRouter, HTTPException, Query
# from typing import List

# from services.question_generator.src.config import AVAILABLE_CATEGORIES
# from services.question_generator.src.enums import Language
# from services.question_generator.src.questions_generator import generate_question

# router = APIRouter(
#     prefix="/api/questions", 
#     tags=["Questions"]
# )

# CATEGORIES_DB = {
#     f"cat_{i}": category 
#     for i, category in enumerate(AVAILABLE_CATEGORIES, 1)
# }

# @router.get("/generate-quiz", response_model=List[dict]) 
# async def generate_quiz_endpoint(
#     category_id: str = Query(..., alias="category"),
#     lang: str = "en",
#     amount: int = 7  
# ):
#     category_obj = CATEGORIES_DB.get(category_id)
    
#     if not category_obj:
#         raise HTTPException(status_code=404, detail="Category not found")

#     language_enum = Language.PL if lang == 'pl' else Language.ENG
    
#     generated_questions = []
#     attempts = 0
    
#     while len(generated_questions) < amount and attempts < 20:
#         attempts += 1
#         try:
#             q = generate_question(category_obj, language_enum)
            
#             if q:
#                 if any(existing["question_text"] == q.question_text for existing in generated_questions):
#                     continue

#                 generated_questions.append({
#                     "question_id": q.question_id,
#                     "category": q.category.name,
#                     "topic": q.topic,
#                     "question_text": q.question_text,
#                     "answer": q.answer,
#                     "language": q.language.value
#                 })
              
#         except Exception as e:
#             continue

#     if not generated_questions:
#         raise HTTPException(status_code=500, detail="Failed to generate quiz")

#     return generated_questions