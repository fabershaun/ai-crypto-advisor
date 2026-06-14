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

## Review and hardening

After the initial build, the assistant did a full pass over the code against the spec and
surfaced gaps, then fixed them with tests:

- Only the "News" content preference actually drove a dashboard section. Every content
  type now gates its own section (Charts→Prices, News→News, Social→a derived sentiment
  section, Fun→Meme), and unselected sections are omitted.
- Voting was extended to every section (the Prices section had none).
- The news service gained a static fallback so the section is never empty.
- The meme was made dynamic per refresh (with a manual Refresh button) per the brief.
- The AI insight was shortened (tighter prompt + a `max_tokens` cap).
- Server-side input validation was added on signup (password length/strength, non-empty
  name), matching the frontend rules.

The pytest suite grew from ~32 to 56 tests over this work.

## Deployment

The app is deployed (frontend on Vercel, backend + PostgreSQL on Render via the
`render.yaml` blueprint). The assistant prepared the deploy config and walked through the
process, debugging real deployment-only issues:

- SQLAlchemy 2.x rejects Render's `postgres://` connection string; the config now
  normalizes it to `postgresql://`.
- CoinGecko's keyless free endpoint works from a laptop but rate-limits Render's
  datacenter IP, leaving prices empty in production — resolved with a free CoinGecko
  demo API key (already supported in code).
- Render appended a suffix to the backend's hostname, so the frontend and CORS origin had
  to be pointed at the actual URL; verified end-to-end (signup, preferences, dashboard,
  votes) against the live services.

## Human role

- Reviewed and approved all architectural decisions, schema design, and the roadmap.
- Tested the app end-to-end in the browser after each significant change and reported
  bugs with screenshots/repro steps.
- Made product decisions (e.g., the replacement news source, how to treat the "Social"
  preference, password-strength rules).
- Provided API credentials (OpenRouter, CoinGecko) and ran the account-level deployment
  steps on Render and Vercel.
- Decided when to commit/push and how to group changes; set up the GitHub repository.
