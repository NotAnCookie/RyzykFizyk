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
        "Twoim zadaniem jest ułożenie pytania do teleturnieju 'Milionerzy'.\n"
        "ZASADY KRYTYCZNE:\n"
        "1. SELEKCJA WARTOŚCI (Priorytety):\n"
        "   - NAJLEPSZE: Wielkości fizyczne (np. wysokość w metrach, masa w kg, prędkość km/h, temperatura), statystyki (populacja, procenty).\n"
        "   - OSTATECZNOŚĆ: Rok/Data. Pytaj o rok TYLKO wtedy, gdy w tekście nie ma absolutnie żadnych innych liczb. Daty są zazwyczaj nudne.\n"
        "2. FILTR ANTY-META (Najważniejsze!): \n"
        "   - ZABRANIA SIĘ pytać o strukturę tekstu (np. 'Ile przykładów wymieniono?', 'Ile typów podano?').\n"
        "   - Jeśli w tekście jest wyliczanka (np. 'wymieniono 3 kraje'), IGNORUJ TĘ LICZBĘ. Szukaj innej.\n"
        "3. JEDNOSTKA: Pytanie MUSI zawierać jednostkę (np. 'ile metrów', 'ile tysięcy', 'w jakim stopniu').\n"
        "4. ODPOWIEDŹ: Musi być czystą liczbą (int lub float).\n"
        "5. Jeśli nie możesz znaleźć sensownej liczby (a nie wyliczenia) -> ZWRÓĆ is_relevant: false.\n\n"
        "Zwróć TYLKO JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"Jaka jest maksymalna prędkość tego zwierzęcia w km/h?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    ),

    "en": (
        "Article Title: {topic}\n"
        "Text: '{context_text}'\n\n"
        "Your task is to write a 'Who Wants to Be a Millionaire' style trivia question.\n"
        "CRITICAL RULES:\n"
        "1. VALUE SELECTION (Priorities):\n"
        "   - BEST: Physical quantities (e.g., height in meters, weight in kg, speed in km/h, temperature), statistics (population, percentages).\n"
        "   - LAST RESORT: Year/Date. Ask about a year ONLY if there are absolutely no other numbers in the text. Dates are usually boring.\n"
        "2. ANTI-META FILTER (Most Important!):\n"
        "   - DO NOT ask about the text structure (e.g., 'How many examples are listed?').\n"
        "   - If the text lists items (e.g., '3 types of animals'), IGNORE THAT NUMBER. Find another one.\n"
        "3. UNIT: The question MUST specify the unit (e.g., 'how many meters', 'in degrees', 'what percentage').\n"
        "4. ANSWER: Must be a pure number (int or float), no text.\n"
        "5. If no factual number (other than counts of examples) is found -> RETURN is_relevant: false.\n\n"
        "Return ONLY JSON:\n"
        "{{\n"
        "  \"is_relevant\": true,\n"
        "  \"question_text\": \"What is the maximum speed of this animal in km/h?\",\n"
        "  \"answer_number\": 65\n"
        "}}"
    ),
}