SYSTEM_PROMPT_TEMPLATE = {
    "pl": (
        "Jesteś precyzyjnym generatorem pytań do quizu wiedzy. "
        "Twoim celem jest wygenerowanie JEDNEGO ciekawego pytania wyłącznie na podstawie dostarczonego tekstu nie halucynuj. "
        "Zawsze zwracasz wynik w formacie JSON."
    ),
    "en": (
        "You are a precise Trivia Quiz Generator. "
        "Your goal is to generate ONE interesting question based ONLY on the provided text don't hallucinate. "
        "You always return the output in JSON format."
    )
}

QUESTION_PROMPT_TEMPLATE = {
    "pl": (
        "Tytuł artykułu: {topic}\n"
        "Tekst: '{context_text}'\n\n"
        "Twoim zadaniem jest ułożenie pytania numerycznego do teleturnieju.\n"
        "ZASADY KRYTYCZNE:\n"
        "1. SELEKCJA WARTOŚCI:\n"
        "   - Szukaj twardych danych: wielkości fizyczne (metry, kg, km/h), statystyki, procenty.\n"
        "   - Unikaj dat (chyba że nie ma nic innego). Unikaj numerów porządkowych (np. 1. miejsce) chyba że pytanie dotyczy rankingu.\n"
        "2. FILTR GRAMATYCZNY (Absolutny priorytet!):\n"
        "   - Pytanie MUSI zaczynać się od fraz pytających o ilość: 'Ile...', 'Jaka jest...', 'Jaka wartość...', 'W którym roku...', 'Które miejsce...'.\n"
        "   - ZABRANIA SIĘ pytań o tożsamość typu: 'Który...', 'Kto...', 'Gdzie...', 'W jakim mieście...'.\n"
        "   - Przykład BŁĘDU: 'Który port jest największy?' (gdy odp to 1).\n"
        "   - POPRAWKA: 'Które miejsce w rankingu zajmuje ten port?'.\n"
        "   - Przykład BŁĘDU: 'W jakiej części płynie rzeka w km?'\n"
        "   - POPRAWKA: 'Ile kilometrów od Piły płynie ta rzeka?'.\n"
        "3. SPÓJNOŚĆ:\n"
        "   - Pytanie musi logicznie pasować do jednostki odpowiedzi.\n"
        "   - Jeśli odpowiedź to '1995', pytanie musi dotyczyć czasu.\n"
        "   - Jeśli odpowiedź to '50', pytanie musi dotyczyć ilości/wielkości.\n"
        "4. FILTR ANTY-META:\n"
        "   - Nie pytaj o strukturę tekstu (np. 'Ile rozdziałów ma tekst?').\n"
        "\n"
        "Zwróć TYLKO JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"Ile metrów wysokości ma wieża ratusza?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    ),
    "en": (
        "Article Title: {topic}\n"
        "Text: '{context_text}'\n\n"
        "Your task is to write a numeric trivia question.\n"
        "CRITICAL RULES:\n"
        "1. VALUE SELECTION:\n"
        "   - Prioritize physical quantities (meters, kg, km/h), stats, percentages.\n"
        "2. GRAMMAR FILTER (Highest Priority!):\n"
        "   - The question MUST ask for a quantity/value: 'How many...', 'What is the height...', 'In what year...', 'What rank...'.\n"
        "   - FORBIDDEN starts: 'Which...', 'Who...', 'Where...' (unless explicitly asking for coordinates/rank).\n"
        "   - BAD Example: 'Which port is the biggest?' (if answer is 1).\n"
        "   - FIX: 'What is the rank of this port?'.\n"
        "3. CONSISTENCY:\n"
        "   - The question phrasing must explicitly match the numeric answer unit.\n"
        "4. ANTI-META:\n"
        "   - Do not ask about text structure.\n"
        "\n"
        "Return ONLY JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"What is the maximum speed in km/h?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    )
}