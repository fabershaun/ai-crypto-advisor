import httpx

from app.core.config import settings

CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"


def get_news(symbols: list[str], limit: int = 5) -> list[dict]:
    if not settings.cryptopanic_api_key:
        return []

    params = {
        "auth_token": settings.cryptopanic_api_key,
        "public": "true",
    }
    if symbols:
        params["currencies"] = ",".join(symbols)

    try:
        response = httpx.get(CRYPTOPANIC_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        return []

    news = []
    for post in data.get("results", [])[:limit]:
        news.append(
            {
                "id": str(post.get("id")),
                "title": post.get("title"),
                "url": post.get("url"),
                "source": (post.get("source") or {}).get("title"),
                "published_at": post.get("published_at"),
            }
        )
    return news
