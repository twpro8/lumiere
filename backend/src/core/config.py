from typing import Literal

from pydantic import computed_field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "FastAPI"
    APP_ENV: Literal["development", "testing", "production"] = "testing"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASS: str
    POSTGRES_DB: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 2
    REDIS_RETRY_ON_TIMEOUT: bool = True

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_SECONDS: int = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    @computed_field  # type: ignore
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASS,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def secure_cookies(self) -> bool:
        """Enable secure only on production (HTTPS)"""
        return self.APP_ENV == "production"


settings = Settings()  # type: ignore
