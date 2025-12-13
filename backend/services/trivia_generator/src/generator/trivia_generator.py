import re
from typing import Optional
from pydantic import BaseModel
from services.trivia_generator.src.communication.api_client import APIClient
from services.trivia_generator.src.prompts import TRIVIA_PROMPT_TEMPLATE
from services.trivia_generator.src.enums import *
from services.trivia_generator.src.models import *


class TriviaGenerator:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()

    def generate_trivia(self, request: TriviaRequest) -> TriviaResult:
        self._validate_input(request.question_text)

        prompt = self._build_prompt(
            topic=request.question_text,
            language=request.language
        )

        raw_text = self._get_trivia_text(prompt)
        return self._build_trivia_result(raw_text)

    def _validate_input(self, text: str):
        if not text or len(text.strip()) < 3:
            raise ValueError("Treść pytania jest zbyt krótka lub pusta.")

    def _build_prompt(self, topic: str, language: Language) -> str:
        template = TRIVIA_PROMPT_TEMPLATE.get(language.value, TRIVIA_PROMPT_TEMPLATE["pl"])
        return template.format(topic=topic)


    def _get_trivia_text(self, prompt: str) -> str:
        return self.api_client.get_completion(prompt)

    def _extract_source(self, text: str) -> Optional[str]:
        match = re.search(r"\((https?://[^\s)]+)\)", text)
        return match.group(1) if match else None

    def _build_trivia_result(self, trivia_text: str) -> TriviaResult:
        source_url = self._extract_source(trivia_text)
        source = SourceMetadata(url=source_url) if source_url else None
        return TriviaResult(trivia=trivia_text.strip(), source=source)

