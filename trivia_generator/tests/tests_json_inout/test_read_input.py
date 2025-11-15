import pytest
from communication import json_inout

def test_read_input_valid():
    # Arrange
    json_str = '{"question": "Co to jest kosmos?"}'

    # Act
    data = json_inout.read_input(json_str)

    # Assert
    assert isinstance(data, dict)
    assert "question" in data
    assert data["question"] == "Co to jest kosmos?"


def test_read_input_missing_question():
    # Arrange
    json_str = '{"text": "nie ma question"}'

    # Act / Assert
    with pytest.raises(ValueError, match="Brak klucza 'question'"):
        json_inout.read_input(json_str)


def test_read_input_invalid_json():
    # Arrange
    json_str = '{"question": "abc",}'  # niepoprawny JSON

    # Act / Assert
    with pytest.raises(ValueError, match="Błędny format JSON"):
        json_inout.read_input(json_str)