from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Defines application settings. Loads values from environment variables
    or an .env file (which should be gitignored).
    """

    DATABASE_URL: str = "postgresql+asyncpg://test:test@localhost/dev_db"

    SECRET_KEY: str = "SECRET_KEY"

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
