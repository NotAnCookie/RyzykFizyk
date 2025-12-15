import os
import requests
from dotenv import load_dotenv

load_dotenv()


class GoogleSearchClient:
    def __init__(self, language: str = "pl"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx = os.getenv("GOOGLE_CX")
        self.language = language

        if not self.api_key or not self.cx:
            raise RuntimeError("Brak GOOGLE_API_KEY lub GOOGLE_CX w .env")

        self.url = "https://www.googleapis.com/customsearch/v1"

    def search_wikipedia_link(self, question: str) -> dict | None:
        """
        Zwraca {title, url} lub None
        """
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": f"site:wikipedia.org {question}",
            "num": 1,
            "hl": self.language
        }

        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return None

        data = response.json()
        items = data.get("items", [])

        if not items:
            return None

        item = items[0]
        return {
            "title": item.get("title"),
            "url": item.get("link")
        }