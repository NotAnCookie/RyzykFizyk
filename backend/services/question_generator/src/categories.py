import random
from enum import Enum
from pydantic import BaseModel

class WikiCategory(BaseModel):
    name: str
    keywords: list[str]

CATEGORIES_KEYWORDS = {
    "geography": {
        "name": "Geography",
         "keywords": ["river", "lake", "mountain peak", "mountain", "island", "desert", "city", "capital", "ocean", "volcano", "strait"]
    },
    "history": {
        "name": "History",
        "keywords": ["battle", "war", "king", "treaty", "uprising", "dynasty", "revolution", "castle", "emperor"],
    },
    "biology": {
        "name": "Biology",
        "keywords": ["mammal", "bird", "reptile", "anatomy", "tree", "forest", "bacteria", "organism", "species"],
    },
    "technology_space": {
        "name": "Technology_Space",
        "keywords": ["planet", "rocket", "airplane", "engine", "element", "star", "computer", "invention", "energy"],
    },
}

AVAILABLE_CATEGORIES = {
    key: WikiCategory(**value)
    for key, value in CATEGORIES_KEYWORDS.items()
}
