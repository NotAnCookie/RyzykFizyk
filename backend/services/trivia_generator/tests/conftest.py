# conftest.py
import pytest

from dotenv import load_dotenv
load_dotenv()

def pytest_addoption(parser):
    parser.addoption(
        "--runai", action="store_true", default=False, help="Run tests marked as ai"
    )

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--runai"):
        skip_ai = pytest.mark.skip(reason="Skipped unless --runai is used")
        for item in items:
            if "ai" in item.keywords:
                item.add_marker(skip_ai)
