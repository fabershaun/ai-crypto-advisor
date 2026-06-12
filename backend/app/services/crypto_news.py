import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import httpx

COINDESK_RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"


def get_news(symbols: list[str], limit: int = 5) -> list[dict]:
    try:
        response = httpx.get(COINDESK_RSS_URL, timeout=10, follow_redirects=True)
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except (httpx.HTTPError, ET.ParseError):
        return []

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
    return news
