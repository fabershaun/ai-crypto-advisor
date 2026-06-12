# AI Crypto Advisor

A full-stack crypto dashboard that gives each user a personalized daily view of the
market: live prices for the coins they care about, recent crypto news, an AI-generated
"Insight of the Day", and a meme to lighten the mood. Users can upvote/downvote any piece
of content, and tune their experience (investor type, content types, tracked assets) from
an onboarding wizard or a preferences page.

Built as a portfolio project to demonstrate a complete, production-shaped full-stack
slice: authentication, a normalized relational schema with migrations, external API
integration, server-side caching of AI-generated content, and a tested REST API.

## Features

- **JWT authentication** — signup, login, and a protected `/auth/me` endpoint
- **Onboarding wizard** — captures investor type, preferred content types (News, Charts,
  Social, Fun), and tracked crypto assets
- **Preferences page** — edit those choices at any time after onboarding
- **Personalized dashboard**
  - Live prices + 24h change for the user's tracked assets ([CoinGecko](https://www.coingecko.com/en/api))
  - Recent crypto headlines (CoinDesk RSS feed)
  - "Insight of the Day" — an AI-generated summary of the user's market data,
    generated once per day per user and cached in the database
  - A daily crypto meme
- **Voting** — upvote/downvote news items, the AI insight, or the meme; votes persist
  and are restored on future loads
- **Automated tests** — pytest suite covering auth, preferences, dashboard, and votes

## Tech stack

| Layer    | Technology |
|----------|------------|
| Frontend | React (Vite), React Router, Axios |
| Backend  | FastAPI, SQLAlchemy, Alembic, Pydantic Settings |
| Database | PostgreSQL |
| Auth     | JWT (`python-jose`), password hashing via `passlib`/`bcrypt` |
| External APIs | [CoinGecko](https://www.coingecko.com/en/api) (prices), CoinDesk RSS (news), [OpenRouter](https://openrouter.ai/) (AI insight) |
| Testing  | pytest |

## Architecture

```mermaid
erDiagram
    users ||--o| user_preferences : has
    users ||--o{ user_content_preferences : has
    users ||--o{ user_assets : tracks
    users ||--o{ votes : casts
    users ||--o{ ai_insights : "generated for"

    users {
        int id
        string name
        string email
        string password_hash
    }
    user_preferences {
        int user_id
        string investor_type
    }
    user_content_preferences {
        int user_id
        string content_type
    }
    user_assets {
        int user_id
        string asset_symbol
    }
    votes {
        int user_id
        string content_type
        string content_id
        string vote
    }
    ai_insights {
        int user_id
        text content
        date generated_date
    }
```

`votes.content_id` and `ai_insights` reference content that doesn't have its own table
row (a news article, a meme, or "today's" AI insight) via an external string id, e.g.
`AI_INSIGHT:2026-06-12` or `MEME:meme-3`.

### Dashboard request flow

1. Load the user's preferences, content types, and tracked assets
2. Fetch live prices for those assets (CoinGecko)
3. If "News" is a selected content type, fetch recent headlines (CoinDesk RSS)
4. Check `ai_insights` for an entry for today
   - if missing, build a prompt from the user's preferences/prices/news, call
     OpenRouter, and cache the result
5. Pick a meme of the day
6. Attach the user's existing votes to news items, the insight, and the meme
7. Return everything as a single aggregated response

## Project structure

```
backend/
  app/
    api/          # FastAPI routers: auth, preferences, dashboard, votes
    models/       # SQLAlchemy models
    schemas/      # Pydantic request/response schemas
    services/     # External API clients (CoinGecko, CoinDesk news, OpenRouter)
    core/         # Config, database session, security/JWT helpers
  alembic/        # Database migrations
  tests/          # pytest suite
frontend/
  src/
    pages/        # Home, Login, Signup, Onboarding, Dashboard, Preferences
    components/   # Navbar, ProtectedRoute, VoteButtons
    context/      # AuthContext (session, preferences)
    services/     # Axios API client
```

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally (or a connection string to one)

### Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # then fill in values, see below
alembic upgrade head
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` (interactive docs at `/docs`).

#### Backend environment variables (`backend/.env`)

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | yes | e.g. `postgresql://user:password@localhost:5432/crypto_advisor` |
| `JWT_SECRET` | yes | secret used to sign access tokens |
| `COINGECKO_API_KEY` | no | optional CoinGecko demo API key for higher rate limits |
| `OPENROUTER_API_KEY` | no | if unset, the AI insight falls back to a static message |
| `FRONTEND_URL` | yes | used for CORS, e.g. `http://localhost:5173` |

### Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000
npm run dev
```

The app will be available at `http://localhost:5173`.

#### Frontend environment variables (`frontend/.env`)

| Variable | Required | Notes |
|----------|----------|-------|
| `VITE_API_BASE_URL` | yes | base URL of the backend API, e.g. `http://localhost:8000` |

## Running tests

```bash
cd backend
pytest
```

## API overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/signup` | no | Create an account |
| POST | `/auth/login` | no | Log in, returns a JWT access token |
| GET | `/auth/me` | yes | Get the current user |
| GET | `/preferences` | yes | Get investor type, content types, and tracked assets |
| POST | `/preferences` | yes | Upsert investor type, content types, and tracked assets |
| GET | `/dashboard` | yes | Aggregated dashboard: prices, news, AI insight, meme, votes |
| POST | `/votes` | yes | Upsert a vote (`UP`/`DOWN`) on a piece of content |

## Deployment

The backend is set up to deploy to [Render](https://render.com) and the frontend to
[Vercel](https://vercel.com).

### Backend (Render)

`render.yaml` at the repo root defines a Render "Blueprint": a free PostgreSQL database
and a web service for the FastAPI app (`rootDir: backend`). Render runs
`pip install -r requirements.txt && alembic upgrade head` on each deploy, then starts
`uvicorn`. `DATABASE_URL` and `JWT_SECRET` are provisioned automatically; set these in
the Render dashboard after creating the service from the blueprint:

- `COINGECKO_API_KEY` (optional)
- `OPENROUTER_API_KEY` (optional, falls back to a static insight if unset)
- `FRONTEND_URL` — your deployed Vercel URL, for CORS

### Frontend (Vercel)

Import the repo into Vercel with **Root Directory** set to `frontend`. Vercel
auto-detects the Vite build (`npm run build`, output `dist`); `frontend/vercel.json`
adds a rewrite so client-side routes (e.g. `/dashboard`) work on refresh. Set this
environment variable in the Vercel project settings:

- `VITE_API_BASE_URL` — your deployed Render API URL

## AI usage

This project was built collaboratively with an AI coding assistant. See
[AI_USAGE.md](AI_USAGE.md) for details on how it was used.
