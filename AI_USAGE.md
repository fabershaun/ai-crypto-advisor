# AI Usage

This project was built in collaboration with **Claude Code**, an AI coding assistant,
used as an active pair-programmer rather than a one-off code generator. This document
describes how it was used and where human judgment drove the work.

## Planning

The project started from a rough architecture proposal (tech stack, schema, API
surface, and a 35-commit roadmap split into 8 phases). Before any code was written, the
proposal was reviewed and refined together, resolving several open design questions:

- Multi-select content preferences (News/Charts/Social/Fun) became their own junction
  table (`user_content_preferences`), mirroring `user_assets`.
- Votes on content without a database row (news articles, AI insights, memes) reference
  that content via an external string id (e.g. `AI_INSIGHT:2026-06-12`) rather than a
  foreign key.
- The AI-generated "Insight of the Day" is generated once per user per day and cached in
  an `ai_insights` table, instead of calling the LLM on every dashboard load.
- A pytest suite covering auth, preferences, dashboard, and votes was scoped in from the
  start.

## Implementation

Each phase of the roadmap (scaffolding, auth, onboarding, external services + dashboard,
voting, polish, docs) was implemented incrementally:

- Backend: FastAPI routers, SQLAlchemy models, Alembic migrations, Pydantic schemas, and
  the CoinGecko / news / OpenRouter service integrations were written by the assistant
  following the agreed schema and endpoint design.
- Frontend: React Router setup, auth context, onboarding wizard, dashboard UI, and the
  voting components were likewise written by the assistant, then reviewed and adjusted
  in the browser.
- Tests: pytest tests were written alongside each backend feature (auth flows,
  preference upserts, dashboard aggregation/caching, vote upserts).

## Debugging

The assistant was also used to diagnose real issues that came up during manual testing,
for example:

- The dashboard's "Prices" and "News" sections were always empty for a real user even
  though a direct API test returned correct data. Root-caused to `uvicorn --reload` on
  Windows silently failing to restart the worker process after file changes — every
  in-progress fix was running against stale code. Fixed by doing full server restarts
  instead of relying on `--reload`.
- CryptoPanic's free news API was discontinued mid-project. The news service was
  replaced with a free CoinDesk RSS feed, with tests updated accordingly.
- Several dashboard rendering bugs (empty-state sections disappearing entirely instead
  of showing a friendly message, price rows being dropped when a price lookup failed).

## Human role

- Reviewed and approved all architectural decisions, schema design, and the roadmap.
- Tested the app end-to-end in the browser after each significant change and reported
  bugs with screenshots/repro steps.
- Made product decisions (e.g., which replacement news source to use once CryptoPanic's
  free tier was discontinued).
- Provided API credentials (OpenRouter) and decided when to commit/push, including how
  to group changes into commits.
- Set up the GitHub repository and remote.
