from typing import Any, Optional, Union

from pydantic import AmqpDsn, PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings

    Values are pulled from local .env file"""

    # Get config values from `.env` file
    model_config = SettingsConfigDict(env_file=".env")

    PROJECT_NAME: Optional[str] = "FastAPI File MD5 Hash Demo"

    POSTGRES_HOST: str
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: str
    POSTGRES_PSWD: str
    POSTGRES_DB: str
    POSTGRES_DB_URL: Union[Optional[PostgresDsn], Optional[str]] = None
    POSTGRES_DB_URL_ASYNC: Union[Optional[PostgresDsn], Optional[str]] = None

    @field_validator("POSTGRES_DB_URL", mode="before")
    @classmethod
    def db_conn(cls, v: Optional[PostgresDsn], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PSWD"),
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB"),
        ).unicode_string()

    @field_validator("POSTGRES_DB_URL_ASYNC", mode="before")
    @classmethod
    def db_conn_async(cls, v: Optional[PostgresDsn], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PSWD"),
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB"),
        ).unicode_string()

    CELERY_APP: Optional[str] = None
    CELERY_BROKER_USER: str
    CELERY_BROKER_PSWD: str
    CELERY_BROKER_HOST: str
    CELERY_BROKER_PORT: int
    CELERY_BROKER_URL: Union[Optional[AmqpDsn], Optional[str]] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def celery_broker_conn(cls, v: Optional[AmqpDsn], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return AmqpDsn.build(
            scheme="amqp",
            username=info.data.get("CELERY_BROKER_USER"),
            password=info.data.get("CELERY_BROKER_PSWD"),
            host=info.data.get("CELERY_BROKER_HOST"),
            port=info.data.get("CELERY_BROKER_PORT"),
        ).unicode_string()

    CELERY_BACKEND_URL: Union[Optional[PostgresDsn], Optional[str]] = None

    @field_validator("CELERY_BACKEND_URL", mode="before")
    @classmethod
    def celery_backend_conn(
        cls, v: Optional[PostgresDsn], info: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v

        postgres_url = PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PSWD"),
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB"),
        )

        return f"db+{postgres_url}"

    CELERY_QUEUE: Optional[str] = "hash-queue"
    CELERY_DB_VERBOSE: Optional[bool] = False
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: Optional[bool] = True

    INPUT_FILE_DIR: Optional[str] = "./files"
    LOG_FILE: Optional[str] = "./logs/app.log"


settings = Settings()
