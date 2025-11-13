# src/trivia_generator.py

from typing import Optional, Dict
from src.communication.api_client import APIClient
from src.prompts import TRIVIA_PROMPT_TEMPLATE
from src.communication.json_inout import write_output


class TriviaGenerator:
    """Moduł generujący krótkie ciekawostki na podstawie pytania lub tematu."""

    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()

    def generate_trivia(self, question_text: str) -> Dict[str, str]:
        if not question_text or len(question_text.strip()) < 3:
            raise ValueError("Treść pytania jest zbyt krótka lub pusta.")

        prompt = TRIVIA_PROMPT_TEMPLATE.format(topic=question_text)
        trivia_text = self.api_client.get_completion(prompt)

        source = self._extract_source(trivia_text)
        return {"trivia": trivia_text.strip(), "source": source}

    def generate_json_response(self, question_text: str) -> str:
        """Generuje wynik i zwraca go w formacie JSON."""
        data = self.generate_trivia(question_text)
        return write_output(**data)

    def _extract_source(self, text: str) -> Optional[str]:
        import re
        match = re.search(r"\((https?://[^\s)]+)\)", text)
        return match.group(1) if match else None
