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
        "content_types": ["NEWS", "CHARTS", "SOCIAL", "FUN"],
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

    assert data["prices"]["content_id"].startswith("PRICE:")
    assert data["prices"]["items"] == [
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
def test_dashboard_skips_news_when_not_selected(mock_prices, mock_news, mock_insight, client):
    mock_prices.return_value = {}
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, content_types=["CHARTS"])

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["news"] is None
    mock_news.assert_not_called()


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_skips_prices_when_charts_not_selected(
    mock_prices, mock_news, mock_insight, client
):
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, content_types=["NEWS"])

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["prices"] is None


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_includes_existing_vote_for_prices(
    mock_prices, mock_news, mock_insight, client, db_session
):
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(
        client, email="oscar@example.com", content_types=["CHARTS"]
    )
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    content_id = f"PRICE:{date.today().isoformat()}"
    db_session.add(
        Vote(user_id=user_id, content_type="PRICE", content_id=content_id, vote="DOWN")
    )
    db_session.commit()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["prices"]["vote"] == "DOWN"


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_skips_meme_when_fun_not_selected(
    mock_prices, mock_news, mock_insight, client
):
    mock_prices.return_value = {}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, content_types=["NEWS"])

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["meme"] is None


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_social_section_classifies_sentiment(
    mock_prices, mock_news, mock_insight, client
):
    mock_prices.return_value = {
        "BTC": {"price_usd": 67000, "change_24h": 5.0},  # bullish
        "ETH": {"price_usd": 3500, "change_24h": -3.2},  # bearish
        "SOL": {"price_usd": 150, "change_24h": 0.4},  # neutral
    }
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(
        client, content_types=["SOCIAL"], assets=["BTC", "ETH", "SOL"]
    )

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    social = response.json()["social"]
    assert social["content_id"].startswith("SOCIAL:")
    sentiments = {item["symbol"]: item["sentiment"] for item in social["items"]}
    assert sentiments == {"BTC": "BULLISH", "ETH": "BEARISH", "SOL": "NEUTRAL"}


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_skips_social_when_not_selected(
    mock_prices, mock_news, mock_insight, client
):
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, content_types=["CHARTS"])

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["social"] is None


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_includes_existing_vote_for_social(
    mock_prices, mock_news, mock_insight, client, db_session
):
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(
        client, email="nina@example.com", content_types=["SOCIAL"]
    )
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    content_id = f"SOCIAL:{date.today().isoformat()}"
    db_session.add(
        Vote(user_id=user_id, content_type="SOCIAL", content_id=content_id, vote="UP")
    )
    db_session.commit()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["social"]["vote"] == "UP"


@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_returns_a_price_row_for_every_tracked_asset(
    mock_prices, mock_news, mock_insight, client
):
    # provider only knows BTC; ETH is missing from the response
    mock_prices.return_value = {"BTC": {"price_usd": 67000, "change_24h": 1.5}}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."

    headers = _signup_login_and_onboard(client, assets=["BTC", "ETH"])

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    prices = {p["symbol"]: p for p in response.json()["prices"]["items"]}
    assert prices["BTC"]["price_usd"] == 67000
    # missing asset still gets a row, with null values rather than being dropped
    assert prices["ETH"]["price_usd"] is None
    assert prices["ETH"]["change_24h"] is None


@patch("app.api.dashboard.random.choice")
@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_meme_rotates_each_load(
    mock_prices, mock_news, mock_insight, mock_choice, client
):
    mock_prices.return_value = {}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."
    # the meme is chosen dynamically per request, not fixed for the day
    mock_choice.side_effect = [
        {"id": "meme-2", "url": "/memes/meme-2.svg", "caption": "A"},
        {"id": "meme-4", "url": "/memes/meme-4.svg", "caption": "B"},
    ]

    headers = _signup_login_and_onboard(client)

    first = client.get("/dashboard", headers=headers).json()["meme"]
    second = client.get("/dashboard", headers=headers).json()["meme"]
    assert first["content_id"] == "MEME:meme-2"
    assert second["content_id"] == "MEME:meme-4"


@patch("app.api.dashboard.random.choice")
@patch("app.api.dashboard.openrouter.generate_insight")
@patch("app.api.dashboard.crypto_news.get_news")
@patch("app.api.dashboard.coingecko.get_prices")
def test_dashboard_includes_existing_vote_for_meme(
    mock_prices, mock_news, mock_insight, mock_choice, client, db_session
):
    mock_prices.return_value = {}
    mock_news.return_value = []
    mock_insight.return_value = "Today's insight: markets are calm."
    # pin the meme so the vote we insert lines up with what's rendered
    mock_choice.return_value = {"id": "meme-1", "url": "/memes/meme-1.svg", "caption": "x"}

    headers = _signup_login_and_onboard(client, email="mallory@example.com")
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    meme_content_id = client.get("/dashboard", headers=headers).json()["meme"]["content_id"]
    db_session.add(
        Vote(user_id=user_id, content_type="MEME", content_id=meme_content_id, vote="UP")
    )
    db_session.commit()

    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json()["meme"]["vote"] == "UP"


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
