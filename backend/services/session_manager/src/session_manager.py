from schemas.game_session import GameSession, MAX_QUESTIONS
from schemas.enums import SessionState, Language, Category
from schemas.player import Player, PlayerAnswer
from schemas.question import Question


class SessionManager:

    def __init__(self, question_generator, verify_service, trivia_service):
        self.question_generator = question_generator
        self.verify_service = verify_service
        self.trivia_service = trivia_service

        # aktywne sesje
        self.sessions: dict[int, GameSession] = {}

    def create_session(self, player: Player, language: Language, category: Category) -> GameSession:
        session = GameSession(
            id=len(self.sessions) + 1,
            player=player,
            language=language,
            category=category,
            questions=[],
            answers=[],
            currentQuestion=0,
            state=SessionState.INIT,
        )
        self.sessions[session.id] = session
        return session

    async def start_session(self, session_id: int) -> GameSession:
        session = self.sessions[session_id]

        # pytania (tylko teksty)
        session.state = SessionState.LOADING
        session.questions = await self.question_generator.generate(
            language=session.language,
            category=session.category,
            amount=MAX_QUESTIONS,
        )

        session.state = SessionState.IN_PROGRESS
        return session

    async def get_next_question(self, session_id: int):
        session = self.sessions[session_id]

        # Jeśli są pytania do wykorzystania
        if session.currentQuestion < len(session.questions):
            q = session.questions[session.currentQuestion]
            session.currentQuestion += 1
            return q

        # Jeśli brakuje pytań
        missing = MAX_QUESTIONS - len(session.questions)
        if missing > 0:
            new_questions = await self.question_generator.generate(
                language=session.language,
                category=session.category,
                amount=missing
            )
            session.questions.extend(new_questions)
            return await self.get_next_question(session_id)

        # 7 pytań -> END
        session.state = SessionState.SUMMARY
        return None


    async def submit_answer(self, session_id: int, answer: PlayerAnswer):
        session = self.sessions[session_id]

        question = next(q for q in session.questions if q.id == answer.questionId)

        # źródło
        verify_result = await self.verify_service.verify(question.text, answer.value)
        question.sourceUrl = verify_result.source.url

        # ciekawostka
        question.trivia = await self.trivia_service.generate(question.text)

        session.answers.append(answer)
        if session.currentQuestion >= len(session.questions):
            session.state = SessionState.SUMMARY

        return verify_result
    

    def end_session(self, session_id: int) -> GameSession:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")
        
        session.state = SessionState.ENDED
        return session
    

    


