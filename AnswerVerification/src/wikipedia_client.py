import requests

class WikipediaClient:
    def __init__(self, language="pl"):
        self.language = language.lower()
        self.headers = {
            "User-Agent": "RyzykFizyk/1.0 (contact: agabibek1@gmail.com)"
        }

    def search_page(self, query: str):
        url = f"https://{self.language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            return None

        data = response.json()

        if not data.get("query", {}).get("search"):
            return None

        return data["query"]["search"][0]["title"]

    def get_page_summary(self, title):
        url = f"https://{self.language}.wikipedia.org/api/rest_v1/page/summary/{title}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None

        return response.json()
