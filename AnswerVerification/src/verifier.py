import re
from schemas import VerificationRequest, VerificationResult, SourceMetadata
from wikipedia_client import WikipediaClient

class AnswerVerifier:
    def __init__(self, wikipedia_client=None):
        # jeśli moduł nie dostanie mocka → użyje prawdziwego klienta
        self.wikipedia_client = wikipedia_client

    def extract_numbers(self, text):
        return [float(x.replace(",", ".")) for x in re.findall(r'\d+(?:[\.,]\d+)?', text)]

    def verify(self, request: VerificationRequest) -> VerificationResult:
        # jeśli wstrzyknięto mock → używamy mocka
        # inaczej tworzymy prawdziwy WikipediaClient
        wiki = self.wikipedia_client or WikipediaClient(
            language="pl" if request.language == "PL" else "en"
        )
        
        title = wiki.search_page(request.question_text)
        if not title:
            raise ValueError("No Wikipedia page found")

        summary = wiki.get_page_summary(title)
        if not summary:
            raise ValueError("Cannot fetch Wikipedia summary")

        text = summary.get("extract", "")
        numbers = self.extract_numbers(text)

        source = SourceMetadata(
            title=summary.get("title"),
            site_name="Wikipedia",
            url=summary.get("content_urls", {}).get("desktop", {}).get("page")
        )

        return VerificationResult(
            verified_answer=request.numeric_answer,
            source=source
        )
