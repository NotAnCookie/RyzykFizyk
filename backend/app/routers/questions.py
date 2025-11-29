from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.services.question_generator.src.config import AVAILABLE_CATEGORIES
from app.services.question_generator.src.enums import Language
from app.services.question_generator.src.questions_generator import generate_question

router = APIRouter(
    prefix="/api/questions", 
    tags=["Questions"]
)

CATEGORIES_DB = {
    f"cat_{i}": category 
    for i, category in enumerate(AVAILABLE_CATEGORIES, 1)
}

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