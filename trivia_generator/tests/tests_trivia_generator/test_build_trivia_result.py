import pytest
from models import TriviaResult

def test_build_trivia_result_with_source(trivia_generator):
    # Arrange
    text = "Ciekawostka testowa (https://example.com)."
    
    # Act
    result = trivia_generator._build_trivia_result(text)
    
    # Assert
    assert isinstance(result, TriviaResult)
    assert result.source.url == "https://example.com"


def test_build_trivia_result_no_source(trivia_generator):
    # Arrange
    text = "Ciekawostka bez linku"
    
    # Act
    result = trivia_generator._build_trivia_result(text)
    
    # Assert
    assert isinstance(result, TriviaResult)
    assert result.source is None


def test_build_trivia_result_wrong_brackets(trivia_generator):
    # Arrange
    text = "Ciekawostka [https://example.com]"
    
    # Act
    result = trivia_generator._build_trivia_result(text)
    
    # Assert
    assert result.source is None