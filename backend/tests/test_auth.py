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
