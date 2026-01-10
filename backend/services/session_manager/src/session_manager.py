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

    def __init__(self, question_generator, verify_service, trivia_service, combined_generator=None):
        self.question_generator = question_generator
        self.verify_service = verify_service
        self.trivia_service = trivia_service
        self.combined_generator = combined_generator

        # aktywne sesje
        self.sessions: dict[int, GameSession] = {}

        # track background prefill tasks per session to avoid duplicates
        self._prefill_tasks: dict[int, asyncio.Task] = {}

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
    
    async def _collect_remaining_tasks(self, session: GameSession, pending_tasks):
        """
        Ta funkcja czeka na pozostałe zadania, które nie zdążyły być 'pierwsze'.
        Gdy tylko skończą, dodaje je do listy.
        """
        print(f"🏃 [RACE] Czekam na {len(pending_tasks)} pozostałych pytań w tle...")
        
        try:
            # as_completed pozwala przetwarzać zadania w miarę ich kończenia (nie po kolei!)
            for completed_task in asyncio.as_completed(pending_tasks):
                try:
                    question = await completed_task
                    if question:
                        # Nadajemy ID dynamicznie
                        question.id = len(session.questions) + 1
                        session.questions.append(question)
                        print(f"✅ [RACE] Dodano kolejne pytanie (ID: {question.id})")
                except Exception as e:
                    print(f"⚠️ [RACE] Błąd w zadaniu tła: {e}")
                    
        except Exception as e:
            print(f"❌ [RACE] Błąd pętli zbierającej: {e}")

    async def start_session(self, session_id: int) -> GameSession:
        session = self.sessions[session_id]
        session.state = SessionState.LOADING
        
        TOTAL_QUESTIONS = 7
        
        print(f"🏁 [START] Wystrzeliwuję {TOTAL_QUESTIONS} zapytań do AI JEDNOCZEŚNIE...")

        # A. Tworzymy listę zadań (Future objects), ale ich nie czekamy (await)
        tasks = [
            asyncio.create_task(self._generate_single_complete_question(session, TOTAL_QUESTIONS))
            for _ in range(TOTAL_QUESTIONS)
        ]

        # B. Czekamy na PIERWSZEGO gotowego (FIRST_COMPLETED)
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        first_task = done.pop() # Pobieramy zakończone zadanie
        first_q = first_task.result() # Pobieramy wynik


        if not first_q:
            print("⚠️ [RACE] Najszybsze pytanie było puste! Czekam na kolejne...")

            raise HTTPException(status_code=503, detail="Błąd generatora AI (Empty Race).")

        first_q.id = 1
        session.questions.append(first_q)
        print(f"🥇 [WINNER] Mamy pierwsze pytanie! Zwracam je do gracza.")

        if pending:
            asyncio.create_task(self._collect_remaining_tasks(session, pending))

            # If we don't yet have the full set of questions, start prefill for the remaining
            remaining = max(0, TOTAL_QUESTIONS - len(session.questions))
            if remaining > 0 and session.id not in self._prefill_tasks:
                self._start_prefill_task(session.id, remaining)

        session.state = SessionState.IN_PROGRESS
        session.currentQuestion += 1
        
        return session

    def _start_prefill_task(self, session_id: int, count: int):
        """Start a background prefill for the session if not already running."""
        if session_id in self._prefill_tasks:
            return

        task = asyncio.create_task(self._prefill_questions_background(session_id, count))
        self._prefill_tasks[session_id] = task

        def _on_done(t):
            self._prefill_tasks.pop(session_id, None)
        task.add_done_callback(_on_done)
    
    # async def start_session(self, session_id: int) -> GameSession:
    #     session = self.sessions[session_id]
    #     session.state = SessionState.LOADING

    #     # KROK 1: Generujemy Q1 (Blokujemy użytkownika na te 3-5s, bo musi mieć co robić)
    #     # Używamy _generate_single_complete_question, żeby Q1 też miało od razu trivię!
    #     first_q = await self._generate_single_complete_question(session, 0)
        
    #     if not first_q:
    #          raise HTTPException(status_code=503, detail="Failed to start game.")

    #     first_q.id = 1
    #     session.questions.append(first_q)

    #     # KROK 2: Resztę (5 pytań) puszczamy w tle
    #     # UWAGA: create_task powoduje, że Python NIE CZEKA tutaj na wynik.
    #     # Python idzie do następnej linijki (return) natychmiast.
    #     asyncio.create_task(self._prefill_questions_background(session_id, 6))

    #     session.state = SessionState.IN_PROGRESS
    #     session.currentQuestion += 1
        
    #     # KROK 3: Zwracamy sesję. Gracz gra.
    #     # W międzyczasie w tle mieli się 5 wątków. Zanim gracz odpowie na Q1, 
    #     # Q2-Q6 będą już gotowe w liście session.questions.
    #     return session
    

    
    # # async def start_session2(self, session_id: int) -> GameSession:
    # #     session = self.sessions[session_id]

    # #     session.state = SessionState.LOADING

    # #     # generujemy pierwsze pytanie
    # #     generated_q = self.question_generator.generate_question(
    # #         category=session.category,
    # #         language=session.language
    # #     )

        
    # #     first_question = map_generated_question_to_global(generated_q)
    # #     first_question.id = len(session.questions) + 1

    # #     session.questions.append(first_question)

    # #     session.state = SessionState.IN_PROGRESS
    # #     session.currentQuestion+=1
    # #     return session

    
    async def get_next_question(self, session_id: int):
        session = self.sessions[session_id]
        session.currentQuestion += 1
        indx = session.currentQuestion

        # Jeśli są pytania do wykorzystania
        if indx < len(session.questions):
            q = session.questions[indx]

            # Ensure background prefill is running for the remaining questions
            if len(session.questions) < MAX_QUESTIONS and session.id not in self._prefill_tasks:
                self._start_prefill_task(session.id, MAX_QUESTIONS - len(session.questions))

            return q

        # Jeśli brakuje pytań a nie osiągnięto MAX_QUESTIONS -> uruchom prefill tła i poczekaj krótko
        if indx < MAX_QUESTIONS:
            # Start background prefill for remaining questions if not already running
            if session.id not in self._prefill_tasks:
                self._start_prefill_task(session.id, MAX_QUESTIONS - len(session.questions))

            # Wait briefly for background prefill to add at least one question
            timeout = 3.0
            poll = 0.1
            waited = 0.0
            while indx >= len(session.questions) and waited < timeout:
                await asyncio.sleep(poll)
                waited += poll

            # If background prefill added the question while we were waiting, return it
            if indx < len(session.questions):
                return session.questions[indx]

            # Fallback: try synchronous generation with retries so the caller is not blocked
            max_attempts = 5
            attempt = 0
            backoff = 0.2
            generated = None

            while attempt < max_attempts:
                attempt += 1
                new_generated_q = await self._generate_single_complete_question(session, 1)

                # If prefill filled the slot while we were generating, prefer that
                if indx < len(session.questions):
                    return session.questions[indx]

                if new_generated_q:
                    # If there's still room, append and return
                    if len(session.questions) < MAX_QUESTIONS:
                        new_generated_q.id = len(session.questions) + 1
                        session.questions.append(new_generated_q)
                        return new_generated_q

                    # If we cannot append because the session is already full, try to return existing question
                    if indx < len(session.questions):
                        return session.questions[indx]

                    # Unexpected race: break and mark as exhausted
                    break

                # nothing generated this attempt — wait briefly and retry
                await asyncio.sleep(backoff)

            # After retries, check again if prefill produced the question
            if indx < len(session.questions):
                return session.questions[indx]

            # After attempts exhausted, mark summary and return None
            session.currentQuestion = MAX_QUESTIONS
            session.state = SessionState.SUMMARY
            return None

        # Jeżeli osiągnięto limit pytań
        session.currentQuestion = MAX_QUESTIONS
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
            # If a combined generator is available, use it to make a single OpenAI call
            if self.combined_generator:
                print("🔗 [COMBINED] Using combined generator to create question + trivia in one call.")
                combined_res = await asyncio.to_thread(self.combined_generator.generate, session.category, session.language)
                if not combined_res:
                    print("⚠️ [COMBINED] Combined generator returned None.")
                    return None

                gen_q, trivia_res = combined_res

                question = map_generated_question_to_global(gen_q)

                # attach trivia and source if present
                if trivia_res:
                    question.trivia = trivia_res.trivia
                    if trivia_res.source and getattr(trivia_res.source, 'url', None):
                        question.sourceUrl = trivia_res.source.url

                return question

            # A. Generowanie treści (Tekst + Odpowiedź) using the old separate question generator
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
        
        # Run them concurrently and wait for results
        results = await asyncio.gather(*tasks)

        # Filter out failures
        valid_questions = [q for q in results if q is not None]

        for q in valid_questions:
            # Stop if we've already reached the MAX_QUESTIONS (race-safety)
            if len(session.questions) >= MAX_QUESTIONS:
                print(f"⚠️ [PREFILL] Osiągnięto limit pytań, pomijam nadmiar")
                break

            q.id = len(session.questions) + 1
            session.questions.append(q)
            print(f"✅ [PREFILL] Dodano gotowe pytanie ID: {q.id}")

        print(f"🏁 [PREFILL] Zakończono! Razem w sesji: {len(session.questions)}")


