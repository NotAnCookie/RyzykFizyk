import pytest
from unittest.mock import MagicMock
from verifier import AnswerVerifier
from models import VerificationRequest

@pytest.fixture
def wikipedia_mock():
    mock = MagicMock()
    mock.search_page.return_value = "Speed_of_light"
    mock.get_page_summary.return_value = {
        "title": "Speed of light",
        "extract": "The speed of light is 299792458 m/s.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/..."}}
    }
    return mock


@pytest.fixture
def answer_verifier(wikipedia_mock):
    return AnswerVerifier(wikipedia_client=wikipedia_mock)

@pytest.mark.google
def test_verify_source_found(answer_verifier):
    # Arrange
    req = VerificationRequest(
        question_text="What is the speed of light?",
        language="EN",
        numeric_answer=299792458
    )

    # Act
    result = answer_verifier.verify(req)

    # Assert
    assert result.verified_answer == 299792458
    assert result.source.title == "Speed of light"
    assert result.source.url == "https://en.wikipedia.org/..."

@pytest.mark.google
def test_verify_returns_empty_result_when_no_summary(answer_verifier, wikipedia_mock):
    # Arrange
    wikipedia_mock.get_page_summary.return_value = None

    req = VerificationRequest(
        question_text="speed of light",
        language="EN",
        numeric_answer=1
    )

    # Act
    result = answer_verifier.verify(req)

    # Assert
    assert result is not None
    assert result.source is None
    assert result.verified_answer is None

@pytest.mark.google
def test_verify_returns_empty_when_page_not_found(answer_verifier, wikipedia_mock):
    # ARRANGE
    wikipedia_mock.search_page.return_value = None

    req = VerificationRequest(
        question_text="Unknown question",
        language="EN",
        numeric_answer=42
    )

    # ACT
    result = answer_verifier.verify(req)

    # ASSERT
    assert result.verified_answer is None
    assert result.source is None




