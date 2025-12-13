import os
import pytest
from services.trivia_generator.src.communication.api_client import APIClient

@pytest.mark.ai
def test_api_client_basic():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set, skipping AI tests")

    print("Tworzę APIClient z kluczem:", api_key[:4] + "****")
    client = APIClient(api_key=api_key)

    prompt = "Napisz jedno zdanie o kotach."
    print("Wysyłam prompt:", prompt)

    response_text = client.get_completion(prompt)
    
    print("Odpowiedź z API:", repr(response_text))
    print("Długość odpowiedzi:", len(response_text))

    assert response_text.strip() != "", "Odpowiedź API jest pusta"
