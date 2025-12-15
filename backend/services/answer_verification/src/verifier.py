import re
from services.answer_verification.src.models import VerificationRequest, VerificationResult, SourceMetadata
from services.answer_verification.src.wikipedia_client import WikipediaClient
from services.answer_verification.src.enums import Language
from services.answer_verification.src.communication.google_client import GoogleSearchClient

class AnswerVerifier:
    def __init__(self, wikipedia_client=None,google_client: GoogleSearchClient | None = None):
        self.wikipedia_client = wikipedia_client
        self.google_client = google_client

    def verify_wikipedia(self, request: VerificationRequest) -> VerificationResult:
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
    

    def verify(self, request: VerificationRequest) -> VerificationResult:
        try:
            result = self.verify_google(request)
            if result and result.source:
                return result

        except Exception as e:
            print(f"[GoogleSearch] error -> fallback to Wikipedia: {e}")

        return self.verify_wikipedia(request)


    def build_google_query(self, question: str) -> str:
        q = question.lower()
        q = re.sub(r"\[.*?\]", "", q)
        q = re.sub(r"wynosi.*", "", q)
        return q.strip()


    def verify_google(self, request: VerificationRequest) -> VerificationResult:
        if not self.google_client:
            self.google_client = GoogleSearchClient(
                language=request.language
            )

        query = self.build_google_query(request.question_text)
        google_result = self.google_client.search_wikipedia_link(
            query
        )

        # google_result = self.google_client.search_wikipedia_link(
        #     request.question_text
        # )

        if not google_result:
            return VerificationResult(
                verified_answer=None,
                source=None
            )


        return VerificationResult(
            verified_answer=request.numeric_answer,
            source=SourceMetadata(
                title=google_result["title"],
                site_name="Wikipedia",
                url=google_result["url"]
            )
        )





