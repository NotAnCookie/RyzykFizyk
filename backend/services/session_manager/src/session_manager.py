from schemas.game_session import GameSession, MAX_QUESTIONS
from schemas.enums import SessionState, Language, CategoryEnum
from schemas.player import Player, PlayerAnswer
from schemas.question import Question
from mappers.question_mapper import *
from services.answer_verification.src.models import VerificationRequest, VerificationResult
from services.trivia_generator.src.models import TriviaRequest
from services.question_generator.src.categories import CATEGORIES_CONFIG
from fastapi import HTTPException
import asyncio

class SessionManager:

    def __init__(self, question_generator, verify_service, trivia_service):
        self.question_generator = question_generator
        self.verify_service = verify_service
        self.trivia_service = trivia_service

        # aktywne sesje
        self.sessions: dict[int, GameSession] = {}

    def create_session(self, player: Player, language: Language, category_id: str) -> GameSession:

        if category_id not in CATEGORIES_CONFIG:
            raise ValueError(f"Category ID  {category_id} not found")
        
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
    
    async def start_session(self, session_id: int) -> GameSession:
        session = self.sessions[session_id]
        session.state = SessionState.LOADING

        # KROK 1: Generujemy Q1 (Blokujemy użytkownika na te 3-5s, bo musi mieć co robić)
        # Używamy _generate_single_complete_question, żeby Q1 też miało od razu trivię!
        first_q = await self._generate_single_complete_question(session, 0)
        
        if not first_q:
             raise HTTPException(status_code=503, detail="Failed to start game.")

        first_q.id = 1
        session.questions.append(first_q)

        # KROK 2: Resztę (5 pytań) puszczamy w tle
        # UWAGA: create_task powoduje, że Python NIE CZEKA tutaj na wynik.
        # Python idzie do następnej linijki (return) natychmiast.
        asyncio.create_task(self._prefill_questions_background(session_id, 6))

        session.state = SessionState.IN_PROGRESS
        session.currentQuestion += 1
        
        # KROK 3: Zwracamy sesję. Gracz gra.
        # W międzyczasie w tle mieli się 5 wątków. Zanim gracz odpowie na Q1, 
        # Q2-Q6 będą już gotowe w liście session.questions.
        return session
    

    
    # async def start_session2(self, session_id: int) -> GameSession:
    #     session = self.sessions[session_id]

    #     session.state = SessionState.LOADING

    #     # generujemy pierwsze pytanie
    #     generated_q = self.question_generator.generate_question(
    #         category=session.category,
    #         language=session.language
    #     )

        
    #     first_question = map_generated_question_to_global(generated_q)
    #     first_question.id = len(session.questions) + 1

    #     session.questions.append(first_question)

    #     session.state = SessionState.IN_PROGRESS
    #     session.currentQuestion+=1
    #     return session

    
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
    
    async def verify_only(self, session_id: int, user_value: float, question_id: int):
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError("Session not found")

        # 1. Znajdź pytanie
        question = next((q for q in session.questions if q.id == question_id), None)
        if not question:
            raise KeyError("Question not found")
        verify_request = VerificationRequest(
            question_text=question.text,
            numeric_answer=user_value,
            language=session.language
        )

        result = await asyncio.to_thread(self.verify_service.verify, verify_request)

        if result.source:
            question.sourceUrl = result.source.url # Link do źródła
        
        # Zwracamy wynik, żeby router mógł go odesłać
        return result

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
    

    async def _generate_single_complete_question(self, session: GameSession, index_offset: int):
        try:
            # A. Generowanie treści (Tekst + Odpowiedź)
            generated_q = await asyncio.to_thread(
                self.question_generator.generate_question,
                category=session.category,
                language=session.language
            )

            if not generated_q:
                print("⚠️ [Batch] Generator zwrócił None.")
                return None

            question = map_generated_question_to_global(generated_q)
            
            # B. Wzbogacanie (Trivia + Source) - RÓWNOLEGLE!            
            async def get_trivia():
                if self.trivia_service:
                    req = TriviaRequest(question_text=question.text, language=session.language)
                    return await asyncio.to_thread(self.trivia_service.generate_trivia, req)
                return None

            async def get_source():
                req = VerificationRequest(
                    question_text=question.text, 
                    numeric_answer=question.answer, 
                    language=session.language
                )
                return await asyncio.to_thread(self.verify_service.verify, req)

            trivia_res, source_res = await asyncio.gather(get_trivia(), get_source(), return_exceptions=True)

            # Przypisanie wyników (z obsługą błędów wewnątrz gather)
            if isinstance(trivia_res, Exception):
                print(f"⚠️ Błąd Trivii: {trivia_res}")
                question.trivia = None
            elif trivia_res:
                question.trivia = trivia_res.trivia

            if isinstance(source_res, Exception):
                print(f"⚠️ Błąd Źródła: {source_res}")
                question.sourceUrl = None
            elif source_res and source_res.source:
                question.sourceUrl = source_res.source.url

            return question

        except Exception as e:
            print(f"❌ [Batch] Błąd generowania pojedynczego pytania: {e}")
            return None

    async def _prefill_questions_background(self, session_id: int, count: int):
        session = self.sessions.get(session_id)
        if not session: return

        print(f"🚀 [PREFILL] Startuję generowanie {count} pytań równolegle dla sesji {session_id}...")

        tasks = [self._generate_single_complete_question(session, i) for i in range(count)]
        
        # Uruchamiamy WSZYSTKIE naraz i czekamy aż wszystkie spłyną
        results = await asyncio.gather(*tasks)

        # Filtrujemy None (nieudane próby)
        valid_questions = [q for q in results if q is not None]

        current_len = len(session.questions)
        for i, q in enumerate(valid_questions):
            q.id = current_len + i + 1
            session.questions.append(q)
            print(f"✅ [PREFILL] Dodano gotowe pytanie ID: {q.id}")

        print(f"🏁 [PREFILL] Zakończono! Dodano {len(valid_questions)} pytań. Razem w sesji: {len(session.questions)}")


