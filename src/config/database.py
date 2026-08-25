"""Database configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    postgres_user: str = Field(default="gdi_user", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="gdi_password", validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="gdi_db", validation_alias="POSTGRES_DB")

    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    pool_timeout: float = Field(default=30.0, validation_alias="DB_POOL_TIMEOUT")
    database_optional: bool = Field(default=True, validation_alias="DATABASE_OPTIONAL")

    @property
    def async_connection_string(self) -> str:
        """Asynchronous PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_connection_string(self) -> str:
        """Synchronous connection URL for Alembic migrations."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        extra = "ignore"
