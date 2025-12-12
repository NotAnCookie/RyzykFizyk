import wikipedia
import re
import random
from typing import Optional

# Importujemy Twoje modele
from services.question_generator.src.models import Question
from services.question_generator.src.enums import Language
from services.question_generator.src.categories import WikiCategory
from schemas.enums import *

def resolve_category(category_enum: CategoryEnum) -> WikiCategory:
    if category_enum == CategoryEnum.RANDOM:
        data = random.choice(list(CATEGORIES_KEYWORDS.values()))
        return WikiCategory(**data)

    data = CATEGORIES_KEYWORDS[category_enum.value]
    return WikiCategory(**data)


def remove_brackets(text: str) -> str:
    """Usuwa przypisy [1] i nawiasy (ur...)"""
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text

def find_article_title(category: WikiCategory) -> Optional[str]:
    print(f"   -> Szukam w Wikipedii tematów dla: {category.name}...")
    
    if not category.keywords:
        return None
        
    keyword = random.choice(category.keywords)
    
    try:
        results = wikipedia.search(keyword, results=50)
        if not results:
            return None
        return random.choice(results)
    except Exception:
        return None

def generate_question(category_enum: CategoryEnum, language: Language = Language.EN) -> Optional[Question]:
    wikipedia.set_lang(language.value)
    category = resolve_category(category_enum)

    attempts = 0
    while attempts < 5:
        attempts += 1
        
        title = find_article_title(category)
        if not title:
            continue

        try:
            page = wikipedia.page(title, auto_suggest=False)
            content = page.summary
            content = remove_brackets(content)
            
            sentences = content.split('.')
            candidates = []
            
            for sentence in sentences:
                numbers = re.findall(r'\b\d{2,}(?:[.,]\d+)?\b', sentence)
                
                valid_numbers = [n for n in numbers if len(n) < 4]
                if valid_numbers and len(sentence) > 30:
                    number_to_hide = min(valid_numbers, key=len) 
                    candidates.append((sentence, number_to_hide))
            
            if not candidates:
                continue

            selected_sentence, answer = random.choice(candidates)
            question_text = selected_sentence.replace(answer, " [???] ")
            
            question_obj = Question(
                category=category,
                language=language,
                question_text=question_text.strip(),
                topic=title,
                answer=answer
            )
            
            return question_obj
            
        except (wikipedia.DisambiguationError, wikipedia.PageError):
            continue 
            
    return None