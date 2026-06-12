from unittest.mock import MagicMock, patch

import httpx

from app.services import coingecko


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


def test_get_prices_handles_http_error():
    with patch("app.services.coingecko.httpx.get", side_effect=httpx.HTTPError("boom")):
        assert coingecko.get_prices(["BTC"]) == {}
