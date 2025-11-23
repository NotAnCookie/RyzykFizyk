from enum import Enum

class Language(str, Enum):
    EN = "en"
    PL = "pl"

class SessionState(Enum):
    INIT = 0
    IN_PROGRESS = 1
    SUMMARY = 2
    ENDED = 3
    LOADING = 4

class Category(str,Enum):
    RANDOM = "random"
    HISTORY = "history"
    GEOGRAPHY = "geography"