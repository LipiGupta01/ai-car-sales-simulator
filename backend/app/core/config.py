"""Purpose: Application settings model loaded from environment variables."""

from pydantic import Field, AliasChoices, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration for API, database, and AI provider."""

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url")
    )

    @model_validator(mode="after")
    def validate_and_set_database_url(self) -> 'Settings':
        if self.app_env == "production":
            if not self.database_url:
                raise ValueError("DATABASE_URL environment variable is required in production environment.")
            if "localhost" in self.database_url or "127.0.0.1" in self.database_url:
                raise ValueError("Localhost database URL is not allowed in production environment.")
        else:
            if not self.database_url:
                self.database_url = "postgresql+psycopg2://ai_car_user:ai_car_pass@localhost:5432/ai_car_sales"
        return self

    model_provider: str = "groq"
    model_name: str = "llama-3.3-70b-versatile"
    showroom_name: str = "Kia Frontier Motors"
    showroom_city: str = "New Delhi"
    showroom_state: str = "Delhi"
    showroom_country: str = "India"
    showroom_address: str = "Outer Ring Road, Rohini, New Delhi"
    showroom_location: str = "Kia Dealership Showroom"
    groq_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # Configure loading settings from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
