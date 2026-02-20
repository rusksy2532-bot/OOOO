from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Solana Memecoin Signals"
    api_prefix: str = "/api/v1"
    api_key: str = "change-me"
    database_url: str = "sqlite:///./app.db"
    holders_snapshot_max_age_minutes: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
