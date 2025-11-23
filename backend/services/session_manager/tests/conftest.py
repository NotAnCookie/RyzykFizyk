import pytest
from unittest.mock import AsyncMock, Mock

from services.session_manager.src.session_manager import SessionManager
from schemas.player import Player
from schemas.enums import Language, Category
from schemas.question import Question


# @pytest.fixture
# def mock_question_generator():
#     gen = AsyncMock()
#     gen.generate = AsyncMock(return_value=[
#         Question(id=1, text="Q1", category=Category.RANDOM, language=Language.PL),
#         Question(id=2, text="Q2", category=Category.RANDOM, language=Language.PL),
#     ])
#     return gen

@pytest.fixture
def fake_question_generator():
    async def generate(language, category, amount):
        return [
            Question(
                id=i,
                text=f"Q{i}",
                category=category,
                language=language,
                answer=1.0,
                trivia=None,
                sourceUrl=None
            )
            for i in range(1, amount + 1)
        ]

    mock = Mock()
    mock.generate = AsyncMock(side_effect=generate)
    return mock




@pytest.fixture
def mock_verify_service():
    verify = AsyncMock()
    verify.verify = AsyncMock(return_value=type(
        "VerifyResult", (), {"verified_answer": True, "source": "https://example.com"}
    )())
    return verify


@pytest.fixture
def mock_trivia_service():
    trivia = AsyncMock()
    trivia.generate = AsyncMock(return_value="Some trivia")
    return trivia


@pytest.fixture
def session_manager(fake_question_generator, mock_verify_service, mock_trivia_service):
    return SessionManager(
        question_generator=fake_question_generator,
        verify_service=mock_verify_service,
        trivia_service=mock_trivia_service
    )


@pytest.fixture
def test_player():
    return Player(id=1, email="test@mail.com", name="Tester")
