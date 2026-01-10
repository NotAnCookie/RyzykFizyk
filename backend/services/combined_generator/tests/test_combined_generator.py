from services.combined_generator.src.combined_generator import CombinedGenerator
from services.trivia_generator.src.models import TriviaResult
from services.question_generator.src.models import Question
from services.trivia_generator.src.communication.api_client import APIClient
from services.question_generator.src.enums import Language


class FakeAPIClient:
    def get_completion(self, prompt: str) -> str:
        # Return a deterministic JSON payload
        return '''{
            "question": {
                "is_relevant": true,
                "question_text": "What is the highest mountain in the world in meters?",
                "answer_number": 8848
            },
            "trivia": {
                "trivia_text": "Mount Everest was first summited in 1953 (https://en.wikipedia.org/wiki/Mount_Everest)",
                "source": "https://en.wikipedia.org/wiki/Mount_Everest"
            }
        }'''


def test_combined_generator_basic():
    client = FakeAPIClient()
    cg = CombinedGenerator(api_client=client)

    # Use a known category (geography) and language
    res = cg.generate("geography", Language.EN)
    assert res is not None
    q, trivia = res
    assert isinstance(q, Question)
    assert q.question_text.startswith("What is the highest mountain")
    assert q.answer == "8848"
    assert isinstance(trivia, TriviaResult)
    assert "Everest" in trivia.trivia
    assert trivia.source.url.startswith("https://")
