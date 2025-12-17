import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock
from types import SimpleNamespace

from services.session_manager.src.session_manager import SessionManager
from routers.session_router import get_session_router
from schemas.enums import Language, CategoryEnum


@pytest.fixture
def mock_services():
    question_generator = Mock()
    question_generator.generate_question = Mock(
        side_effect=lambda *, language, category: SimpleNamespace(
            question_text="Q?",
            topic="Test topic",
            category=SimpleNamespace(name=category.name),
            language=language,
            answer="1"
        )
    )

    verify_service = Mock()
    verify_service.verify = Mock(
        return_value=SimpleNamespace(
            correct=True,
            source=SimpleNamespace(url="https://example.com")
        )
    )

    trivia_service = Mock()
    trivia_service.generate_trivia = Mock(
        return_value=SimpleNamespace(trivia="Some trivia")
    )

    return question_generator, verify_service, trivia_service


@pytest.fixture
def app(mock_services):
    qg, vs, ts = mock_services
    manager = SessionManager(qg, vs, ts)

    app = FastAPI()
    app.include_router(get_session_router(manager))
    return app


@pytest.fixture
def client(app):
    return TestClient(app)
