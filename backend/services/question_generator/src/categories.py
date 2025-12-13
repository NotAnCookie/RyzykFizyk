import random
from enum import Enum
from pydantic import BaseModel

class WikiCategory(BaseModel):
    name: str
    keywords: list[str]

CATEGORIES_KEYWORDS = {
    "geography": {
        "name": "Geography",
        "keywords": ["river", "lake", "mountain", "island"],
    },
    "history": {
        "name": "History",
        "keywords": ["battle", "king", "dynasty"],
    },
    "biology": {
        "name": "Biology",
        "keywords": ["mammal", "bird", "forest"],
    },
    "technology_space": {
        "name": "Technology_Space",
        "keywords": ["rocket", "engine", "planet"],
    },
}

AVAILABLE_CATEGORIES = {
    key: WikiCategory(**value)
    for key, value in CATEGORIES_KEYWORDS.items()
}
