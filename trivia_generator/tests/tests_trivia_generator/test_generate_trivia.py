import pytest
from src.trivia_generator import TriviaGenerator

class MockAPIClient:
    def get_completion(self, prompt):
        return "Ciekawostka testowa o kosmosie (https://pl.wikipedia.org/wiki/Kosmos)."

def test_generate_trivia_valid_input():
    generator = TriviaGenerator(api_client=MockAPIClient())
    result = generator.generate_trivia("kosmos")
    assert "Ciekawostka" in result["trivia"]
    assert result["source"].startswith("https://")

def test_generate_trivia_invalid_input():
    generator = TriviaGenerator(api_client=MockAPIClient())
    with pytest.raises(ValueError):
        generator.generate_trivia("")

# do innego pliku
# def test_generate_json_response():
#     generator = TriviaGenerator(api_client=MockAPIClient())
#     json_str = generator.generate_json_response("koty")
#     assert '"trivia":' in json_str
#     assert '"source":' in json_str
