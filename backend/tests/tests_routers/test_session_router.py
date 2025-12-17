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


def test_submit_answer_updates_question(client):
    create = client.post("/session/create", json={
        "player_id": 1,
        "player_name": "Tester",
        "player_email": "test@mail.com",
        "language": "pl",
        "category": "geography"
    })
    cookies = create.cookies

    q = client.post("/session/next_question", cookies=cookies).json()

    res = client.post(
        "/session/submit_answer",
        cookies=cookies,
        json={
            "question_id": q["id"],
            "value": 42
        }
    )

    assert res.status_code == 200
    updated = res.json()
    assert updated["sourceUrl"] == "https://example.com"
    assert updated["trivia"] == "Some trivia"


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
