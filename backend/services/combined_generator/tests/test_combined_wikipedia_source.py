from services.combined_generator.src.combined_generator import CombinedGenerator
from services.trivia_generator.src.models import TriviaResult
from services.question_generator.src.models import Question

class FakeAPIClientNoSource:
    def get_completion(self, prompt: str) -> str:
        return '''{
            "question": {
                "is_relevant": true,
                "question_text": "What is the tallest mountain?",
                "answer_number": 8848
            },
            "trivia": {
                "trivia_text": "Mount Everest was first summited in 1953.",
                "source": null
            }
        }'''

class FakeWikiClient:
    def search_page(self, question: str):
        return "Mount Everest"
    def get_page_summary(self, title: str):
        return {"content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Mount_Everest"}}}


def test_combined_generator_falls_back_to_wikipedia():
    api = FakeAPIClientNoSource()
    wiki = FakeWikiClient()

    cg = CombinedGenerator(api_client=api, wiki_client=wiki)
    res = cg.generate("geography")
    assert res is not None
    q, trivia = res
    assert isinstance(q, Question)
    assert trivia.source.url == "https://en.wikipedia.org/wiki/Mount_Everest"
