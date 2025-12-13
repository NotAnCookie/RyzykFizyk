from pydantic import BaseModel
from schemas.enums import *

class Player(BaseModel):
    id: int
    email: str
    name: str

class PlayerAnswer(BaseModel):
    questionId: int
    playerId: int
    value: float