import pytest
from wikipedia_client import WikipediaClient
from enums import Language

pytestmark = pytest.mark.integration 

def test_wikipedia_search_real():
    client = WikipediaClient(language=Language.PL.value)
    query = "Ile kilometrów ma rzeka Wisła"
    
    title = client.search_page(query)
    
    print(f"Search result for '{query}': {title}")
    
    assert title is None or isinstance(title, str)
    if title:
        assert len(title) > 0 


def test_wikipedia_summary_real():
    client = WikipediaClient(language=Language.PL.value)
    page = "Wisła"

    summary = client.get_page_summary(page)
    
    #print(f"Summary for '{page}': {summary}")

    assert summary is not None
    assert "title" in summary and isinstance(summary["title"], str)
    assert "extract" in summary and isinstance(summary["extract"], str)
    assert len(summary["extract"]) > 10  
    import re
    numbers = re.findall(r'\d+(?:[\.,]\d+)?', summary["extract"])
    #print(f"Numbers found in extract: {numbers}")

