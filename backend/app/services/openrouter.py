import httpx

from app.core.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b:free"

FALLBACK_INSIGHT = (
    "We're unable to generate a personalized insight right now. "
    "Check back later for an AI-powered summary of your portfolio."
)


def generate_insight(prompt: str) -> str:
    if not settings.openrouter_api_key:
        return FALLBACK_INSIGHT

    try:
        response = httpx.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={
                "model": DEFAULT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError):
        return FALLBACK_INSIGHT
