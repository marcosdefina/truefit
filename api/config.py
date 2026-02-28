from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "TrueFit"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8101"]

    # Zara scraper
    zara_base_url: str = "https://www.zara.com"
    zara_region: str = "cz"  # Czech Republic
    zara_language: str = "en"

    # Cache TTL (seconds) — 6 hours
    cache_ttl: int = 21600

    # Outfit generation
    max_outfit_candidates: int = 200
    top_n_outfits: int = 3

    class Config:
        env_prefix = "TRUEFIT_"


settings = Settings()
