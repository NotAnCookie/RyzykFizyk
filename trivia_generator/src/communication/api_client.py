class APIClient:
    """Mock dla przyszłego klienta API """

    def get_completion(self, prompt: str) -> str:
        """Zwraca przykładową odpowiedź — do testów offline."""
        return f"Ciekawostka testowa o temacie: {prompt[:20]}... (Wikipedia)."
