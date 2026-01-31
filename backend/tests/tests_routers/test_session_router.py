from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers.session_router import get_session_router
from schemas.enums import SessionState


class FakeSessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, player, language, category_id):
        session = SimpleNamespace(
            id=len(self.sessions) + 1,
            player=player,
            language=language,
            category=category_id,
            state=SessionState.INIT,
            questions=[],
            answers=[],
            currentQuestion=0,
        )
        self.sessions[session.id] = session
        return session

    async def start_session(self, session_id):
        return self.sessions[session_id]

    async def get_next_question(self, session_id):
        return SimpleNamespace(
            id=1,
            text="Q?",
            topic="Test topic",
            answer="1",
            category=self.sessions[session_id].category,
            trivia="Some trivia",
            sourceUrl="https://example.com"
        )

    async def submit_answer(self, session_id, answer):
        return SimpleNamespace(
            sourceUrl="https://example.com",
            trivia="Some trivia"
        )

    def end_session(self, session_id):
        return self.sessions.get(session_id)

@pytest.fixture
def client():
    fake_sm = FakeSessionManager()

    app = FastAPI()
    app.include_router(get_session_router(fake_sm))

    return TestClient(app)




def test_create_session_sets_cookie(client):
    res = client.post("/session/create", json={
        "player_id": 1,
        "player_name": "Tester",
        "player_email": "test@mail.com",
        "language": "pl",
        "category": "geography"
    })

    assert res.status_code == 200
    assert "session_id" in res.cookies
    body = res.json()
    assert body["current_question_index"] == 0


def test_next_question_returns_question(client):
    res = client.post("/session/create", json={
        "player_id": 1,
        "player_name": "Tester",
        "player_email": "test@mail.com",
        "language": "pl",
        "category": "geography"
    })
    cookies = res.cookies

    q = client.post("/session/next_question", cookies=cookies)
    assert q.status_code == 200
    data = q.json()
    assert data["text"] == "Q?"
    assert data["topic"] == "Test topic"


def test_summary_too_early(client):
    res = client.post("/session/create", json={
        "player_id": 1,
        "player_name": "Tester",
        "player_email": "test@mail.com",
        "language": "pl",
        "category": "geography"
    })
    cookies = res.cookies

    summary = client.get("/session/summary", cookies=cookies)
    assert summary.status_code == 400


def test_sessions_are_isolated(client):
    s1 = client.post("/session/create", json={
        "player_id": 1,
        "player_name": "A",
        "player_email": "a@mail.com",
        "language": "pl",
        "category": "geography"
    })
    s2 = client.post("/session/create", json={
        "player_id": 2,
        "player_name": "B",
        "player_email": "b@mail.com",
        "language": "pl",
        "category": "geography"
    })

    # Pobieramy pytanie z każdej sesji
    q1 = client.post("/session/next_question", cookies=s1.cookies)
    q2 = client.post("/session/next_question", cookies=s2.cookies)

    # Sprawdzamy, że sesje są różne na podstawie player_id lub cookie session_id
    assert s1.cookies["session_id"] != s2.cookies["session_id"]
    assert q1.json()["text"] == "Q?"
    assert q2.json()["text"] == "Q?"
