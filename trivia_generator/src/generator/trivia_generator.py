from typing import Optional, Dict
from communication.api_client import APIClient
from prompts import TRIVIA_PROMPT_TEMPLATE
from communication.json_inout import write_output
import re


class TriviaGenerator:
    """Moduł generujący krótkie ciekawostki na podstawie pytania lub tematu."""

    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()

    # ------------------------------------------------------------------
    # PUBLIC API – pozostaje TAKIE JAK TERAZ
    # ------------------------------------------------------------------

    def generate_trivia(self, question_text: str) -> Dict[str, str]:
        """Główna metoda – koordynuje cały proces generowania ciekawostki."""
        self._validate_input(question_text)
        prompt = self._build_prompt(question_text)
        raw_text = self._get_trivia_text(prompt)
        return self._build_trivia_dict(raw_text)

    def generate_json_response(self, question_text: str) -> str:
        """Generuje wynik w formacie JSON."""
        data = self.generate_trivia(question_text)
        return self._serialize_to_json(data)

    # ------------------------------------------------------------------
    # INTERNAL HELPERS – małe funkcje robiące jedną rzecz
    # ------------------------------------------------------------------

    def _validate_input(self, text: str):
        """Sprawdza czy wejście jest poprawne."""
        if not text or len(text.strip()) < 3:
            raise ValueError("Treść pytania jest zbyt krótka lub pusta.")

    def _build_prompt(self, topic: str) -> str:
        """Tworzy prompt do API."""
        return TRIVIA_PROMPT_TEMPLATE.format(topic=topic)

    def _get_trivia_text(self, prompt: str) -> str:
        """Pobiera ciekawostkę z API."""
        return self.api_client.get_completion(prompt)

    def _extract_source(self, text: str) -> Optional[str]:
        """Wyszukuje link w tekście."""
        match = re.search(r"\((https?://[^\s)]+)\)", text)
        return match.group(1) if match else None

    def _build_trivia_dict(self, trivia_text: str) -> Dict[str, str]:
        """Zamienia tekst ciekawostki na gotowy słownik."""
        return {
            "trivia": trivia_text.strip(),
            "source": self._extract_source(trivia_text)
        }

    def _serialize_to_json(self, data: Dict[str, str]) -> str:
        """Konwertuje słownik na JSON przez write_output()."""
        return write_output(**data)
