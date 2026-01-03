import wikipedia
import re
import random
import json
import os
from openai import OpenAI
from typing import Optional
from services.question_generator.src.models import Question
from services.question_generator.src.enums import Language
from services.question_generator.src.categories import WikiCategory, CATEGORIES_CONFIG, CATEGORIES_KEYWORDS
from schemas.enums import CategoryEnum
from dotenv import load_dotenv  
load_dotenv()

SYSTEM_PROMPT_TEMPLATE = {
    "pl": (
        "Jesteś precyzyjnym generatorem pytań do quizu wiedzy. "
        "Twoim celem jest wygenerowanie JEDNEGO ciekawego pytania wyłącznie na podstawie dostarczonego tekstu. "
        "Zawsze zwracasz wynik w formacie JSON."
    ),
    "en": (
        "You are a precise Trivia Quiz Generator. "
        "Your goal is to generate ONE interesting question based ONLY on the provided text. "
        "You always return the output in JSON format."
    )
}

QUESTION_PROMPT_TEMPLATE = {
    "pl": (
        "Przeanalizuj poniższy tekst: '{context_text}'. "
        "Znajdź liczbę, która jest w nim wprost podana (np. rok, ilość, wymiar). "
        "Ułóż JEDNO naturalne i ciekawe pytanie po polsku, na które odpowiedzią jest ta konkretna liczba. "
        "Zwróć TYLKO poprawny obiekt JSON z kluczami: 'question_text' (treść pytania) oraz 'answer_number' (liczba jako int lub float). "
        "Nie dodawaj żadnego innego tekstu ani formatowania markdown."
    ),

    "en": (
        "Analyze the following text: '{context_text}'. "
        "Identify a number explicitly mentioned in the text (e.g., a year, count, dimension). "
        "Create ONE natural, interesting question in English where the answer is that specific number. "
        "Return ONLY a valid JSON object with keys: 'question_text' (string) and 'answer_number' (number as int or float). "
        "Do not add any other text or markdown formatting."
    ),
}

class QuestionGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ Brak klucza OPENAI_API_KEY w pliku .env")
        
        self.client = OpenAI(api_key=api_key)

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
        
    def generate_question_with_ai(self, context_text: str, topic: str, language: Language) -> Optional[dict]:

        lang_key = language.value
        
        system_prompt = SYSTEM_PROMPT_TEMPLATE.get(lang_key, SYSTEM_PROMPT_TEMPLATE["en"])

        raw_user_prompt = QUESTION_PROMPT_TEMPLATE.get(lang_key, QUESTION_PROMPT_TEMPLATE["en"])
        user_prompt = raw_user_prompt.format(context_text=context_text[:1500])

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Lub "gpt-4o-mini" (tańszy i szybszy)
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" }, # Wymusza JSON
                temperature=0.7 
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            return {
                "question": data.get("question_text"),
                "answer": data.get("answer_number")
            }
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
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

                # sentences = content.split('.')
                # candidates = []

                # for sentence in sentences:
                #     numbers = re.findall(r'\b\d{2,}(?:[.,]\d+)?\b', sentence)
                #     valid_numbers = [n for n in numbers if len(n) < 4]
                #     if valid_numbers and len(sentence) > 30:
                #         number_to_hide = min(valid_numbers, key=len)
                #         candidates.append((sentence, number_to_hide))

                # if not candidates:
                #     continue

                # selected_sentence, answer = random.choice(candidates)
                # question_text = selected_sentence.replace(answer, " [???] ")

                ai_result = self.generate_question_with_ai(content, title, language)
                
                if not ai_result or not ai_result.get("question"):
                    continue

                question_obj = Question(
                    category=category,
                    language=language,
                    question_text=ai_result["question"],
                    topic=title,
                    answer=float(ai_result["answer"]),

                )
                return question_obj

            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue

        return None
