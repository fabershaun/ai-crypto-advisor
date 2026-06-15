# AI Crypto Advisor — Project Overview

A personalized crypto dashboard that gets to know each user through a short onboarding
quiz, then shows daily, preference-tailored content — live prices, news, an AI "Insight
of the Day", a social-sentiment read, and a meme — each with thumbs up/down feedback.

## Links

- **Live app:** https://ai-crypto-advisor-frontend-pi.vercel.app
- **Demo login:** `demo@aicrypto.app` / `demopass123` (or sign up for a fresh account)
- **Repository:** https://github.com/fabershaun/ai-crypto-advisor
- **AI usage summary:** `AI_USAGE.md` in the repo · **Database access:** connection string supplied with the submission

> The backend runs on Render's free tier and spins down when idle, so the **first request
> after inactivity can take ~30–50 seconds** while it wakes up.

## What it does

After signing up (email + password, JWT auth), a first-time user completes a three-step
onboarding wizard: investor type, content interests (News / Charts / Social / Fun), and
tracked assets. These are saved as preferences and drive a personalized dashboard:

- **Prices** — live quotes + 24h change (CoinGecko)
- **News** — recent headlines (CoinDesk RSS, with a static fallback)
- **Social Sentiment** — Bullish / Bearish / Neutral per asset, derived from 24h momentum
- **Insight of the Day** — an LLM summary (OpenRouter), generated once per user per day and cached
- **Meme** — a rotating crypto meme

Each section appears only if the user selected its content type, and every section supports
up/down voting, persisted per user for future personalization.

## Tech stack

- **Frontend:** React (Vite), React Router, Axios — deployed on Vercel
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic — deployed on Render
- **Database:** PostgreSQL (Render)
- **Auth:** JWT (`python-jose`) with bcrypt password hashing
- **External APIs (all free tier):** CoinGecko, CoinDesk RSS, OpenRouter

## Architecture & notable decisions

- **Normalized schema with migrations** — six tables (users, preferences,
  content-preferences, assets, votes, ai_insights). Multi-select preferences are junction
  tables rather than delimited columns.
- **Votes reference external content** (a news article, meme, or "today's" insight) by a
  string id such as `AI_INSIGHT:2026-06-15`, so feedback works without a DB row per item.
- **The AI insight is cached once per day per user**, so the LLM is not called on every
  dashboard load.
- **One aggregated `/dashboard` endpoint** assembles prices, news, sentiment, insight,
  meme, and the user's existing votes in a single response.
- **Tested** — a 56-case pytest suite (auth, preferences, dashboard gating/caching, votes,
  external-service clients) plus a clean ESLint frontend.
- **Deployment** — a single Render blueprint (`render.yaml`) provisions the database, API,
  and static frontend; CORS is wired to the frontend origin.

## Running locally

See the repository `README.md` for backend (`uvicorn`) and frontend (`npm run dev`) setup;
the test suite runs with `pytest`.
