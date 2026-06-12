from unittest.mock import MagicMock, patch

import httpx

from app.core.config import settings
from app.services import cryptopanic


def test_get_news_without_api_key_returns_empty(monkeypatch):
    monkeypatch.setattr(settings, "cryptopanic_api_key", "")
    assert cryptopanic.get_news(["BTC"]) == []


def test_get_news_success(monkeypatch):
    monkeypatch.setattr(settings, "cryptopanic_api_key", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": 123,
                "title": "Bitcoin hits new high",
                "url": "https://example.com/1",
                "source": {"title": "Example News"},
                "published_at": "2026-06-12T00:00:00Z",
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch("app.services.cryptopanic.httpx.get", return_value=mock_response) as mock_get:
        news = cryptopanic.get_news(["BTC"])

    mock_get.assert_called_once()
    assert news == [
        {
            "id": "123",
            "title": "Bitcoin hits new high",
            "url": "https://example.com/1",
            "source": "Example News",
            "published_at": "2026-06-12T00:00:00Z",
        }
    ]


def test_get_news_handles_http_error(monkeypatch):
    monkeypatch.setattr(settings, "cryptopanic_api_key", "test-key")

    with patch("app.services.cryptopanic.httpx.get", side_effect=httpx.HTTPError("boom")):
        assert cryptopanic.get_news(["BTC"]) == []
