import pytest
from generator.trivia_generator import TriviaGenerator

class MockAPIClient:
    def get_completion(self, prompt):
        return "Ciekawostka testowa (https://example.com)."

@pytest.fixture
def mock_api_client():
    return MockAPIClient()

@pytest.fixture
def trivia_generator(mock_api_client):
    """Tworzy instancję klasy z gotowym MockAPIClient"""
    return TriviaGenerator(api_client=mock_api_client)
