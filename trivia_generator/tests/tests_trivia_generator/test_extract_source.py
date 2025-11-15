import pytest

def test_extract_source_valid(trivia_generator):
    # Arrange
    generator = trivia_generator
    text = "Test (https://abc.pl)"

    # Act
    result = generator._extract_source(text)

    # Assert
    assert result == "https://abc.pl"


def test_extract_source_missing(trivia_generator):
    # Arrange
    generator = trivia_generator
    text = "Brak linku tutaj."

    # Act
    result = generator._extract_source(text)

    # Assert
    assert result is None