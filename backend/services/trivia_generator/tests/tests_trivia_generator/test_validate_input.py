import pytest

def test_validate_input_empty_string(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator._validate_input("")


def test_validate_input_too_short(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator._validate_input("aa")


def test_validate_input_whitespace(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator._validate_input("   ")


def test_validate_input_long_string(trivia_generator):
    # Arrange
    long_text = "a" * 1000
    
    # Act / Assert
    # * assert -> nie rzuca wyjątku
    trivia_generator._validate_input(long_text)


def test_validate_input_none(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator._validate_input(None)