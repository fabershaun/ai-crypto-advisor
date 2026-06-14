from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    coingecko_api_key: str = ""
    openrouter_api_key: str = ""
    frontend_url: str = "http://localhost:5173"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Some hosts (e.g. Render) expose a "postgres://" URL, but SQLAlchemy 2.x
        # only recognizes the "postgresql://" scheme.
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value


settings = Settings()
