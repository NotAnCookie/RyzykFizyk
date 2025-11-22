import pytest
from unittest.mock import AsyncMock, patch
from schemas.game_session import GameSession, MAX_QUESTIONS
from schemas.enums import SessionState, Language, Category
from schemas.question import Question

class TestNextQuestion:
    @pytest.mark.asyncio
    async def test_next_question_normal_flow(self, session_empty_init):
        # ARRANGE
        questions = [
            Question(id=1, text="Q1", category=Category.RANDOM, language=Language.PL, answer=None),
            Question(id=2, text="Q2", category=Category.RANDOM, language=Language.PL, answer=None),
            Question(id=3, text="Q3", category=Category.RANDOM, language=Language.PL, answer=None),
        ]

        session = session_empty_init
        session.questions = questions

        # ACT
        q1 = await session.nextQuestion()

        # ASSERT
        assert q1.text == "Q1"
        assert session.currentQuestion == 1
        assert session.state == SessionState.IN_PROGRESS


    @pytest.mark.asyncio
    async def test_next_question_uses_generator_when_no_questions(self, session_empty_init,fake_questions):
        # ARRANGE
        session = session_empty_init

        # MOCK generator
        with patch.object(GameSession, "generateQuestions", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = fake_questions

            # ACT
            q1 = await session.nextQuestion()

        # ASSERT
        assert q1.text == "Generated 1"
        assert session.currentQuestion == 1
        assert len(session.questions) == 1
        mock_gen.assert_called_once()


    @pytest.mark.asyncio
    async def test_next_question_generator_returns_none(self, session_empty_init):
        # ARRANGE
        session = session_empty_init

        # MOCK generator
        with patch.object(GameSession, "generateQuestions", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = None

            # ACT
            q1 = await session.nextQuestion()

        # When
        result = await session.nextQuestion()

        # Then
        assert result is None
        assert session.state == SessionState.SUMMARY


    @pytest.mark.asyncio
    async def test_next_question_reaches_max_limit(self, session_empty_init):
        # ARRANGE
        questions = [
            Question(id=i, text=f"Q{i}", category=Category.RANDOM, language=Language.PL, answer=None)
            for i in range(MAX_QUESTIONS)
        ]
        session = session_empty_init
        session.currentQuestion = MAX_QUESTIONS
        session.questions = questions

        # ACT
        result = await session.nextQuestion()

        # ASSERT
        assert result is None
        assert session.state == SessionState.SUMMARY


    @pytest.mark.asyncio
    async def test_next_question_after_generation_continues_normally(self, session_empty_init):
        # ARRANGE
        questions = [
            Question(id=1, text="Q1", category=Category.RANDOM, language=Language.PL, answer=None)
        ]
        session = session_empty_init
        session.questions = questions

        generated = [
            Question(id=2, text="Q2", category=Category.RANDOM, language=Language.PL, answer=None),
            Question(id=3, text="Q3", category=Category.RANDOM, language=Language.PL, answer=None)
        ]

        # MOCK generator
        with patch.object(GameSession, "generateQuestions", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = generated

            # ACT
            q1 = await session.nextQuestion()
            assert q1.text == "Q1"
            q2 = await session.nextQuestion()
            assert q2.text == "Q2"

        assert len(session.questions) >= 2

