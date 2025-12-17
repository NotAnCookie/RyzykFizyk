# conftest.py
import pytest
from dotenv import load_dotenv

load_dotenv()

def pytest_addoption(parser):
    parser.addoption(
        "--rungoogle",
        action="store_true",
        default=False,
        help="Run tests marked as google",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--rungoogle"):
        skip_google = pytest.mark.skip(reason="Skipped unless --rungoogle is used")
        for item in items:
            if "google" in item.keywords:
                item.add_marker(skip_google)
