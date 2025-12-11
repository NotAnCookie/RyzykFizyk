import os
import pytest
from communication.api_client import *
from generator.trivia_generator import *

@pytest.mark.ai
def test_trivia_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set, skipping AI tests")

    print("Tworzę APIClient z kluczem:", api_key[:4] + "****")
    api_client = APIClient(api_key=api_key)

    print("Tworzę TriviaGenerator")
    generator = TriviaGenerator(api_client=api_client)

    trivia_request = TriviaRequest(
        question_text="Koty",
        language=Language.PL
    )
    print("Wysyłam request:", trivia_request)

    result = generator.generate_trivia(trivia_request)

    print("Otrzymany wynik:", result)
    print("Długość trivia:", len(result.trivia))
    print("Źródło:", result.source)

    assert len(result.trivia) > 0, "Trivia jest pusta, coś poszło nie tak z API"
