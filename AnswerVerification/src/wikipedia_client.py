import requests
import yake
from pathlib import Path
from gpt4all import GPT4All
from enums import Language
import os

class WikipediaClient:
    def __init__(self, language="pl"):
        self.language = language  

        self.headers = {
            "User-Agent": "TriviaVerifier/1.0 (agabibek1@gmail.com)"
        }
        self.kw_extractor = yake.KeywordExtractor(lan=language, n=1, top=1)


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
        # Wyciągamy keyword z GPT
        keyword = self.extract_keyword(question)
        print(f"Keyword GPT4All: {keyword}")

        url = f"https://{self.language}.wikipedia.org/w/api.php"
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

        # Szukamy najlepszego dopasowania: tytuł zawiera keyword
        for r in results:
            title = r["title"]
            if keyword.lower() in title.lower():
                return title

        # fallback: pierwszy wynik
        return results[0]["title"]

    # def search_page(self, query: str):
    #     url = f"https://{self.language}.wikipedia.org/w/api.php"
    #     params = {
    #         "action": "query",
    #         "list": "search",
    #         "srsearch": query,
    #         "format": "json"
    #     }

    #     response = requests.get(url, params=params, headers=self.headers)

    #     if response.status_code != 200:
    #         return None

    #     data = response.json()

    #     if not data.get("query", {}).get("search"):
    #         return None

    #     return data["query"]["search"][0]["title"]

    def get_page_summary(self, title):
        url = f"https://{self.language}.wikipedia.org/api/rest_v1/page/summary/{title}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None

        return response.json()
    
    def search_pages(self, query: str, limit=5):
        url = f"https://{self.language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json"
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            return []

        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        return [r["title"] for r in search_results]

