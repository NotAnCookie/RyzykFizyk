import sys
import os

# To magiczna linijka: mówi Pythonowi "Hej, szukaj modułów też w folderze ../src"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import MagicMock
from models import Category
from enums import Language

@pytest.fixture
def sample_category():
    return Category(name="TestCategory", keywords=["test_keyword"])

@pytest.fixture
def sample_language():
    return Language.ENG

@pytest.fixture
def mock_wikipedia(mocker):
    mock_wiki = mocker.patch("questions_generator.wikipedia")
    mock_wiki.DisambiguationError = Exception
    mock_wiki.PageError = Exception
    return mock_wiki

@pytest.fixture
def mock_random(mocker):
    return mocker.patch("questions_generator.random")