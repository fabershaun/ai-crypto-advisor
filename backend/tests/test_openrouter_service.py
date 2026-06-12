from unittest.mock import MagicMock, patch

import httpx

from app.core.config import settings
from app.services import openrouter


def test_generate_insight_without_api_key_returns_fallback(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_api_key", "")
    assert openrouter.generate_insight("prompt") == openrouter.FALLBACK_INSIGHT


def test_generate_insight_success(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_api_key", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "  Here is your insight.  "}}]
    }
    mock_response.raise_for_status.return_value = None

    with patch("app.services.openrouter.httpx.post", return_value=mock_response) as mock_post:
        result = openrouter.generate_insight("prompt")

    mock_post.assert_called_once()
    assert result == "Here is your insight."


def test_generate_insight_handles_http_error(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_api_key", "test-key")

    with patch("app.services.openrouter.httpx.post", side_effect=httpx.HTTPError("boom")):
        assert openrouter.generate_insight("prompt") == openrouter.FALLBACK_INSIGHT


def test_generate_insight_handles_malformed_response(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_api_key", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {"unexpected": "shape"}
    mock_response.raise_for_status.return_value = None

    with patch("app.services.openrouter.httpx.post", return_value=mock_response):
        assert openrouter.generate_insight("prompt") == openrouter.FALLBACK_INSIGHT
