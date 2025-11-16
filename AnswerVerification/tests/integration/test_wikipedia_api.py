import pytest
from wikipedia_client import WikipediaClient

pytestmark = pytest.mark.integration  # oznacz wszystko jako integracyjne

def test_wikipedia_search_real():
    client = WikipediaClient(language="pl")
    title = client.search_page("Ile kilometrów ma Wisła")

    assert title is None or isinstance(title, str)



def test_wikipedia_summary_real():
    # Arrange
    client = WikipediaClient(language="pl")

    # Act
    summary = client.get_page_summary("Wisła")

    # Assert
    assert summary is not None
    assert "title" in summary
    assert "extract" in summary
    assert len(summary["extract"]) > 10
