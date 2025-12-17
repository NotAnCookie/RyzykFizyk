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
async def test_create_and_start_session(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category_id=CategoryEnum.GEOGRAPHY
    )

    assert session.state.name == "INIT"

    await session_manager.start_session(session.id)

    assert session.state.name == "IN_PROGRESS"
    assert len(session.questions) == 1
    assert session.questions[0].id == 1


@pytest.mark.asyncio
async def test_get_next_question_generates_questions(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category_id=CategoryEnum.GEOGRAPHY
    )

    await session_manager.start_session(session.id)

    q2 = await session_manager.get_next_question(session.id)

    assert q2.text == "Q2"
    assert q2.id == 2


from schemas.player import PlayerAnswer

@pytest.mark.asyncio
async def test_submit_answer_updates_question(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category_id=CategoryEnum.GEOGRAPHY
    )

    await session_manager.start_session(session.id)
    q = await session_manager.get_next_question(session.id)

    await session_manager.submit_answer(
        session.id,
        PlayerAnswer(questionId=q.id, playerId=test_player.id, value=42)
    )

    question = session.questions[1]
    assert question.sourceUrl == "https://example.com"
    assert question.trivia == "Some trivia"
    assert len(session.answers) == 1


@pytest.mark.asyncio
async def test_submit_answer_not_summary_too_early(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category_id=CategoryEnum.GEOGRAPHY
    )

    await session_manager.start_session(session.id)
    q = await session_manager.get_next_question(session.id)

    await session_manager.submit_answer(
        session.id,
        PlayerAnswer(questionId=q.id, playerId=test_player.id, value=10)
    )

    assert session.state.name == "IN_PROGRESS"


from schemas.game_session import MAX_QUESTIONS

@pytest.mark.asyncio
async def test_full_game_flow(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category_id=CategoryEnum.GEOGRAPHY
    )

    await session_manager.start_session(session.id)

    for _ in range(MAX_QUESTIONS-1):
        q = await session_manager.get_next_question(session.id)
        assert q is not None
        await session_manager.submit_answer(
            session.id,
            PlayerAnswer(questionId=q.id, playerId=test_player.id, value=1)
        )

    q = await session_manager.get_next_question(session.id)
    assert q is None
    assert session.state.name == "SUMMARY"
    assert session.currentQuestion == MAX_QUESTIONS


@pytest.mark.asyncio
async def test_invalid_session_id_raises(session_manager):
    with pytest.raises(KeyError):
        await session_manager.get_next_question(999)


