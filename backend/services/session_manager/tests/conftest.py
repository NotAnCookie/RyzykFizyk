import pytest
from unittest.mock import AsyncMock, Mock

from services.session_manager.src.session_manager import SessionManager
from schemas.player import Player
from schemas.enums import *
from schemas.question import Question


@pytest.fixture
def fake_question_generator():
    generator = Mock()
    counter = {"i": 0}

    def generate_question(*, language, category):
        counter["i"] += 1
        return SimpleNamespace(
            question_text=f"Q{counter['i']}",
            topic="Test topic",
            category=SimpleNamespace(
                name=category.name
            ),
            language=language,
            answer="1.0" 
        )

    generator.generate_question = Mock(side_effect=generate_question)
    return generator


from types import SimpleNamespace
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_verify_service():
    service = Mock()

    service.verify = Mock(
        return_value=SimpleNamespace(
            correct=True,
            source=SimpleNamespace(
                title="title",
                site_name="Wikipedia",
                url="https://example.com"
            )
        )
    )
    return service




@pytest.fixture
def mock_trivia_service():
    service = Mock()
    service.generate_trivia = Mock(
        return_value=SimpleNamespace(trivia="Some trivia")
    )
    return service



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
