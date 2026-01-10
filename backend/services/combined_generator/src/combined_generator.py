import json
import re
import random
import wikipedia
from typing import Optional, Tuple
from services.question_generator.src.models import Question
from services.question_generator.src.enums import Language
from services.question_generator.src.categories import CATEGORIES_CONFIG, WikiCategory
from services.trivia_generator.src.communication.api_client import APIClient
from services.answer_verification.src.wikipedia_client import WikipediaClient
from services.trivia_generator.src.prompts import TRIVIA_PROMPT_TEMPLATE
from services.question_generator.src.prompts import QUESTION_PROMPT_TEMPLATE, SYSTEM_PROMPT_TEMPLATE
from services.trivia_generator.src.models import TriviaResult, SourceMetadata


COMBINED_PROMPT_TEMPLATE = {
    "pl": (
        "Dostajesz TYTUŁ artykułu: {topic}\n" 
        "Tekst: '{context_text}'\n\n"
        "Twoim zadaniem jest (1) wygenerować JEDNO istotne pytanie liczbowe w formacie JSON i (2) jedną krótką ciekawostkę (max 1 zdanie) inspirowaną tym tematem.\n"
        "KRYTYCZNE ZASADY DLA PYTANIA:\n"
        " - Priorytet: wielkości fizyczne/statystyki. Ostateczność: rok/date tylko jeśli brak innych liczb.\n"
        " - Odpowiedź MUSI być czystą liczbą (int lub float). Jeśli nie znajdziesz sensownej liczby, ustaw is_relevant=false.\n"
        "KRYTYCZNE ZASADY DLA TRIVII:\n"
        " - Jedno krótkie zdanie, bez liczb. Jeżeli masz link do źródła, dołącz go w nawiasie po zdaniu.\n\n"
        "ZWRÓĆ TYLKO I WYŁĄCZNIE PRAWIDŁOWY JSON W FORMACIE:\n"
        "{{\n"
        "  \"question\": {{\n"
        "    \"is_relevant\": true,\n"
        "    \"question_text\": \"...\",\n"
        "    \"answer_number\": 123\n"
        "  }},\n"
        "  \"trivia\": {{\n"
        "    \"trivia_text\": \"...\",\n"
        "    \"source\": \"https://...\"\n"
        "  }}\n"
        "}}"
    ),
    "en": (
        "Article Title: {topic}\n"
        "Text: '{context_text}'\n\n"
        "Your task: (1) generate ONE numeric trivia question in JSON format and (2) one short trivia sentence (max 1 sentence) inspired by the topic.\n"
        "QUESTION RULES:\n"
        " - Priority: physical quantities / statistics. Year/date only if no other numbers.\n"
        " - Answer MUST be a pure number (int or float). If none: is_relevant=false.\n"
        "TRIVIA RULES:\n"
        " - One short sentence, no numbers. If you have a source link, include it in parentheses.\n\n"
        "RETURN ONLY VALID JSON IN THE FORMAT:\n"
        "{{\n"
        "  \"question\": {{\n"
        "    \"is_relevant\": true,\n"
        "    \"question_text\": \"...\",\n"
        "    \"answer_number\": 123\n"
        "  }},\n"
        "  \"trivia\": {{\n"
        "    \"trivia_text\": \"...\",\n"
        "    \"source\": \"https://...\"\n"
        "  }}\n"
        "}}"
    ),
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

    def _extract_source(self, text: str) -> Optional[str]:
        match = re.search(r"\((https?://[^\s)]+)\)", text)
        return match.group(1) if match else None

    def _build_prompt(self, topic: str, context_text: str, language: Language) -> str:
        """Build prompt by reusing existing system & question templates plus trivia prompt."""
        lang_key = language.value

        # system prompt (general role)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.get(lang_key, SYSTEM_PROMPT_TEMPLATE.get("en", ""))

        # question prompt (rules & JSON structure for question)
        question_prompt_template = QUESTION_PROMPT_TEMPLATE.get(lang_key, QUESTION_PROMPT_TEMPLATE.get("en", ""))
        question_prompt = question_prompt_template.format(topic=topic, context_text=context_text[:1500])

        # trivia prompt (short sentence rules)
        trivia_prompt = TRIVIA_PROMPT_TEMPLATE.get(lang_key, TRIVIA_PROMPT_TEMPLATE.get("en", ""))

        # Compose final prompt: system role + question task + trivia task + request for combined JSON
        final = (
            f"{system_prompt}\n\n"
            f"{question_prompt}\n\n"
            f"{trivia_prompt}\n\n"
            "Now return a single JSON object containing two keys: 'question' (an object with is_relevant, question_text, answer_number) and 'trivia' (an object with trivia_text and optional source). Return only valid JSON."
        )

        return final

    def generate(self, category_id: str, language: Language = Language.EN) -> Optional[Tuple[Question, TriviaResult]]:
        wikipedia.set_lang(language.value)

        category_obj = self.resolve_category(category_id, language)

        attempts = 0
        while attempts < 5:
            attempts += 1
            title = self.find_article_title(category_obj, language)
            if not title:
                continue

            try:
                page = wikipedia.page(title, auto_suggest=False)
                content = page.summary
                content = self.remove_brackets(content)

                prompt = self._build_prompt(topic=title, context_text=content, language=language)

                raw = self.api_client.get_completion(prompt)

                # Expecting JSON only — try to parse
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    # Try to extract JSON blob from text
                    m = re.search(r"\{.*\}", raw, re.S)
                    if not m:
                        continue
                    data = json.loads(m.group(0))

                qd = data.get("question")
                td = data.get("trivia")
                if not qd or not qd.get("question_text"):
                    continue

                q = Question(
                    category=category_id,
                    language=language,
                    question_text=qd.get("question_text"),
                    topic=title,
                    answer=str(qd.get("answer_number")),
                )

                trivia_text = td.get("trivia_text") if td else ""
                source_url = (td.get("source") if td else None) or self._extract_source(trivia_text)

                # If no source in trivia, try Wikipedia client to find a relevant page
                if not source_url and self.wiki_client:
                    # Prefer searching by topic then by question text
                    title = None
                    if title is None:
                        title = self.wiki_client.search_page(q.question_text)
                    if not title:
                        title = self.wiki_client.search_page(title if title else q.topic)

                    if title:
                        summary = self.wiki_client.get_page_summary(title)
                        if summary:
                            page = summary.get("content_urls", {}).get("desktop", {}).get("page")
                            if page:
                                source_url = page
                            else:
                                # fallback to canonical construction
                                lang = language.value if hasattr(language, 'value') else language
                                source_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"

                trivia = TriviaResult(trivia=trivia_text.strip() if trivia_text else "", source=SourceMetadata(url=source_url) if source_url else None)

                return q, trivia

            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue

        return None
