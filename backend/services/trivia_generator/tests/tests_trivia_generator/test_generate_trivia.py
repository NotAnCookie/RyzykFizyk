import pytest
from generator.trivia_generator import TriviaGenerator
from models import TriviaRequest, TriviaResult, SourceMetadata
from enums import Language


def test_generate_trivia_valid_input(trivia_generator):
    # Arrange
    req = TriviaRequest(
        question_text="kosmos",
        language=Language.PL
    )

    # Act
    result = trivia_generator.generate_trivia(req)

    # Assert
    assert isinstance(result, TriviaResult)
    assert result.trivia.startswith("Ciekawostka")
    assert result.source is not None
    assert isinstance(result.source, SourceMetadata)
    assert result.source.url == "https://example.com"


def test_generate_trivia_invalid_input_empty(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator.generate_trivia(
            TriviaRequest(question_text="", language=Language.PL)
        )


def test_generate_trivia_invalid_input_too_short(trivia_generator):
    with pytest.raises(ValueError):
        trivia_generator.generate_trivia(
            TriviaRequest(question_text="ja", language=Language.PL)
        )


def test_generate_trivia_no_source_in_text(trivia_generator, mock_api_client):
    # Arrange
    mock_api_client.get_completion = lambda prompt: "Ciekawostka bez linku"
    generator = TriviaGenerator(api_client=mock_api_client)

    req = TriviaRequest(question_text="historia", language=Language.PL)

    # Act
    result = generator.generate_trivia(req)

    # Assert
    assert isinstance(result, TriviaResult)
    assert result.trivia == "Ciekawostka bez linku"
    assert result.source is None


