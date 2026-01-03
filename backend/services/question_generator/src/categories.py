import random
from enum import Enum
from pydantic import BaseModel

class WikiCategory(BaseModel):
    name: str
    keywords: list[str]

CATEGORIES_CONFIG = {
    "geography": {
        "id": "geography",
        "en": {
            "name": "Geography",
            "keywords": ["river", "lake", "mountain peak", "mountain", "island", "desert", "city", "capital", "ocean", "volcano", "strait"]
        },
        "pl": {
            "name": "Geografia",
            "keywords": ["rzeka", "jezioro", "szczyt górski", "góra", "wyspa", "pustynia", "miasto", "stolica", "ocean", "wulkan", "cieśnina", "Polska", "Europa", "Morze Bałtyckie", "Tatry"]
        }
    },
    "history": {
        "id": "history",
        "en": {
            "name": "History",
            "keywords": ["battle", "war", "king", "treaty", "uprising", "dynasty", "revolution", "castle", "emperor"]
        },
        "pl": {
            "name": "Historia",
            "keywords": ["bitwa", "wojna", "król", "traktat", "powstanie", "dynastia", "rewolucja", "zamek", "cesarz", "historia Polski", "II wojna światowa", "średniowiecze"]
        }
    },
    "biology": {
        "id": "biology",
        "en": {
            "name": "Biology",
            "keywords": ["mammal", "bird", "reptile", "anatomy", "tree", "forest", "bacteria", "organism", "species"]
        },
        "pl": {
            "name": "Biologia",
            "keywords": ["ssak", "ptak", "gad", "anatomia", "drzewo", "las", "bakteria", "organizm", "gatunek", "zwierzęta", "rośliny", "ekologia"]
        }
    },
    "technology_space": {
        "id": "technology_space",
        "en": {
            "name": "Technology & Space",
            "keywords": ["planet", "rocket", "airplane", "engine", "element", "star", "computer", "invention", "energy"]
        },
        "pl": {
            "name": "Technologia i Kosmos",
            "keywords": ["planeta", "rakieta", "samolot", "silnik", "pierwiastek", "gwiazda", "komputer", "wynalazek", "energia", "fizyka", "astronomia"]
        }
    }
}


CATEGORIES_KEYWORDS = {}

for cat_id, data in CATEGORIES_CONFIG.items():
    en_data = data.get("en")
    if en_data:
        CATEGORIES_KEYWORDS[cat_id] = {
            "name": en_data["name"],
            "keywords": en_data["keywords"]
        }

AVAILABLE_CATEGORIES = {
    key: WikiCategory(**value)
    for key, value in CATEGORIES_KEYWORDS.items()
}
