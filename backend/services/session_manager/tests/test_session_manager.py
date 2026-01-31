import pytest
from schemas.enums import Language, Category, SessionState, CategoryEnum
from schemas.player import PlayerAnswer
from schemas.question import Question

def debug_session(session):
    print("\n===== DEBUG SESSION =====")
    print("state:", session.state)
    print("currentQuestion:", session.currentQuestion)
    print("total questions:", len(session.questions))
    print("questions:", [q.text for q in session.questions])
    print("=========================\n")


@pytest.mark.asyncio
async def test_invalid_session_id_raises(session_manager):
    with pytest.raises(KeyError):
        await session_manager.get_next_question(999)


