import pytest
from schemas.enums import Language, Category, SessionState
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
        category=Category.RANDOM
    )

    assert session.state == SessionState.INIT

    # start sesji → generator wypełni 7 pytań
    started = await session_manager.start_session(session.id)

    assert started.state == SessionState.IN_PROGRESS
    assert len(started.questions) == 7


@pytest.mark.asyncio
async def test_get_next_question(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category=Category.RANDOM
    )

    # ręcznie generujemy 2 pytania dla testu
    session.questions = await session_manager.question_generator.generate(
        language=session.language,
        category=session.category,
        amount=2
    )
    session.state = SessionState.IN_PROGRESS

    # ACT
    q1 = await session_manager.get_next_question(session.id)
    assert q1.text == "Q1"
    assert session.currentQuestion == 1


@pytest.mark.asyncio
async def test_submit_answer_updates_question(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category=Category.RANDOM
    )

    session.questions = await session_manager.question_generator.generate(
        language=session.language,
        category=session.category,
        amount=1
    )
    session.state = SessionState.IN_PROGRESS

    answer = PlayerAnswer(questionId=1, playerId=1, value=4)

    # ACT
    await session_manager.submit_answer(session.id, answer)

    # ASSERT
    q = session.questions[0]
    assert q.sourceUrl == "https://example.com" 
    assert q.trivia == "Some trivia"
    assert session.answers[0].value == 4



@pytest.mark.asyncio
async def test_start_session_calls_generator_correctly(session_manager, test_player, fake_question_generator):
    session = session_manager.create_session(
        player=test_player,
        language=Language.EN,
        category=Category.HISTORY
    )

    await session_manager.start_session(session.id)

    fake_question_generator.generate.assert_awaited_once_with(
        language=Language.EN,
        category=Category.HISTORY,
        amount=7
    )


@pytest.mark.asyncio
async def test_submit_answer_not_summary_too_early(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category=Category.RANDOM
    )

    session.questions = await session_manager.question_generator.generate(
        language=session.language,
        category=session.category,
        amount=2
    )
    session.state = SessionState.IN_PROGRESS
    session.currentQuestion = 0

    await session_manager.submit_answer(
        session.id,
        PlayerAnswer(questionId=1, playerId=1, value=100)
    )

    # Po jednym pytaniu → nadal IN_PROGRESS
    assert session.state == SessionState.IN_PROGRESS


@pytest.mark.asyncio
async def test_full_game_flow(session_manager, test_player):
    session = session_manager.create_session(
        player=test_player,
        language=Language.PL,
        category=Category.RANDOM
    )

    # start → generator wypełni 7 pytań
    await session_manager.start_session(session.id)
    assert len(session.questions) == 7

    # odpowiedź na wszystkie pytania
    for _ in range(7):
        q = await session_manager.get_next_question(session.id)
        assert q is not None

        await session_manager.submit_answer(
            session.id,
            PlayerAnswer(questionId=q.id, playerId=test_player.id, value=1)
        )

    # brak kolejnych pytań → summary
    q = await session_manager.get_next_question(session.id)

    debug_session(session)

    print("Returned question:", q)
    print("current question index:", session.currentQuestion)
    print("questions list:", session.questions)
    assert q is None
    assert session.state == SessionState.SUMMARY
    assert session.currentQuestion == 7


@pytest.mark.asyncio
async def test_invalid_session_id_raises(session_manager):
    with pytest.raises(KeyError):
        await session_manager.get_next_question(999)

