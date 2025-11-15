import pytest
from unittest.mock import patch

@patch("generator.trivia_generator.write_output")
def test_generate_json_response_calls_write_output(mock_write, trivia_generator):
    # Arrange
    generator = trivia_generator
    mock_write.return_value = '{"trivia": "...", "source": "..."}'

    # Act
    json_str = generator.generate_json_response("pies")

    # Assert
    mock_write.assert_called_once()
    assert '"trivia"' in json_str
    assert '"source"' in json_str