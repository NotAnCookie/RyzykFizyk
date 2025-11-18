import pytest
from wikipedia_client import WikipediaClient
from verifier import AnswerVerifier
from schemas import VerificationRequest
from enums import Language

pytestmark = pytest.mark.integration

def test_answer_verifier_integration():
    # Arrange
    wiki_client = WikipediaClient(language=Language.PL.value)
    verifier = AnswerVerifier(wikipedia_client=wiki_client)

    request = VerificationRequest(
        question_text="Ile kilometrów ma Wisła?",
        language=Language.PL.value,
        numeric_answer=1022
    )

    # Act
    result = verifier.verify(request)

    # Printujemy wynik
    print(f"Verified answer: {result.verified_answer}")
    print(f"Source: {result.source}")

    # Jeśli nic nie znaleziono
    if result.source is None:
        assert result.verified_answer is None
        return

    # Jeśli coś znaleziono
    assert result.source.url is not None
    assert result.source.title is not None
    assert isinstance(result.verified_answer, (int, float))

