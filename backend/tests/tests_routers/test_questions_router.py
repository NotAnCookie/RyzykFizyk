import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from routers.questions import router as questions_router
from services.question_generator.src.categories import AVAILABLE_CATEGORIES

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(questions_router)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_get_categories_returns_list(client):
    res = client.get("/api/questions/categories")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)
    assert len(data) == len(AVAILABLE_CATEGORIES)

def test_category_fields(client):
    res = client.get("/api/questions/categories")
    data = res.json()
    
    for item in data:
        assert "id" in item
        assert "name" in item
        category = AVAILABLE_CATEGORIES[item["id"]]
        assert item["name"] == category.name

def test_get_categories_not_empty(client):
    res = client.get("/api/questions/categories")
    data = res.json()
    assert len(data) > 0
