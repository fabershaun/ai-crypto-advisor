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
    except httpx.HTTPError:
        return {}

    id_to_symbol = {coingecko_id: symbol for symbol, coingecko_id in ASSET_ID_MAP.items()}
    prices = {}
    for coin_id, values in data.items():
        symbol = id_to_symbol.get(coin_id)
        if symbol:
            prices[symbol] = {
                "price_usd": values.get("usd"),
                "change_24h": values.get("usd_24h_change"),
            }
    return prices
