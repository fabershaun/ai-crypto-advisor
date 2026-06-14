import json
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx

COINDESK_RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"
FALLBACK_NEWS_FILE = Path(__file__).resolve().parent.parent / "data" / "fallback_news.json"


def _load_fallback_news(limit: int) -> list[dict]:
    try:
        with open(FALLBACK_NEWS_FILE, encoding="utf-8") as f:
            return json.load(f)[:limit]
    except (OSError, json.JSONDecodeError):
        return []


def get_news(symbols: list[str], limit: int = 5) -> list[dict]:
    try:
        response = httpx.get(COINDESK_RSS_URL, timeout=10, follow_redirects=True)
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except (httpx.HTTPError, ET.ParseError):
        # Live feed unavailable (e.g. network error or provider outage) ->
        # fall back to a curated static list so the section is never empty.
        return _load_fallback_news(limit)

    news = []
    for item in root.findall("./channel/item")[:limit]:
        pub_date = item.findtext("pubDate")
        published_at = None
        if pub_date:
            try:
                published_at = parsedate_to_datetime(pub_date).isoformat()
            except (TypeError, ValueError):
                published_at = None

        link = item.findtext("link")
        news.append(
            {
                "id": item.findtext("guid") or link,
                "title": item.findtext("title"),
                "url": link,
                "source": "CoinDesk",
                "published_at": published_at,
            }
        )

    # Empty/malformed-but-parseable feed -> use the static fallback too.
    return news or _load_fallback_news(limit)
