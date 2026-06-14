from unittest.mock import MagicMock, patch

import httpx

from app.services import crypto_news

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>CoinDesk</title>
    <item>
      <title><![CDATA[Bitcoin hits new high]]></title>
      <link>https://example.com/1</link>
      <guid isPermaLink="false">abc-123</guid>
      <pubDate>Fri, 12 Jun 2026 15:55:42 +0000</pubDate>
      <description><![CDATA[Some description]]></description>
    </item>
    <item>
      <title><![CDATA[Ethereum news]]></title>
      <link>https://example.com/2</link>
      <guid isPermaLink="false">def-456</guid>
      <pubDate>Fri, 12 Jun 2026 14:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>
"""


def _mock_response(text):
    mock_response = MagicMock()
    mock_response.text = text
    mock_response.raise_for_status.return_value = None
    return mock_response


def test_get_news_success():
    with patch(
        "app.services.crypto_news.httpx.get", return_value=_mock_response(SAMPLE_RSS)
    ) as mock_get:
        news = crypto_news.get_news(["BTC"])

    mock_get.assert_called_once()
    assert news == [
        {
            "id": "abc-123",
            "title": "Bitcoin hits new high",
            "url": "https://example.com/1",
            "source": "CoinDesk",
            "published_at": "2026-06-12T15:55:42+00:00",
        },
        {
            "id": "def-456",
            "title": "Ethereum news",
            "url": "https://example.com/2",
            "source": "CoinDesk",
            "published_at": "2026-06-12T14:00:00+00:00",
        },
    ]


def test_get_news_respects_limit():
    with patch("app.services.crypto_news.httpx.get", return_value=_mock_response(SAMPLE_RSS)):
        news = crypto_news.get_news(["BTC"], limit=1)

    assert len(news) == 1


def test_get_news_falls_back_to_static_on_http_error():
    with patch("app.services.crypto_news.httpx.get", side_effect=httpx.HTTPError("boom")):
        news = crypto_news.get_news(["BTC"])

    assert len(news) > 0
    assert all(item["source"] == "Static" for item in news)


def test_get_news_falls_back_to_static_on_parse_error():
    with patch(
        "app.services.crypto_news.httpx.get", return_value=_mock_response("not valid xml")
    ):
        news = crypto_news.get_news(["BTC"])

    assert len(news) > 0
    assert all(item["source"] == "Static" for item in news)


def test_get_news_fallback_respects_limit():
    with patch("app.services.crypto_news.httpx.get", side_effect=httpx.HTTPError("boom")):
        news = crypto_news.get_news(["BTC"], limit=2)

    assert len(news) == 2


def test_get_news_falls_back_when_feed_is_empty():
    empty_feed = '<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'
    with patch(
        "app.services.crypto_news.httpx.get", return_value=_mock_response(empty_feed)
    ):
        news = crypto_news.get_news(["BTC"])

    assert len(news) > 0
    assert all(item["source"] == "Static" for item in news)
