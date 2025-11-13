import os

# Try to import pydantic_settings for convenient environment-backed settings.
# If it's not installed in the environment (common in lightweight dev setups),
# fall back to a minimal settings object using environment variables.
try:
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        # Use Postgres by default for development. Override via .env.
        DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smartroom"

        # AI Agent API Keys (set in .env or environment)
        OPENAI_API_KEY: str | None = None
        ANTHROPIC_API_KEY: str | None = None
        GOOGLE_API_KEY: str | None = None

        IOT_MQTT_BROKER: str = "mqtt://localhost:1883"

        class Config:
            env_file = ".env"

    settings = Settings()
except Exception:
    # Minimal fallback settings object using environment variables
    class _FallbackSettings:
        DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smartroom")
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
        IOT_MQTT_BROKER = os.environ.get("IOT_MQTT_BROKER", "mqtt://localhost:1883")

    settings = _FallbackSettings()
