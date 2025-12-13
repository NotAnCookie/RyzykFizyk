import pytest
from schemas.enums import *
from schemas.question import Question
from schemas.game_session import GameSession

@pytest.fixture
def fake_questions():
    return [
        Question(id=1, text="Generated 1", category=Category.RANDOM, language=Language.PL, answer=None)
    ]

@pytest.fixture
def session_empty_init():
    return GameSession(
        id=1,
        player=None,
        questions=[],
        answers=[],
        currentQuestion=0,
        language=Language.PL,
        category=Category.RANDOM,
        state=SessionState.INIT
    )