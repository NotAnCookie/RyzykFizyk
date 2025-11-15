class APIClient:
    """Mock lub placeholder dla przyszłego klienta API (np. OpenAI, HuggingFace)."""

    def get_completion(self, prompt: str) -> str:
        """Zwraca przykładową odpowiedź — do testów offline."""
        return f"Ciekawostka testowa o temacie: {prompt[:20]}... (Wikipedia)."
