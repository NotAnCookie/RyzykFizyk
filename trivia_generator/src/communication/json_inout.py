import json
from typing import Dict, Any

def read_input(json_str: str) -> Dict[str, Any]:
    """Wczytuje dane wejściowe w formacie JSON."""
    try:
        data = json.loads(json_str)
        if "question" not in data:
            raise ValueError("Brak klucza 'question' w danych wejściowych.")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Błędny format JSON: {e}")

def write_output(trivia: str, source: str = None) -> str:
    """Zwraca dane wyjściowe jako JSON (do przekazania dalej)."""
    result = {"trivia": trivia}
    if source:
        result["source"] = source
    return json.dumps(result, ensure_ascii=False, indent=2)
