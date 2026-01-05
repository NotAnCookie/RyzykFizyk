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
        "Tytuł artykułu: {topic}\n"
        "Tekst: '{context_text}'\n\n"
        "Twoim zadaniem jest ułożenie pytania do teleturnieju 'Milionerzy'.\n"
        "ZASADY KRYTYCZNE:\n"
        "1. SELEKCJA WARTOŚCI (Priorytety):\n"
        "   - NAJLEPSZE: Wielkości fizyczne (np. wysokość w metrach, masa w kg, prędkość km/h, temperatura), statystyki (populacja, procenty).\n"
        "   - OSTATECZNOŚĆ: Rok/Data. Pytaj o rok TYLKO wtedy, gdy w tekście nie ma absolutnie żadnych innych liczb. Daty są zazwyczaj nudne.\n"
        "2. FILTR ANTY-META (Najważniejsze!): \n"
        "   - ZABRANIA SIĘ pytać o strukturę tekstu (np. 'Ile przykładów wymieniono?', 'Ile typów podano?').\n"
        "   - Jeśli w tekście jest wyliczanka (np. 'wymieniono 3 kraje'), IGNORUJ TĘ LICZBĘ. Szukaj innej.\n"
        "3. JEDNOSTKA: Pytanie MUSI zawierać jednostkę (np. 'ile metrów', 'ile tysięcy', 'w jakim stopniu').\n"
        "4. ODPOWIEDŹ: Musi być czystą liczbą (int lub float).\n"
        "5. Jeśli nie możesz znaleźć sensownej liczby (a nie wyliczenia) -> ZWRÓĆ is_relevant: false.\n\n"
        "Zwróć TYLKO JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"Jaka jest maksymalna prędkość tego zwierzęcia w km/h?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    ),

    "en": (
        "Article Title: {topic}\n"
        "Text: '{context_text}'\n\n"
        "Your task is to write a 'Who Wants to Be a Millionaire' style trivia question.\n"
        "CRITICAL RULES:\n"
        "1. VALUE SELECTION (Priorities):\n"
        "   - BEST: Physical quantities (e.g., height in meters, weight in kg, speed in km/h, temperature), statistics (population, percentages).\n"
        "   - LAST RESORT: Year/Date. Ask about a year ONLY if there are absolutely no other numbers in the text. Dates are usually boring.\n"
        "2. ANTI-META FILTER (Most Important!):\n"
        "   - DO NOT ask about the text structure (e.g., 'How many examples are listed?').\n"
        "   - If the text lists items (e.g., '3 types of animals'), IGNORE THAT NUMBER. Find another one.\n"
        "3. UNIT: The question MUST specify the unit (e.g., 'how many meters', 'in degrees', 'what percentage').\n"
        "4. ANSWER: Must be a pure number (int or float), no text.\n"
        "5. If no factual number (other than counts of examples) is found -> RETURN is_relevant: false.\n\n"
        "Return ONLY JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"What is the maximum speed of this animal in km/h?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    ),
}

RELEVANCE_PROMPT_TEMPLATE = {
    "pl": (
        "Jesteś surowym sędzią kategorii. Twoim zadaniem jest ocena, czy dany TEMAT pasuje do KATEGORII.\n"
        "Kategoria: '{category_name}'\n"
        "Temat do oceny: '{topic}'\n\n"
        "ZASADY:\n"
        "1. Zwróć FALSE, jeśli temat to fikcja (film, gra, postać fikcyjna), a kategoria jest naukowa/geograficzna.\n"
        "2. Zwróć FALSE, jeśli temat to 'Lista...', 'Spis...', 'Kalendarium...' lub 'Ujednoznacznienie'.\n"
        "3. Zwróć FALSE, jeśli temat jest ewidentnie z innej dziedziny (np. 'Madonna (piosenkarka)' w kategorii 'Geografia').\n"
        "4. Jeśli temat brzmi wiarygodnie dla tej kategorii -> Zwróć TRUE.\n\n"
        "Zwróć TYLKO JSON: {{ \"is_relevant\": true }} lub {{ \"is_relevant\": false }}"
    ),
    "en": (
        "You are a strict category judge. Evaluate if the TOPIC fits the CATEGORY.\n"
        "Category: '{category_name}'\n"
        "Topic to evaluate: '{topic}'\n\n"
        "RULES:\n"
        "1. Return FALSE if topic is fiction (movie, game) but category is scientific/geographic.\n"
        "2. Return FALSE for Lists, Timelines, or Disambiguations.\n"
        "3. Return FALSE if the topic clearly belongs to another field.\n"
        "4. If likely relevant -> Return TRUE.\n\n"
        "Return ONLY JSON: {{ \"is_relevant\": true }} or {{ \"is_relevant\": false }}"
    )
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

    def find_article_title(self, category: WikiCategory, language: Language) -> Optional[str]:
        print(f"   -> Szukam w Wikipedii tematów dla: {category.name}...")
        
        if not category.keywords:
            return None
        
        keyword = random.choice(category.keywords)
        try:
            results = wikipedia.search(keyword, results=50)
            if not results:
                return None
            
            random.shuffle(results)
            return random.choice(results)
            
            # for potential_topic in results:
                    
            #         lower = potential_topic.lower()
            #         if any(x in lower for x in ["lista ", "list of ", "spis ", "timeline ", "ujednoznacznienie"]):
            #             continue

            #         if self.check_relevance(potential_topic, category.name, language):
            #             return potential_topic
        except Exception:
            return None

    def check_relevance(self, str, topic: str, category_name: str, language: Language) -> bool:
        lang_key = language.value
        prompt_template = RELEVANCE_PROMPT_TEMPLATE.get(lang_key, RELEVANCE_PROMPT_TEMPLATE["en"])
        print(f"  2137...")
        
        user_prompt = prompt_template.format(
            category_name=category_name,
            topic=topic,
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a category judge."},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.1, # Bardzo nisko! Chcemy logicznej, chłodnej oceny.
                max_tokens=100   # Oszczędzamy tokeny, odpowiedź będzie krótka
            )
            data = json.loads(response.choices[0].message.content)
            
            is_valid = data.get("is_relevant", False)
            if not is_valid:
                print(f"🚫 SĘDZIA: Odrzucono temat '{topic}' dla kategorii '{category_name}'.")
            else:
                print(f"✅ SĘDZIA: Zaakceptowano temat '{topic}'.")
                
            return is_valid
        except Exception as e:
            print(f"❌ Relevance Check Error: {e}")
            return False
        
    def generate_question_with_ai(self, context_text: str, topic: str, language: Language) -> Optional[dict]:

        lang_key = language.value
        
        system_prompt = SYSTEM_PROMPT_TEMPLATE.get(lang_key, SYSTEM_PROMPT_TEMPLATE["en"])

        raw_user_prompt = QUESTION_PROMPT_TEMPLATE.get(lang_key, QUESTION_PROMPT_TEMPLATE["en"])
        user_prompt = raw_user_prompt.format(topic = topic, context_text=context_text[:1500])

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Lub "gpt-4o-mini" (tańszy i szybszy)
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

            title = self.find_article_title(category_obj, language)
            if not title: continue

            try:
                page = wikipedia.page(title, auto_suggest=False)
                content = page.summary
                content = self.remove_brackets(content)

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
