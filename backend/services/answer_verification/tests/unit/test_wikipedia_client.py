import pytest
from unittest.mock import MagicMock, patch
from wikipedia_client import WikipediaClient

@pytest.fixture
def client_with_mocked_yake():
    client = WikipediaClient()
    client.kw_extractor = MagicMock()
    return client

@pytest.fixture
def client_with_keyword():
    client = WikipediaClient()
    client.extract_keyword = MagicMock()
    return client


def test_extract_keyword_returns_first_keyword(client_with_mocked_yake):
    # Arrange
    client_with_mocked_yake.kw_extractor.extract_keywords.return_value = [("Polska", 0.1)]

    # Act
    result = client_with_mocked_yake.extract_keyword("Jaka jest stolica Polski?")

    # Assert
    assert result == "Polska"


@patch("wikipedia_client.requests.get")
def test_search_page_returns_matching_title(mock_get, client_with_keyword):
    # Arrange
    client = client_with_keyword
    client.extract_keyword.return_value = "Polska"
    
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "query": {"search": [{"title": "Polska"}]}
    }

    # Act
    result = client.search_page("pytanie")

    # Assert
    assert result == "Polska"


@patch("wikipedia_client.requests.get")
def test_search_page_returns_first_result_when_no_exact_match(mock_get, client_with_keyword):
    # Arrange
    client = client_with_keyword
    client.extract_keyword.return_value = "Gdańsk"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": {
            "search": [
                {"title": "Miasta Polski"},
                {"title": "Warszawa – historia"}
            ]
        }
    }
    mock_get.return_value = mock_response

    # Act
    result = client.search_page("Jakie jest największe miasto w Polsce?")

    # Assert
    assert result == "Miasta Polski"

    
@patch("wikipedia_client.requests.get")
def test_search_page_returns_exact_match(mock_get, client_with_keyword):
    # Arrange
    client = client_with_keyword
    client.extract_keyword.return_value = "Polska"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": {
            "search": [
                {"title": "Historia Polski"},
                {"title": "Polska"},
            ]
        }
    }
    mock_get.return_value = mock_response

    # Act
    result = client.search_page("Pytanie o Polskę")

    # Assert
    assert result == "Polska"


