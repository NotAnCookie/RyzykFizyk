TRIVIA_PROMPT_TEMPLATE = {
    "pl": (
        #"Podaj jedną krótką, ciekawą ciekawostkę związaną z pytaniem: '{topic}'. Nie odpowiadaj na pytanie. "
        # "Zachowaj styl informacyjny. Jeśli to możliwe, dodaj źródło w nawiasie (np. Wikipedia)."
        "Opowiedz zabawną lub nietypową ciekawostkę inspirowaną tematem tego pytania. Nie odpowiadaj na pytanie i nie używaj liczb oraz ogranicz się do jednego krótkiego zdania. {topic}"
    ),

    "en": (
        #"Provide one short and interesting trivia related to the question: '{topic}'. Don't answer the question."
        # "Keep an informative tone. If possible, include a source in parentheses (e.g., Wikipedia)."
        "Tell a funny or unusual fact inspired by the topic of this question. Do not answer the question, do not use numbers, and keep it to a single short sentence. {topic}"
    ),
}
