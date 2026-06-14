from datetime import date

from pydantic import BaseModel


class PriceItemOut(BaseModel):
    symbol: str
    price_usd: float | None = None
    change_24h: float | None = None


class NewsItemOut(BaseModel):
    id: str
    title: str | None = None
    url: str | None = None
    source: str | None = None
    published_at: str | None = None
    vote: str | None = None


class SocialSentimentItemOut(BaseModel):
    symbol: str
    change_24h: float | None = None
    sentiment: str  # BULLISH | BEARISH | NEUTRAL


class SocialOut(BaseModel):
    content_id: str
    items: list[SocialSentimentItemOut] = []
    vote: str | None = None


class AIInsightOut(BaseModel):
    content_id: str
    content: str
    generated_date: date
    vote: str | None = None


class MemeOut(BaseModel):
    id: str
    content_id: str
    url: str
    caption: str | None = None
    vote: str | None = None


class DashboardOut(BaseModel):
    # Sections are populated only when the matching content type is selected
    # (CHARTS -> prices, NEWS -> news, SOCIAL -> social, FUN -> meme); the AI
    # insight is always shown.
    prices: list[PriceItemOut] | None = None
    news: list[NewsItemOut] | None = None
    social: SocialOut | None = None
    ai_insight: AIInsightOut
    meme: MemeOut | None = None
