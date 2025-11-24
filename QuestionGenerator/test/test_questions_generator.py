import pytest
from unittest.mock import MagicMock
from questions_generator import generate_question
from models import Question
from enums import Language

def test_generate_question_success(mock_wikipedia, mock_random, sample_category, sample_language):
    """
    Test the 'Happy Path': The API returns data, and a question is successfully generated.
    """
    
    # --- ARRANGE ---
    
    # 1. Mock the search results
    mock_wikipedia.search.return_value = ["Test Article Title"]
    
    # 2. Mock random choices.
    mock_random.choice.side_effect = [
        "test_keyword",       
        "Test Article Title", 
        ("This is a sentence with 100 items.", "100") 
    ]
    
    # 3. Mock the Wikipedia page content
    mock_page = MagicMock()
    mock_page.summary = "This is a sentence with 100 items. Some other text."
    mock_wikipedia.page.return_value = mock_page

    # --- ACT ---
    result = generate_question(category=sample_category, language=sample_language)

    # --- ASSERT ---
    assert isinstance(result, Question)
    assert result.topic == "Test Article Title"
    assert result.answer == "100"
    assert "[???]" in result.question_text
    assert result.category == sample_category
    assert result.language == sample_language
    
    # Verify the language was set correctly
    mock_wikipedia.set_lang.assert_called_with(sample_language.value)


def test_generate_question_no_search_results(mock_wikipedia, mock_random, sample_category, sample_language):
    # --- ARRANGE ---
    mock_random.choice.return_value = "test_keyword"
    
    # Simulate empty list returned by search
    mock_wikipedia.search.return_value = [] 

    # --- ACT ---
    result = generate_question(sample_category, sample_language)

    # --- ASSERT ---
    assert result is None


def test_generate_question_no_numbers_in_text(mock_wikipedia, mock_random, sample_category, sample_language):
    # --- ARRANGE ---
    mock_wikipedia.search.return_value = ["Text Only Article"]
    
    mock_random.choice.side_effect = ["kw", "Text Only Article"] * 10 

    mock_page = MagicMock()
    # Content with no digits
    mock_page.summary = "This is a very long text but it has absolutely no digits in it whatsoever."
    mock_wikipedia.page.return_value = mock_page

    # --- ACT ---
    result = generate_question(sample_category, sample_language)

    # --- ASSERT ---
    assert result is None


def test_generate_question_api_error(mock_wikipedia, mock_random, sample_category, sample_language):
    # --- ARRANGE ---
    mock_wikipedia.search.return_value = ["Broken Page"]
    mock_random.choice.return_value = "Broken Page"
    
    mock_wikipedia.page.side_effect = Exception("Wikipedia Down") 

    # --- ACT ---
    result = generate_question(sample_category, sample_language)

    # --- ASSERT ---
    assert result is None