from app.models.user import User


def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_signup_duplicate_email(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "secret123"}
    first = client.post("/auth/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/signup", json=payload)
    assert second.status_code == 409


def test_login_success(client):
    client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login", json={"email": "alice@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login", json={"email": "alice@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token(client):
    client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    login_response = client.post(
        "/auth/login", json={"email": "alice@example.com", "password": "secret123"}
    )
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_me_with_malformed_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_with_token_for_deleted_user(client, db_session):
    client.post(
        "/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    login_response = client.post(
        "/auth/login", json={"email": "alice@example.com", "password": "secret123"}
    )
    token = login_response.json()["access_token"]

    user = db_session.query(User).filter(User.email == "alice@example.com").first()
    db_session.delete(user)
    db_session.commit()

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
