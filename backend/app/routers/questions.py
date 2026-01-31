from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel

from services.question_generator.src.categories import AVAILABLE_CATEGORIES, CATEGORIES_CONFIG
import random

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)

class CategoryResponse(BaseModel):
    id: str
    name: str


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    lang: str = Query("en", description="Kod języka (en/pl)")
    ):
        clean_list = []
        
        for cat_id, full_data in CATEGORIES_CONFIG.items():
            
            lang_specific_data = full_data.get(lang, full_data.get("en"))

            if not lang_specific_data:
                continue

            new_item = {
                "id": cat_id,                 # np. "geography"
                "name": lang_specific_data["name"] # np. "Geografia" (jeśli lang="pl")
            }
            
            clean_list.append(new_item)
        
        return clean_list

