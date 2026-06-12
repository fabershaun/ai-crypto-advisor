from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, dashboard, preferences
from app.core.config import settings

app = FastAPI(title="AI Crypto Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(preferences.router)
app.include_router(dashboard.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
