"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Better Auth Configuration
    better_auth_url: str = "http://localhost:3004"

    # Database
    database_url: str = ""

    # CORS - single URL or comma-separated URLs as string
    cors_origins: str = "http://localhost:3000"

    # AI Chatbot Configuration
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"

    def get_cors_origins_list(self) -> list[str]:
        """Parse cors_origins string into a list."""
        if not self.cors_origins:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
