import asyncio
from schemas.game_session import GameSession, MAX_QUESTIONS
from schemas.enums import SessionState, Language
from schemas.player import Player, PlayerAnswer
from schemas.question import Question
from mappers.question_mapper import map_generated_question_to_global
from services.answer_verification.src.models import VerificationRequest
from services.trivia_generator.src.models import TriviaRequest
from services.question_generator.src.categories import CATEGORIES_CONFIG
from fastapi import HTTPException

class SessionManager:

    def __init__(self, question_generator, verify_service, trivia_service):
        self.question_generator = question_generator 
        self.verify_service = verify_service         
        self.trivia_service = trivia_service     
        
        self.sessions: dict[int, GameSession] = {}

    def create_session(self, player: Player, language: Language, category_id: str) -> GameSession:
        if category_id not in CATEGORIES_CONFIG:
            raise ValueError(f"Category ID {category_id} not found")
        
        session = GameSession(
            id=len(self.sessions) + 1,
            player=player,
            language=language,
            category=category_id,
            questions=[],
            answers=[],
            currentQuestion=-1,
            state=SessionState.INIT,
        )
        self.sessions[session.id] = session
        return session

    async def _generate_full_question_pipeline(self, session: GameSession):
        try:
            
            generated_q = await asyncio.to_thread(
                self.question_generator.generate_question,
                category=session.category,
                language=session.language
            )
            
            if not generated_q: return None
            
            question = map_generated_question_to_global(generated_q)

            async def get_trivia():
                if not self.trivia_service: return None
                req = TriviaRequest(question_text=question.text, language=session.language)
                return await asyncio.to_thread(self.trivia_service.generate_trivia, req)

            async def get_source():
                if not self.verify_service: return None
                if question.sourceUrl: return None 
                
                req = VerificationRequest(
                    question_text=question.text, 
                    numeric_answer=question.answer, 
                    language=session.language
                )
                return await asyncio.to_thread(self.verify_service.verify, req)

            # uruchamiamy oba zadania równocześnie
            trivia_res, source_res = await asyncio.gather(
                get_trivia(), 
                get_source(), 
                return_exceptions=True
            )
            
            # ciekawostki
            if trivia_res and not isinstance(trivia_res, Exception):
                question.trivia = trivia_res.trivia

                if trivia_res.source and trivia_res.source.url and not question.sourceUrl:
                    question.sourceUrl = trivia_res.source.url

            # źródła
            if source_res and not isinstance(source_res, Exception):
                if source_res.source and source_res.source.url and not question.sourceUrl:
                    question.sourceUrl = source_res.source.url

            return question

        except Exception as e:
            print(f"❌ Błąd w pipeline: {e}")
            return None

    async def start_session(self, session_id: int) -> GameSession:
        session = self.sessions[session_id]
        session.state = SessionState.LOADING
        
        TOTAL_CONCURRENT = 7
        tasks = [
            asyncio.create_task(self._generate_full_question_pipeline(session))
            for _ in range(TOTAL_CONCURRENT)
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        
        first_q = done.pop().result()

        if not first_q:
             raise HTTPException(status_code=503, detail="Nie udało się wygenerować pytania startowego.")

        first_q.id = 1
        session.questions.append(first_q)

        asyncio.create_task(self._collect_remaining_tasks(session, pending))

        session.state = SessionState.IN_PROGRESS
        session.currentQuestion += 1
        
        return session

    async def _collect_remaining_tasks(self, session, pending_tasks):
        """Zbiera resztę pytań, które przegrały wyścig o pierwsze miejsce."""
        for completed in asyncio.as_completed(pending_tasks):
            try:
                q = await completed
                if q:
                    if len(session.questions) >= MAX_QUESTIONS:
                        break 
                    
                    q.id = len(session.questions) + 1
                    session.questions.append(q)
                    print(f"📦 [QUEUE] Dodano kompletne pytanie do bufora ID: {q.id}")
            except Exception as e:
                print(f"⚠️ Błąd w zadaniu tła: {e}")

    async def get_next_question(self, session_id: int):
        session = self.sessions[session_id]
        session.currentQuestion += 1
        indx = session.currentQuestion

        if indx < len(session.questions):
            return session.questions[indx]
        
        # fallback
        print("⚠️ Pusty bufor! Generuję pytanie na żywo (może potrwać)...")
        q = await self._generate_full_question_pipeline(session)
        if q:
            q.id = len(session.questions) + 1
            session.questions.append(q)
            return q
            
        return None

    async def submit_answer(self, session_id: int, answer: PlayerAnswer):
        session = self.sessions.get(session_id)
        if not session: raise KeyError("Session not found")

        question = next((q for q in session.questions if q.id == answer.questionId), None)
        if not question: raise KeyError("Question not found")

        verify_request = VerificationRequest(
            question_text=question.text,
            numeric_answer=answer.value,
            language=session.language.value
        )
        verify_result = await asyncio.to_thread(self.verify_service.verify, verify_request)
        
        if verify_result.source and verify_result.source.url:
             question.sourceUrl = verify_result.source.url

        if hasattr(verify_result, 'trivia'):
             verify_result.trivia = question.trivia
        else:
             setattr(verify_result, 'trivia', question.trivia)
             
        if hasattr(verify_result, 'source') and verify_result.source:
             verify_result.source.url = question.sourceUrl

        session.answers.append(answer)
        if session.currentQuestion >= len(session.questions) and len(session.questions) >= MAX_QUESTIONS:
            session.state = SessionState.SUMMARY

        return verify_result

    def end_session(self, session_id: int) -> GameSession:
        session = self.sessions.get(session_id)
        if session:
            session.state = SessionState.ENDED
        return session
    
