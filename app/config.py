from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-realtime"

    VOICE: str = "marin"
    TEMPERATURE: float = 0.8

    TAVILY_API_KEY: str = ""

    QDRANT_URL: str = "http://localhost:6333"
    COLLECTION_NAME: str = "documents"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
