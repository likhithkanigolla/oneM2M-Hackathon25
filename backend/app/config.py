from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./smartroom.db"

    # AI Agent API Keys (set in .env or environment)
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    IOT_MQTT_BROKER: str = "mqtt://localhost:1883"

    class Config:
        env_file = ".env"

settings = Settings()
