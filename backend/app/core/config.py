import os
import secrets
import warnings
from typing import Annotated, Any, Literal

try:
    from pydantic import (
        AnyUrl,
        BeforeValidator,
        EmailStr,
        HttpUrl,
        PostgresDsn,
        computed_field,
        model_validator,
    )
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from typing_extensions import Self
except ModuleNotFoundError:  # pragma: no cover - minimal local MVP runtime
    BaseSettings = None


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    if isinstance(v, list | str):
        return v
    raise ValueError(v)


if BaseSettings is None:

    class Settings:
        API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
        SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 8))
        )
        FRONTEND_HOST = os.getenv("FRONTEND_HOST", "http://localhost:3000")
        ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
        PROJECT_NAME = os.getenv("PROJECT_NAME", "AI Learning Backend")
        SENTRY_DSN = os.getenv("SENTRY_DSN") or None
        POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")
        POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
        POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "")
        FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER", "admin@example.com")
        FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "")

        @property
        def BACKEND_CORS_ORIGINS(self) -> list[str]:
            return parse_cors(os.getenv("BACKEND_CORS_ORIGINS", "")) or []

        @property
        def all_cors_origins(self) -> list[str]:
            origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
            return origins + [self.FRONTEND_HOST]

        @property
        def SQLALCHEMY_DATABASE_URI(self) -> str:
            return (
                "postgresql+psycopg://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        @property
        def emails_enabled(self) -> bool:
            return False

else:

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file="../.env",
            env_ignore_empty=True,
            extra="ignore",
        )
        API_V1_STR: str = "/api/v1"
        SECRET_KEY: str = secrets.token_urlsafe(32)
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
        FRONTEND_HOST: str = "http://localhost:3000"
        ENVIRONMENT: Literal["local", "staging", "production"] = "local"

        BACKEND_CORS_ORIGINS: Annotated[
            list[AnyUrl] | str, BeforeValidator(parse_cors)
        ] = []

        @computed_field  # type: ignore[prop-decorator]
        @property
        def all_cors_origins(self) -> list[str]:
            return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
                self.FRONTEND_HOST
            ]

        PROJECT_NAME: str = "AI Learning Backend"
        SENTRY_DSN: HttpUrl | None = None
        POSTGRES_SERVER: str = "db"
        POSTGRES_PORT: int = 5432
        POSTGRES_USER: str = "postgres"
        POSTGRES_PASSWORD: str = ""
        POSTGRES_DB: str = ""

        @computed_field  # type: ignore[prop-decorator]
        @property
        def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
            return PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )

        SMTP_TLS: bool = True
        SMTP_SSL: bool = False
        SMTP_PORT: int = 587
        SMTP_HOST: str | None = None
        SMTP_USER: str | None = None
        SMTP_PASSWORD: str | None = None
        EMAILS_FROM_EMAIL: EmailStr | None = None
        EMAILS_FROM_NAME: str | None = None

        @model_validator(mode="after")
        def _set_default_emails_from(self) -> Self:
            if not self.EMAILS_FROM_NAME:
                self.EMAILS_FROM_NAME = self.PROJECT_NAME
            return self

        EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

        @computed_field  # type: ignore[prop-decorator]
        @property
        def emails_enabled(self) -> bool:
            return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

        EMAIL_TEST_USER: EmailStr = "test@example.com"
        FIRST_SUPERUSER: EmailStr = "admin@example.com"
        FIRST_SUPERUSER_PASSWORD: str = ""

        def _check_default_secret(self, var_name: str, value: str | None) -> None:
            if value == "changethis":
                message = (
                    f'The value of {var_name} is "changethis", '
                    "for security, please change it, at least for deployments."
                )
                if self.ENVIRONMENT == "local":
                    warnings.warn(message, stacklevel=1)
                else:
                    raise ValueError(message)

        @model_validator(mode="after")
        def _enforce_non_default_secrets(self) -> Self:
            self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
            self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
            self._check_default_secret(
                "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
            )
            return self


settings = Settings()  # type: ignore
