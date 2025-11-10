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
