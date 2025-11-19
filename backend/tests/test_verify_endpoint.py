from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_verify_endpoint():
    response = client.post("/verify/", json={"question_id": "Ile wynosi 2+2?", "answer": "4"})
    assert response.status_code == 200
    assert "correct" in response.json()
