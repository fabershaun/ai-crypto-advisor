import httpx

from app.core.config import settings

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

ASSET_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "XRP": "ripple",
    "DOGE": "dogecoin",
}

# Last known-good price per symbol. CoinGecko's free tier rate-limits
# aggressively, so on a failed or partial fetch we fall back to these instead
# of showing nothing.
_price_cache: dict[str, dict] = {}


def get_prices(symbols: list[str]) -> dict[str, dict]:
    coin_ids = [ASSET_ID_MAP[symbol] for symbol in symbols if symbol in ASSET_ID_MAP]
    if not coin_ids:
        return {}

    headers = {}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key

    try:
        response = httpx.get(
            f"{COINGECKO_BASE_URL}/simple/price",
            params={
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        id_to_symbol = {coingecko_id: symbol for symbol, coingecko_id in ASSET_ID_MAP.items()}
        for coin_id, values in data.items():
            symbol = id_to_symbol.get(coin_id)
            if symbol:
                _price_cache[symbol] = {
                    "price_usd": values.get("usd"),
                    "change_24h": values.get("usd_24h_change"),
                }
    except httpx.HTTPError:
        pass

    requested_symbols = [symbol for symbol in symbols if symbol in ASSET_ID_MAP]
    return {
        symbol: _price_cache[symbol] for symbol in requested_symbols if symbol in _price_cache
    }
