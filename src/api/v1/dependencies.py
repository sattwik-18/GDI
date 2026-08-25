"""FastAPI dependency providers."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.connection import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides an async SQLAlchemy database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
