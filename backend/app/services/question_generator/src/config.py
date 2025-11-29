from app.services.question_generator.src.models import Category

AVAILABLE_CATEGORIES = [
    Category(
        name="Geography",
        keywords=["river", "lake", "mountain peak", "mountain", "island", "desert", "city", "capital", "ocean", "volcano", "strait"]
    ),
    Category(
        name="History",
        keywords=["battle", "war", "king", "treaty", "uprising", "dynasty", "revolution", "castle", "emperor"]
    ),
    Category(
        name="Biology",
        keywords=["mammal", "bird", "reptile", "anatomy", "tree", "forest", "bacteria", "organism", "species"]
    ),
    Category(
        name="Technology/Space",
        keywords=["planet", "rocket", "airplane", "engine", "element", "star", "computer", "invention", "energy"]
    )
]