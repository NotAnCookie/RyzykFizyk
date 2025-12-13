import requests
import yake
from pathlib import Path
from app.services.answer_verification.src.enums import Language


class WikipediaClient:
    def __init__(self, language=Language.PL):
        self.language = language

        self.headers = {
            "User-Agent": "TriviaVerifier/1.0 (agabibek1@gmail.com)"
        }
        self.kw_extractor = yake.KeywordExtractor(lan=language.value, n=1, top=1)


    def extract_keyword(self, question: str) -> str:
        keywords = self.kw_extractor.extract_keywords(question)
        if not keywords:
            return ""
        # keywords = [(keyword, score)] 
        return keywords[0][0]


    def search_page(self, question: str) -> str:
        """
        Szuka tytułu strony Wikipedii dla pytania.
        """
        keyword = self.extract_keyword(question)
        print(f"Keyword: {keyword}")

        url = f"https://{self.language.value}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": keyword,
            "format": "json"
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get("query", {}).get("search", [])

        if not results:
            return None

        for r in results:
            title = r["title"]
            if keyword.lower() in title.lower():
                return title

        # pierwszy wynik
        return results[0]["title"]

    def get_page_summary(self, title):
        url = f"https://{self.language.value}.wikipedia.org/api/rest_v1/page/summary/{title}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None

        return response.json()

