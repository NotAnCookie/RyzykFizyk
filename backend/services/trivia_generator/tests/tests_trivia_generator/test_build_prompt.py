import pytest
from enums import *

def test_build_prompt_known_language(trivia_generator):
    # Arrange
    topic = "kosmos"
    
    # Act
    prompt = trivia_generator._build_prompt(topic, Language.PL)
    
    # Assert
    assert topic in prompt


def test_build_prompt_unknown_language(trivia_generator):
    # Arrange
    class FakeLang:
        value = "unknown"
    
    # Act
    prompt = trivia_generator._build_prompt("kosmos", FakeLang())
    
    # Assert
    assert "kosmos" in prompt  # wraca do PL

def test_build_prompt_selects_pl_template(trivia_generator):
    # Arrange
    topic = "kosmos"
    
    # Act
    prompt = trivia_generator._build_prompt(topic, Language.PL)
    
    # Assert
    assert topic in prompt
    assert "Opowiedz" in prompt 


def test_build_prompt_selects_en_template(trivia_generator):
    # Arrange
    topic = "space"
    
    # Act
    prompt = trivia_generator._build_prompt(topic, Language.ENG)
    
    # Assert
    assert topic in prompt
    assert "Tell" in prompt 