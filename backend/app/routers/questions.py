from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel

from schemas.questions_dto import GenerateQuizRequestDTO, QuestionItemDTO
from mappers.question_mapper import domain_to_dto, map_category_enum
from services.question_generator.src.questions_generator import QuestionGenerator
from services.question_generator.src.categories import AVAILABLE_CATEGORIES
import random

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

class CategoryResponse(BaseModel):
    id: str
    name: str

# Tworzymy instancję generatora
question_generator = QuestionGenerator()

@router.post("/generate-quiz")
async def generate_quiz(request: GenerateQuizRequestDTO):

    target_category_id = request.category
    if request.category == 'random':
        available_keys = list(AVAILABLE_CATEGORIES.keys())
        if available_keys:
            target_category_id = random.choice(available_keys)
            #print(f"DEBUG: Wylosowano kategorię: {target_category_id}")

    if target_category_id not in AVAILABLE_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Category '{request.category}' not found")

    category_enum = AVAILABLE_CATEGORIES[target_category_id]

    generated = []
    attempts = 0

    while len(generated) < request.amount and attempts < 20:
        attempts += 1
        try:
            q = question_generator.generate_question(category_enum, request.language)

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

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    print("DEBUG: Generowanie listy kategorii...") # Zobaczysz to w terminalu
    
    clean_list = []
    
    # Iterujemy po słowniku i wyciągamy z niego to co potrzebne
    for key, data in AVAILABLE_CATEGORIES.items():
        
        # Tworzymy prosty obiekt
        new_item = {
            "id": str(key),      # np. "1"
            "name": data.name    # np. "Geography"
        }
        
        clean_list.append(new_item)
    
    print(f"DEBUG: Wysyłam {len(clean_list)} kategorii.")
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
from typing import List

from app.services.question_generator.src.config import AVAILABLE_CATEGORIES
from app.services.question_generator.src.enums import Language
from app.services.question_generator.src.questions_generator import generate_question

router = APIRouter(
    prefix="/api/questions", 
    tags=["Questions"]
)

CATEGORIES_DB = {
    f"{i}": category 
    for i, category in enumerate(AVAILABLE_CATEGORIES, 1)
}

@router.get("/categories")
async def get_categories():
    return [
            CATEGORIES_DB
        ]

@router.get("/generate-quiz", response_model=List[dict]) 
async def generate_quiz_endpoint(
    category_id: str = Query(..., alias="category"),
    lang: str = "en",
    amount: int = 7  
):
    category_obj = CATEGORIES_DB.get(category_id)
    
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category not found")

    language_enum = Language.PL if lang == 'pl' else Language.ENG
    
    generated_questions = []
    attempts = 0
    
    while len(generated_questions) < amount and attempts < 20:
        attempts += 1
        try:
            q = generate_question(category_obj, language_enum)
            
            if q:
                if any(existing["question_text"] == q.question_text for existing in generated_questions):
                    continue

                generated_questions.append({
                    "question_id": q.question_id,
                    "category": q.category.name,
                    "topic": q.topic,
                    "question_text": q.question_text,
                    "answer": q.answer,
                    "language": q.language.value
                })
              
        except Exception as e:
            continue

    if not generated_questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

    return generated_questions