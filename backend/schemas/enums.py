from enum import Enum
from services.question_generator.src.categories import CATEGORIES_KEYWORDS

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

# class CategoryEnum(str, Enum):
#     RANDOM = "random"
#     # dynamicznie wszystkie kategorie z CATEGORY_KEYWORDS
#     for key in CATEGORIES_KEYWORDS.keys():
#         locals()[key.upper()] = key

# przygotowanie dynamicznych wartości enuma
_dynamic_categories = {key.upper(): key for key in CATEGORIES_KEYWORDS.keys()}

# dodajemy RANDOM jako stałą
_dynamic_categories["RANDOM"] = "random"

# tworzymy enuma dynamicznie
CategoryEnum = Enum("CategoryEnum", _dynamic_categories, type=str)