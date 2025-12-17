from fastapi.testclient import TestClient
from main import app
import json
import pytest

client = TestClient(app)

@pytest.mark.google
def test_verify_endpoint():
    response = client.post("/verify/", json={"question_id": "Ile wynosi 2+2?", "answer": "4", "language": "pl"})
    assert response.status_code == 200
    assert "correct" in response.json()


@pytest.mark.google
def test_verify_endpoint_validate_source():
    # ARRANGE
    payload = {
        "question_id": "Ile kilometrów ma Wisła?",
        "answer": "1022",
        "language": "pl"
    }

    # ACT
    response = client.post("/verify/", json=payload)

    # Print
    print("\n=== RESPONSE JSON ===")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    data = response.json()

    # ASSERT
    assert response.status_code == 200

    assert "source" in data
    source = data["source"]

    assert "url" in source
    assert "wikipedia.org" in source["url"].lower()

    assert "title" in source
    assert "wisła" in source["title"].lower()

@pytest.mark.google
def test_verify_endpoint_validate_source_eng():
    # ARRANGE
    payload = {
        "question_id": "How many kilometers has Danube river?",
        "answer": "2857",
        "language": "en"
    }

    # ACT
    response = client.post("/verify/", json=payload)

    # Print
    print("\n=== RESPONSE JSON ===")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    data = response.json()

    # ASSERT
    assert response.status_code == 200

    assert "source" in data
    source = data["source"]

    assert "url" in source
    assert "wikipedia.org" in source["url"].lower()

    assert "title" in source
    assert "danube" in source["title"].lower()

