from pydantic import BaseModel
from schemas.enums import *
from typing import Optional
from schemas.player import *
from schemas.question import *

MAX_QUESTIONS = 7

class GameSession(BaseModel):
    id: int
    player: Optional[Player] = None
    questions: list[Question]
    answers: list[PlayerAnswer]
    currentQuestion: int
    language: Language
    category: Category
    state: SessionState

    def start(self):
        self.currentQuestion = 0
        self.state = SessionState.IN_PROGRESS
    
    def changeCategory(self, category: Category):
        self.category = category

    async def generateQuestions(self, amount: int = 1) -> list[Question]:
        # todo
        return None

    async def nextQuestion(self) -> Optional["Question"]:
        # Rozpoczęcie gry
        if self.state == SessionState.INIT:
            self.state = SessionState.IN_PROGRESS

        # Limit pytań
        if self.currentQuestion >= MAX_QUESTIONS:
            self.state = SessionState.SUMMARY
            return None

        # Brak pytań 
        if self.currentQuestion >= len(self.questions):
            # Czekanie na pytania
            missing = MAX_QUESTIONS - len(self.questions)
            if missing > 0:
                new_questions = await self.generateQuestions(
                    amount=missing
                )

                # Jeśli generator nic nie zwrócił
                if not new_questions:
                    self.state = SessionState.SUMMARY
                    return None
                
                self.questions.extend(new_questions)

        # Kolejne pytanie
        question = self.questions[self.currentQuestion]
        self.currentQuestion += 1

        return question

