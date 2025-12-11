from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Defines application settings. Loads values from environment variables
    or an .env file (which should be gitignored).
    """

    @property
    def DATABASE_URL(self) -> str:
        # Pydantic will construct the final URL using the variables
        # loaded from the .env file or the defaults defined.
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str = "SECRET_KEY"

    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="devpassword")
    POSTGRES_DB: str = Field(default="POT_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
