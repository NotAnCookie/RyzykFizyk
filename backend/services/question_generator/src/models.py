from typing import List
from dataclasses import dataclass, field
from services.question_generator.src.enums import Language 
import uuid
from services.question_generator.src.categories import WikiCategory

# @dataclass
# class Category:
#     name: str
#     keywords: List[str]

#     def __str__(self):
#         return self.name

@dataclass
class Question:
    category: WikiCategory = None
    language: Language = Language.EN
    question_text: str = ""
    topic: str = ""     
    answer: str = ""    
    question_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self):
        return f"[{self.category.name}] {self.question_text}"