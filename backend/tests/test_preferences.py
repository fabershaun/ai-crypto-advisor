def _signup_and_login(client, email="dave@example.com"):
    client.post(
        "/auth/signup",
        json={"name": "Dave", "email": email, "password": "secret123"},
    )
    login_response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_preferences_without_token(client):
    response = client.get("/preferences")
    assert response.status_code == 401


def test_get_preferences_empty_by_default(client):
    headers = _signup_and_login(client)

    response = client.get("/preferences", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["investor_type"] is None
    assert data["content_types"] == []
    assert data["assets"] == []


def test_upsert_and_get_preferences(client):
    headers = _signup_and_login(client)
    payload = {
        "investor_type": "HODLER",
        "content_types": ["NEWS", "CHARTS"],
        "assets": ["BTC", "ETH"],
    }

    response = client.post("/preferences", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["investor_type"] == "HODLER"
    assert sorted(data["content_types"]) == ["CHARTS", "NEWS"]
    assert sorted(data["assets"]) == ["BTC", "ETH"]

    get_response = client.get("/preferences", headers=headers)
    assert get_response.json() == data


def test_upsert_preferences_replaces_existing(client):
    headers = _signup_and_login(client)
    client.post(
        "/preferences",
        json={"investor_type": "HODLER", "content_types": ["NEWS"], "assets": ["BTC"]},
        headers=headers,
    )

    response = client.post(
        "/preferences",
        json={
            "investor_type": "DAY_TRADER",
            "content_types": ["CHARTS", "FUN"],
            "assets": ["ETH", "SOL"],
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["investor_type"] == "DAY_TRADER"
    assert sorted(data["content_types"]) == ["CHARTS", "FUN"]
    assert sorted(data["assets"]) == ["ETH", "SOL"]


def test_upsert_preferences_invalid_investor_type(client):
    headers = _signup_and_login(client)

    response = client.post(
        "/preferences",
        json={"investor_type": "INVALID", "content_types": [], "assets": []},
        headers=headers,
    )
    assert response.status_code == 422
