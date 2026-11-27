from pydantic import Field, field_validator
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

    SECRET_KEY: str = Field(repr=False)

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if value != value.strip() or len(value.encode("utf-8")) < 32:
            raise ValueError("SECRET_KEY must be at least 32 bytes with no leading or trailing whitespace")
        if len(set(value)) == 1 or value == "your-secure-secret-key-here-replace-this":
            raise ValueError("SECRET_KEY must not be a known weak value")
        return value

    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="devpassword")
    POSTGRES_DB: str = Field(default="POT_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, le=30)
    smtp_from_email: str = "test@example.com"
    brevo_api_key: str = ""
    TESTING: bool = False
    REDIS_URL: str = Field(default="")

    email_verification_expiry_minutes: int = 10
    password_reset_expiry_minutes: int = 10
    frontend_base_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )


settings = Settings()
