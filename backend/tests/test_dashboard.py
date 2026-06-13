from datetime import date
from unittest.mock import patch

from app.models.vote import Vote


def _signup_login_and_onboard(client, email="frank@example.com", **prefs):
    client.post(
        "/auth/signup",
        json={"name": "Frank", "email": email, "password": "secret123"},
    )
    login_response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "investor_type": "HODLER",
        "content_types": ["NEWS"],
        "assets": ["BTC", "ETH"],
    }
    payload.update(prefs)
    client.post("/preferences", json=payload, headers=headers)
    return headers


def test_dashboard_without_token(client):
    response = client.get("/dashboard")
    assert response.status_code == 401


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_aggregates_and_caches_insight(mock_prices, mock_news, mock_insight, client):
    mock_prices.return_value = {
        "BTC": {"price_usd": 67000, "change_24h": 1.5},
        "ETH": {"price_usd": 3500, "change_24h": -0.5},
    }
    mock_news.return_value = [
        {
            "id": "123",
            "title": "Bitcoin hits new high",
            "url": "https://example.com/1",
            "source": "Example News",
            "published_at": "2026-06-12T00:00:00Z",
        }
    ]
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client)

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["prices"] == [
        {"symbol": "BTC", "price_usd": 67000, "change_24h": 1.5},
        {"symbol": "ETH", "price_usd": 3500, "change_24h": -0.5},
    ]
    assert data["news"][0]["id"] == "123"
    assert data["news"][0]["vote"] is None
    assert data["ai_insight"]["content"] == "Today's insight: markets are calm."
    assert data["ai_insight"]["generated_date"] == date.today().isoformat()
    assert data["ai_insight"]["vote"] is None
    assert "id" in data["meme"]
    assert "url" in data["meme"]

    response2 = client.get("/dashboard", headers=headers)
    assert response2.status_code == 200
    assert response2.json()["ai_insight"]["content"] == "Today's insight: markets are calm."

    mock_insight.assert_called_once()


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_strips_redundant_title_and_markdown_from_insight(
    mock_prices, mock_news, mock_insight, client
):
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = (
        "**Insight of the Day**\nBTC is **up** today, a solid move for HODLERs."
    )

    headers = _signup_login_and_onboard(client)

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    content = response.json()["ai_insight"]["content"]
    assert "Insight of the Day" not in content
    assert "**" not in content
    assert content == "BTC is up today, a solid move for HODLERs."


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_includes_existing_vote_for_news(
    mock_prices, mock_news, mock_insight, client, db_session
):
    mock_prices.return_value = {}
    mock_news.return_value = [
        {
            "id": "123",
            "title": "Bitcoin hits new high",
            "url": "https://example.com/1",
            "source": "Example News",
            "published_at": "2026-06-12T00:00:00Z",
        }
    ]
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, email="grace@example.com")
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    db_session.add(Vote(user_id=user_id, content_type="NEWS", content_id="123", vote="UP"))
    db_session.commit()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["news"][0]["vote"] == "UP"


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_includes_existing_vote_for_ai_insight(
    mock_prices, mock_news, mock_insight, client, db_session
):
    mock_prices.return_value = {}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, email="heidi@example.com")
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    content_id = f"AI_INSIGHT:{date.today().isoformat()}"
    db_session.add(Vote(user_id=user_id, content_type="AI_INSIGHT", content_id=content_id, vote="DOWN"))
    db_session.commit()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["ai_insight"]["vote"] == "DOWN"
