import json
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.ai_insight import AIInsight
from app.models.asset import UserAsset
from app.models.preference import UserContentPreference, UserPreference
from app.models.user import User
from app.models.vote import Vote
from app.schemas.dashboard_schema import (
    AIInsightOut,
    DashboardOut,
    MemeOut,
    NewsItemOut,
    PriceItemOut,
)
from app.services import coingecko, crypto_news, openrouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

MEMES_FILE = Path(__file__).resolve().parent.parent / "data" / "memes.json"


def _load_memes() -> list[dict]:
    with open(MEMES_FILE) as f:
        return json.load(f)


def _get_votes_map(db: Session, user_id: int, content_type: str) -> dict[str, str]:
    votes = (
        db.query(Vote)
        .filter(Vote.user_id == user_id, Vote.content_type == content_type)
        .all()
    )
    return {vote.content_id: vote.vote for vote in votes}


def _build_insight_prompt(investor_type: str | None, prices: dict, news: list[dict]) -> str:
    asset_lines = []
    for symbol, values in prices.items():
        price = values.get("price_usd")
        if price is None:
            continue
        change = values.get("change_24h")
        if change is not None:
            asset_lines.append(f"- {symbol}: ${price} ({change:+.2f}% 24h)")
        else:
            asset_lines.append(f"- {symbol}: ${price}")

    news_lines = [f"- {item['title']}" for item in news[:5] if item.get("title")]

    prompt = (
        f"You are a crypto market assistant. The user is a {investor_type or 'BEGINNER'} "
        "investor. Write a friendly 2-3 sentence 'Insight of the Day' summarizing the "
        "market data below for this user. Do not give financial advice.\n\n"
    )
    if asset_lines:
        prompt += "Prices:\n" + "\n".join(asset_lines) + "\n\n"
    if news_lines:
        prompt += "Recent headlines:\n" + "\n".join(news_lines) + "\n\n"

    return prompt


@router.get("", response_model=DashboardOut)
def get_dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    preference = (
        db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    )
    content_types = {
        c.content_type
        for c in db.query(UserContentPreference)
        .filter(UserContentPreference.user_id == current_user.id)
        .all()
    }
    asset_symbols = [
        a.asset_symbol
        for a in db.query(UserAsset).filter(UserAsset.user_id == current_user.id).all()
    ]

    prices = coingecko.get_prices(asset_symbols)
    news = crypto_news.get_news(asset_symbols) if "NEWS" in content_types else []

    today = date.today()
    insight = (
        db.query(AIInsight)
        .filter(AIInsight.user_id == current_user.id, AIInsight.generated_date == today)
        .first()
    )
    if insight is None:
        investor_type = preference.investor_type if preference else None
        prompt = _build_insight_prompt(investor_type, prices, news)
        content = openrouter.generate_insight(prompt)
        insight = AIInsight(user_id=current_user.id, content=content, generated_date=today)
        db.add(insight)
        db.commit()
        db.refresh(insight)

    memes = _load_memes()
    meme = memes[date.today().toordinal() % len(memes)]

    news_votes = _get_votes_map(db, current_user.id, "NEWS")
    insight_votes = _get_votes_map(db, current_user.id, "AI_INSIGHT")
    meme_votes = _get_votes_map(db, current_user.id, "MEME")

    price_items = []
    for symbol in asset_symbols:
        values = prices.get(symbol, {})
        price_items.append(
            PriceItemOut(
                symbol=symbol,
                price_usd=values.get("price_usd"),
                change_24h=values.get("change_24h"),
            )
        )

    news_items = [NewsItemOut(**item, vote=news_votes.get(item["id"])) for item in news]

    insight_content_id = f"AI_INSIGHT:{insight.generated_date.isoformat()}"
    ai_insight = AIInsightOut(
        content_id=insight_content_id,
        content=insight.content,
        generated_date=insight.generated_date,
        vote=insight_votes.get(insight_content_id),
    )

    meme_content_id = f"MEME:{meme['id']}"
    meme_out = MemeOut(
        id=meme["id"],
        content_id=meme_content_id,
        url=meme["url"],
        caption=meme.get("caption"),
        vote=meme_votes.get(meme_content_id),
    )

    return DashboardOut(
        prices=price_items, news=news_items, ai_insight=ai_insight, meme=meme_out
    )
