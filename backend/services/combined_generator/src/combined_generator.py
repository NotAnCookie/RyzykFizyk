import json
import re
import random
import wikipedia
from typing import Optional, Tuple

# Importy modeli i enumów
from services.question_generator.src.models import Question
from services.question_generator.src.enums import Language
from services.question_generator.src.categories import CATEGORIES_CONFIG, WikiCategory
from services.trivia_generator.src.models import TriviaResult, SourceMetadata

# Importy klientów
from services.trivia_generator.src.communication.api_client import APIClient
from services.answer_verification.src.wikipedia_client import WikipediaClient

# --- NOWY, ZINTEGROWANY PROMPT (ONE-SHOT) ---
COMBINED_PROMPT_TEMPLATE = {
    "pl": (
        "Jesteś precyzyjnym generatorem quizów. Działasz wyłącznie na podstawie poniższego tekstu.\n"
        "TYTUŁ: {topic}\n"
        "TEKST ŹRÓDŁOWY: '{context_text}'\n\n"
        "Twoim zadaniem jest wygenerowanie obiektu JSON zawierającego (1) Pytanie numeryczne i (2) Ciekawostkę.\n\n"
        "ZASADY DLA PYTANIA ('question'):\n"
        "1. PRIORYTET DANYCH: Szukaj wielkości fizycznych (metry, kg, km/h, %) lub statystyk. Pytaj o ROK/DATĘ tylko w ostateczności, jeśli brak innych liczb.\n"
        "2. FILTR ANTY-META (Krytyczne!): ZABRANIA SIĘ pytać o strukturę tekstu (np. 'Ile przykładów wymieniono?'). Jeśli tekst wylicza elementy, IGNORUJ tę liczbę.\n"
        "3. JEDNOSTKA: Pytanie musi zawierać jednostkę (np. 'w metrach', 'w tysiącach').\n"
        "4. ODPOWIEDŹ: Musi być czystą liczbą (int lub float).\n"
        "5. Jeśli brak sensownych liczb -> ustaw 'is_relevant': false.\n\n"
        "ZASADY DLA CIEKAWOSTKI ('trivia'):\n"
        "1. TREŚĆ: Ma być zabawna lub nietypowa, inspirowana tematem.\n"
        "2. OGRANICZENIA: Max 1 krótkie zdanie. NIE UŻYWAJ LICZB w ciekawostce. NIE ODPOWIADAJ na pytanie w treści ciekawostki.\n"
        "3. ŹRÓDŁO: Jeśli znasz, dodaj w nawiasie (np. Wikipedia).\n\n"
        "PRZYKŁAD IDEALNEGO WYNIKU (JSON):\n"
        "{{\n"
        "  \"question\": {{\n"
        "    \"is_relevant\": true,\n"
        "    \"question_text\": \"Jaka jest maksymalna głębokość Rowu Mariańskiego w metrach?\",\n"
        "    \"answer_number\": 10994\n"
        "  }},\n"
        "  \"trivia\": {{\n"
        "    \"trivia_text\": \"Na dnie tego rowu ciśnienie jest ponad tysiąc razy większe niż na poziomie morza.\",\n"
        "    \"source\": null\n"
        "  }}\n"
        "}}\n\n"
        "Teraz wygeneruj JSON dla podanego tekstu:"
    ),
    "en": (
        "You are a precise quiz generator working ONLY based on the text below.\n"
        "TITLE: {topic}\n"
        "SOURCE TEXT: '{context_text}'\n\n"
        "Your task is to generate a JSON object containing (1) A numeric Question and (2) A Trivia fact.\n\n"
        "RULES FOR QUESTION ('question'):\n"
        "1. PRIORITY: Look for physical quantities (meters, kg, km/h, %) or stats. Ask about YEAR/DATE only as a last resort.\n"
        "2. ANTI-META FILTER (Critical!): DO NOT ask about text structure (e.g., 'How many examples are listed?'). If the text lists items, IGNORE that count.\n"
        "3. UNIT: The question must specify the unit (e.g., 'in meters', 'in thousands').\n"
        "4. ANSWER: Must be a pure number (int or float).\n"
        "5. If no valid numbers found -> set 'is_relevant': false.\n\n"
        "RULES FOR TRIVIA ('trivia'):\n"
        "1. CONTENT: Funny or unusual fact inspired by the topic.\n"
        "2. CONSTRAINTS: Max 1 short sentence. DO NOT USE NUMBERS in trivia. DO NOT ANSWER the question in the trivia.\n"
        "3. SOURCE: If known, include in parentheses.\n\n"
        "ONE-SHOT IDEAL OUTPUT (JSON):\n"
        "{{\n"
        "  \"question\": {{\n"
        "    \"is_relevant\": true,\n"
        "    \"question_text\": \"What is the maximum depth of the Mariana Trench in meters?\",\n"
        "    \"answer_number\": 10994\n"
        "  }},\n"
        "  \"trivia\": {{\n"
        "    \"trivia_text\": \"At the bottom of this trench, the pressure is over a thousand times greater than at sea level.\",\n"
        "    \"source\": null\n"
        "  }}\n"
        "}}\n\n"
        "Now generate JSON for the provided text:"
    )
}

class CombinedGenerator:
    def __init__(self, api_client: Optional[APIClient] = None, wiki_client: Optional[WikipediaClient] = None):
        self.api_client = api_client or APIClient()
        self.wiki_client = wiki_client or WikipediaClient()

    def remove_brackets(self, text: str) -> str:
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\(.*?\)", "", text)
        return text

    def resolve_category(self, category_id: str, language: Language) -> WikiCategory:
        main_config = CATEGORIES_CONFIG.get(category_id)
        if not main_config:
            main_config = list(CATEGORIES_CONFIG.values())[0]

        lang_code = language.value
        lang_data = main_config.get(lang_code, main_config.get("en"))
        return WikiCategory(name=lang_data["name"], keywords=lang_data["keywords"])

    def find_article_title(self, category: WikiCategory, language: Language) -> Optional[str]:
        if not category.keywords:
            return None
        keyword = random.choice(category.keywords)
        try:
            results = wikipedia.search(keyword, results=50)
            if not results:
                return None
            random.shuffle(results)
            return random.choice(results)
        except Exception:
            return None

    def _build_prompt(self, topic: str, context_text: str, language: Language) -> str:
        """
        Buduje jeden spójny prompt przy użyciu szablonu One-Shot.
        """
        lang_key = language.value
        template = COMBINED_PROMPT_TEMPLATE.get(lang_key, COMBINED_PROMPT_TEMPLATE.get("en"))
        
        # Formatujemy prompt. Przycinamy tekst, aby oszczędzać tokeny, 
        # ale 2000 znaków to wystarczająco na dobry kontekst.
        return template.format(topic=topic, context_text=context_text[:2000])

    def generate_question_with_ai(self, context_text: str, topic: str, language: Language) -> Optional[dict]:
        """
        Wysyła zapytanie do OpenAI i zwraca sparsowany słownik z pytaniem i trivią.
        """
        full_prompt = self._build_prompt(topic, context_text, language)

        try:
            response = self.api_client.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    # Krótki system prompt ustawiający format JSON
                    {"role": "system", "content": "You are a helpful API that outputs strictly valid JSON."},
                    {"role": "user", "content": full_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Mapowanie odpowiedzi JSON na wewnętrzną strukturę
            qd = data.get("question", {})
            td = data.get("trivia", {})

            # Sprawdzenie "is_relevant" - jeśli AI uznało, że nie ma liczb, zwracamy None
            if qd.get("is_relevant") is False:
                return None

            return {
                "question": qd.get("question_text"),
                "answer": qd.get("answer_number"),
                "trivia": td.get("trivia_text"),
                # AI może zwrócić źródło, ale my i tak nadpiszemy je prawdziwym URL z Wiki
                "search_query": td.get("source") 
            }
        except Exception as e:
            print(f"❌ OpenAI Error (Combined): {e}")
            return None

    def generate(self, category_id: str, language: Language = Language.EN) -> Optional[Tuple[Question, TriviaResult]]:
        # Ustawiamy język dla biblioteki wikipedia (do wyszukiwania tytułów)
        wikipedia.set_lang(language.value)
        # Ustawiamy język dla naszego klienta (do pobierania treści i URL)
        if self.wiki_client:
            self.wiki_client.language = language

        category_obj = self.resolve_category(category_id, language)

        attempts = 0
        while attempts < 5:
            attempts += 1
            
            # 1. Znajdź losowy temat
            title = self.find_article_title(category_obj, language)
            if not title: continue

            try:
                content = ""
                real_source_url = ""

                # 2. Pobierz treść i URL (Preferujemy WikipediaClient bo daje pewne URL)
                if self.wiki_client:
                    # print(f" 📥 [WikiClient] Pobieram: {title}")
                    page_summary = self.wiki_client.get_page_summary(title)
                    if page_summary:
                        content = page_summary.get("extract", "")
                        # Wyciągamy kanoniczny URL
                        real_source_url = page_summary.get("content_urls", {}).get("desktop", {}).get("page")
                
                # Fallback do biblioteki wikipedia jeśli klient zawiódł
                if not content:
                    page = wikipedia.page(title, auto_suggest=False)
                    content = page.summary
                    real_source_url = page.url

                if not content: continue

                # Czyszczenie tekstu
                content = self.remove_brackets(content)

                # 3. Generowanie przez AI (Jeden strzał)
                ai_result = self.generate_question_with_ai(content, title, language)
                
                if not ai_result or not ai_result.get("question"):
                    continue

                # 4. Parsowanie i walidacja liczby
                final_answer = 0.0
                try:
                    ans = ai_result.get("answer")
                    if isinstance(ans, str):
                        # Obsługa "1,200.50" -> 1200.5
                        final_answer = float(ans.replace(',', '').replace(' ', ''))
                    else:
                        final_answer = float(ans)
                except (ValueError, TypeError):
                    # Jeśli odpowiedź nie jest liczbą, pomijamy to pytanie
                    continue

                # 5. Budowanie obiektów
                q = Question(
                    category=category_id,
                    language=language,
                    question_text=ai_result["question"],
                    topic=title,
                    answer=final_answer,
                )

                trivia_text = ai_result.get("trivia", "")
                
                # Jeśli nie mamy URL z WikiClienta, budujemy go ręcznie jako fallback
                if not real_source_url:
                     lang_str = language.value if hasattr(language, 'value') else language
                     real_source_url = f"https://{lang_str}.wikipedia.org/wiki/{title.replace(' ', '_')}"

                trivia = TriviaResult(
                    trivia=trivia_text.strip(),
                    source=SourceMetadata(url=real_source_url)
                )

                return q, trivia

            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
            except Exception as e:
                print(f"⚠️ Błąd w pętli generatora: {e}")
                continue

        return None