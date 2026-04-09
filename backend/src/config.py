from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines application settings. Loads values from environment variables
    or an .env file (which should be gitignored).
    """

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        # Pydantic will construct the final URL using the variables
        # loaded from the .env file or the defaults defined.
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str = "SECRET_KEY"

    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="devpassword")
    POSTGRES_DB: str = Field(default="POT_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = "test"
    smtp_password: str = "test"
    smtp_from_email: str = "test@example.com"
    TESTING: bool = False
    REDIS_URL: str = Field(default="")

    email_verification_expiry_minutes: int = 10
    password_reset_expiry_minutes: int = 10
    frontend_base_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
