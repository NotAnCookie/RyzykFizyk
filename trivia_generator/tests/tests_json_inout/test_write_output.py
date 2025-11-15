import pytest
from communication import json_inout

def test_write_output_with_source():
    # Arrange
    trivia = "Ciekawostka"
    source = "https://example.com"

    # Act
    json_str = json_inout.write_output(trivia, source)

    # Assert
    assert '"trivia": "Ciekawostka"' in json_str
    assert '"source": "https://example.com"' in json_str


def test_write_output_without_source():
    # Arrange
    trivia = "Ciekawostka"

    # Act
    json_str = json_inout.write_output(trivia)

    # Assert
    assert '"trivia": "Ciekawostka"' in json_str
    assert '"source"' not in json_str