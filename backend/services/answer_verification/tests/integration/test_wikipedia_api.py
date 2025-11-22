import pytest
from wikipedia_client import WikipediaClient
from enums import Language

pytestmark = pytest.mark.integration 

def test_wikipedia_search_real():
    # Arrange
    client = WikipediaClient(language=Language.PL)
    query = "Ile kilometrów ma rzeka Wisła"
    
    # Act
    title = client.search_page(query)
    
    # Print
    print(f"Search result for '{query}': {title}")
    
    # Assert
    assert title is None or isinstance(title, str)
    if title:
        assert len(title) > 0 


def test_wikipedia_summary_real():
    # Arrnge
    client = WikipediaClient(language=Language.PL)
    page = "Wisła"

    # Act
    summary = client.get_page_summary(page)

    # Assert
    assert summary is not None
    assert "title" in summary and isinstance(summary["title"], str)
    assert "extract" in summary and isinstance(summary["extract"], str)
    assert len(summary["extract"]) > 10 

