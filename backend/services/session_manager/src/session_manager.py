from schemas.game_session import GameSession, MAX_QUESTIONS
from schemas.enums import SessionState, Language, CategoryEnum
from schemas.player import Player, PlayerAnswer
from schemas.question import Question
from mappers.question_mapper import *
from services.answer_verification.src.models import VerificationRequest, VerificationResult
from services.trivia_generator.src.models import TriviaRequest
import asyncio

class SessionManager:

    def __init__(self, question_generator, verify_service, trivia_service):
        self.question_generator = question_generator
        self.verify_service = verify_service
        self.trivia_service = trivia_service

        # aktywne sesje
        self.sessions: dict[int, GameSession] = {}

    def create_session(self, player: Player, language: Language, category_id: str) -> GameSession:

        if category_id not in AVAILABLE_CATEGORIES:
            raise ValueError(f"Category ID  {category_id} not found")
        
        category_obj = AVAILABLE_CATEGORIES[category_id]

        session = GameSession(
            id=len(self.sessions) + 1,
            player=player,
            language=language,
            category=category_obj,
            questions=[],
            answers=[],
            currentQuestion=-1,
            state=SessionState.INIT,
        )
        self.sessions[session.id] = session
        return session
    
    async def start_session(self, session_id: int) -> GameSession:
        session = self.sessions[session_id]

        session.state = SessionState.LOADING

        # generujemy pierwsze pytanie
        generated_q = self.question_generator.generate_question(
            category=session.category,
            language=session.language
        )

        session.questions = [map_generated_question_to_global(generated_q)]

        session.state = SessionState.IN_PROGRESS
        session.currentQuestion+=1
        return session

    
    async def get_next_question(self, session_id: int):
        session = self.sessions[session_id]
        session.currentQuestion += 1
        indx = session.currentQuestion

        # Jeśli są pytania do wykorzystania
        if indx < len(session.questions):
            q = session.questions[indx]
            return q

        # Generujemy kolejne pytanie tylko wtedy, gdy brakuje do MAX_QUESTIONS
        if indx < MAX_QUESTIONS:
            new_generated_q = self.question_generator.generate_question(
                language=session.language,
                category=session.category
            )

            if new_generated_q:
                # mapujemy na globalny model Question
                new_question = map_generated_question_to_global(new_generated_q)
                new_question.id = len(session.questions) + 1

                session.questions.append(new_question)
                return new_question

        # Jeżeli osiągnięto limit pytań
        session.state = SessionState.SUMMARY
        return None

    async def generate_background_question(self, session_id: int):
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        # Generujemy pytanie używając obiektu kategorii z sesji
        new_generated_q = self.question_generator.generate_question(
            category=session.category, 
            language=session.language
        )

        if new_generated_q:
            # Mapujemy na globalny model
            new_question = map_generated_question_to_global(new_generated_q)
            # Ustawiamy ID na "długość listy + 1", czyli na koniec kolejki
            new_question.id = len(session.questions) + 1 

            session.questions.append(new_question)
            
            return new_question
        
        return None

    async def submit_answer(self, session_id: int, answer: PlayerAnswer):
        # pobranie sesji
        session = self.sessions.get(session_id)   
        if session is None:
            raise KeyError(f"Session {session_id} not found")

        # znajdź pytanie po id (bez ryzyka StopIteration)
        question = next((q for q in session.questions if q.id == answer.questionId), None)
        if question is None:
            raise KeyError(f"Question {answer.questionId} not found in session {session_id}")

        # stwórz request do verify_service
        verify_request = VerificationRequest(
            question_text=question.text,
            numeric_answer=answer.value,
            language=session.language.value
        )

        # asynchroniczne wywołanie weryfikacji w osobnym wątku
        verify_result = await asyncio.to_thread(
            self.verify_service.verify,
            verify_request
        )

        # przypisz źródło jeśli dostępne
        if verify_result.source:
            question.sourceUrl = verify_result.source.url

        # ciekawostka (trivia) - też w osobnym wątku
        if self.trivia_service:
            trivia_request = TriviaRequest(
                question_text=question.text,
                language=session.language
            )
            trivia_result = await asyncio.to_thread(
                self.trivia_service.generate_trivia,
                trivia_request
            )
            question.trivia = trivia_result.trivia if trivia_result else None

        # zapisz odpowiedź
        session.answers.append(answer)

        # # aktualizuj stan sesji jeśli osiągnięto koniec pytań
        if session.currentQuestion >= len(session.questions):
            session.state = SessionState.SUMMARY

        # zwróć wynik weryfikacji
        return verify_result

    

    def end_session(self, session_id: int) -> GameSession:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")
        
        session.state = SessionState.ENDED
        return session
    

    


