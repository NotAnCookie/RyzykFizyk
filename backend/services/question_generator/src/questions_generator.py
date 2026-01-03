import wikipedia
import re
import random
from typing import Optional
from services.question_generator.src.models import Question
from services.question_generator.src.enums import Language
from services.question_generator.src.categories import WikiCategory, CATEGORIES_CONFIG, CATEGORIES_KEYWORDS
from schemas.enums import CategoryEnum


class QuestionGenerator:
    def __init__(self):
        pass  # Możesz tu później dodać konfigurację, jeśli potrzebna

    def resolve_category(self, category_id: str, language: Language) -> WikiCategory:
        main_config = CATEGORIES_CONFIG.get(category_id)
        
        if not main_config:
            print(f"⚠️ Nieznane ID kategorii: {category_id}. Używam fallback.")
            main_config = list(CATEGORIES_CONFIG.values())[0]

        lang_code = language.value 
        
        lang_data = main_config.get(lang_code, main_config.get("en"))

        return WikiCategory(
            name=lang_data["name"],
            keywords=lang_data["keywords"]
        )

    def remove_brackets(self, text: str) -> str:
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        return text

    def find_article_title(self, category: WikiCategory) -> Optional[str]:
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

    def generate_question(
        self, category, language: Language = Language.EN
    ) -> Optional[Question]:
        wikipedia.set_lang(language.value)

        category_obj = self.resolve_category(category, language)

        attempts = 0
        while attempts < 5:
            attempts += 1

            if not category_obj.keywords:
                print("DEBUG: Keyword list empty")
                return None
        
            # keyword = random.choice(category.keywords)
            # search_results = wikipedia.search(keyword)
            # title = random.choice(search_results)    

            title = self.find_article_title(category_obj)
            if not title: continue

            try:
                page = wikipedia.page(title, auto_suggest=False)
                content = page.summary
                content = self.remove_brackets(content)

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
                    answer=answer,

                )
                return question_obj

            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue

        return None
