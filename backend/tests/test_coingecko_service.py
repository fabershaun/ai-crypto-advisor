from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services import coingecko


@pytest.fixture(autouse=True)
def clear_price_cache():
    coingecko._price_cache.clear()
    yield
    coingecko._price_cache.clear()


def test_get_prices_empty_symbols():
    assert coingecko.get_prices([]) == {}


def test_get_prices_ignores_unknown_symbols():
    assert coingecko.get_prices(["NOT_A_COIN"]) == {}


def test_get_prices_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"usd": 67000, "usd_24h_change": 1.5},
        "ethereum": {"usd": 3500, "usd_24h_change": -0.5},
    }
    mock_response.raise_for_status.return_value = None

    with patch("app.services.coingecko.httpx.get", return_value=mock_response) as mock_get:
        prices = coingecko.get_prices(["BTC", "ETH"])

    mock_get.assert_called_once()
    assert prices["BTC"] == {"price_usd": 67000, "change_24h": 1.5}
    assert prices["ETH"] == {"price_usd": 3500, "change_24h": -0.5}


def test_get_prices_handles_http_error_with_no_cache():
    with patch("app.services.coingecko.httpx.get", side_effect=httpx.HTTPError("boom")):
        assert coingecko.get_prices(["BTC"]) == {}


def test_get_prices_falls_back_to_cache_on_http_error():
    mock_response = MagicMock()
    mock_response.json.return_value = {"bitcoin": {"usd": 67000, "usd_24h_change": 1.5}}
    mock_response.raise_for_status.return_value = None

    with patch("app.services.coingecko.httpx.get", return_value=mock_response):
        coingecko.get_prices(["BTC"])

    with patch("app.services.coingecko.httpx.get", side_effect=httpx.HTTPError("boom")):
        prices = coingecko.get_prices(["BTC"])

    assert prices["BTC"] == {"price_usd": 67000, "change_24h": 1.5}


def test_get_prices_falls_back_to_cache_for_missing_symbol():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"usd": 67000, "usd_24h_change": 1.5},
        "ethereum": {"usd": 3500, "usd_24h_change": -0.5},
    }
    mock_response.raise_for_status.return_value = None
    with patch("app.services.coingecko.httpx.get", return_value=mock_response):
        coingecko.get_prices(["BTC", "ETH"])

    # next response only includes BTC, e.g. a partial/rate-limited reply
    mock_response2 = MagicMock()
    mock_response2.json.return_value = {"bitcoin": {"usd": 68000, "usd_24h_change": 2.0}}
    mock_response2.raise_for_status.return_value = None
    with patch("app.services.coingecko.httpx.get", return_value=mock_response2):
        prices = coingecko.get_prices(["BTC", "ETH"])

    assert prices["BTC"] == {"price_usd": 68000, "change_24h": 2.0}
    assert prices["ETH"] == {"price_usd": 3500, "change_24h": -0.5}
