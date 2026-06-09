from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    groq_api_key: str
    apify_api_token: str
    apify_actor_id: str = "apify/instagram-scraper"
    youtube_api_key: str
    chroma_persist_dir: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    groq_llm_model: str = "llama-3.3-70b-versatile"
    frontend_origin: str = "http://localhost:5173"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()