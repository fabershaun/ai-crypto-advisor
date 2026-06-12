from app.models.vote import Vote


def _signup_and_login(client, email="ivan@example.com"):
    client.post("/auth/signup", json={"name": "Ivan", "email": email, "password": "secret123"})
    login_response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_votes_without_token(client):
    response = client.post(
        "/votes", json={"content_type": "NEWS", "content_id": "123", "vote": "UP"}
    )
    assert response.status_code == 401


def test_create_vote(client, db_session):
    headers = _signup_and_login(client)

    response = client.post(
        "/votes",
        json={"content_type": "NEWS", "content_id": "123", "vote": "UP"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"content_type": "NEWS", "content_id": "123", "vote": "UP"}

    user_id = client.get("/auth/me", headers=headers).json()["id"]
    votes = db_session.query(Vote).filter(Vote.user_id == user_id).all()
    assert len(votes) == 1
    assert votes[0].vote == "UP"


def test_vote_upsert_updates_existing(client, db_session):
    headers = _signup_and_login(client, email="judy@example.com")

    client.post(
        "/votes",
        json={"content_type": "MEME", "content_id": "meme-1", "vote": "UP"},
        headers=headers,
    )
    response = client.post(
        "/votes",
        json={"content_type": "MEME", "content_id": "meme-1", "vote": "DOWN"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["vote"] == "DOWN"

    user_id = client.get("/auth/me", headers=headers).json()["id"]
    votes = (
        db_session.query(Vote)
        .filter(Vote.user_id == user_id, Vote.content_type == "MEME")
        .all()
    )
    assert len(votes) == 1
    assert votes[0].vote == "DOWN"


def test_vote_invalid_content_type(client):
    headers = _signup_and_login(client, email="kane@example.com")

    response = client.post(
        "/votes",
        json={"content_type": "INVALID", "content_id": "1", "vote": "UP"},
        headers=headers,
    )
    assert response.status_code == 422
