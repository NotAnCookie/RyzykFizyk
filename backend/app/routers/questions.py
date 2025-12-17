from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from services.question_generator.src.categories import AVAILABLE_CATEGORIES
import random

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)

class CategoryResponse(BaseModel):
    id: str
    name: str


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    
    clean_list = []
    
    # Iterujemy po słowniku i wyciągamy z niego to co potrzebne
    for key, data in AVAILABLE_CATEGORIES.items():

        new_item = {
            "id": str(key),      # np. "1"
            "name": data.name    # np. "geography"
        }
        
        clean_list.append(new_item)
    
    return clean_list

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

#     return generated_questionsfrom fastapi import APIRouter, HTTPException, Query