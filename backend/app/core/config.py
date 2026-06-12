from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    coingecko_api_key: str = ""
    cryptopanic_api_key: str = ""
    openrouter_api_key: str = ""
    frontend_url: str = "http://localhost:5173"


settings = Settings()
