from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    DATABASE_URL: str = Field(..., description="Database connection string")
    DISCORD_TOKEN: str = Field(..., description="Discord bot token")
    DISCORD_CHANNEL_ID: str = Field(..., description="Discord channel ID")
    INTERVALS_API_KEY: str = Field(..., description="Intervals API key")
    INTERVALS_ATHLETE_ID: str = Field(..., description="Intervals athlete ID")
    INTERVALS_BASE_URL: str = Field(..., description="Intervals base URL")
    GOOGLE_GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    GOOGLE_GEMINI_MODEL: str = Field(default="gemini-3.8-flash", min_length=1)
    ENVIRONMENT: str = Field(..., description="Application environment")
    LOG_LEVEL: str = Field(..., description="Logging level")


settings = Settings()