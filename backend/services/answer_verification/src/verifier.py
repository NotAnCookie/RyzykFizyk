import re
from app.services.answer_verification.src.models import VerificationRequest, VerificationResult, SourceMetadata
from app.services.answer_verification.src.wikipedia_client import WikipediaClient
from app.services.answer_verification.src.enums import Language

class AnswerVerifier:
    def __init__(self, wikipedia_client=None):
        self.wikipedia_client = wikipedia_client

    def verify(self, request: VerificationRequest) -> VerificationResult:
        wiki = self.wikipedia_client or WikipediaClient(
            language = Language(request.language)
        )
        print(f"{request.language}")

        title = wiki.search_page(request.question_text)
        if not title:
            return VerificationResult(
                verified_answer=None,
                source=None
            )

        summary = wiki.get_page_summary(title)
        if not summary:
            return VerificationResult(
                verified_answer=None,
                source=None
            )

        url = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        extract = summary.get("extract", "")

        source = SourceMetadata(
            title=summary.get("title"),
            site_name="Wikipedia",
            url=url
        )

        return VerificationResult(
            verified_answer=request.numeric_answer,
            source=source,
        )





