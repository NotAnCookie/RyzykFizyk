import pytest

def test_generate_trivia_valid_input(trivia_generator):
    # Arrange
    generator = trivia_generator

    # Act
    result = generator.generate_trivia("kosmos")

    # Assert
    assert result["trivia"].startswith("Ciekawostka")
    assert result["source"] == "https://example.com"

def test_generate_trivia_invalid_input_empty(trivia_generator):
    # Arrange
    generator = trivia_generator

    # Act / Assert
    with pytest.raises(ValueError):
        generator.generate_trivia("")



def test_generate_trivia_invalid_input_too_short(trivia_generator):
    # Arrange
    generator = trivia_generator

    # Act / Assert
    with pytest.raises(ValueError):
        generator.generate_trivia("ja")

