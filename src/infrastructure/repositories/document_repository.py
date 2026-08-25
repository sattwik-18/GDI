"""SQLAlchemy implementation of DocumentRepository."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.document import Document
from src.domain.interfaces.repositories import DocumentRepository
from src.domain.value_objects.document_hash import DocumentHash
from src.infrastructure.database.models import DocumentModel


class SQLAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy async implementation for Document repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, document: Document) -> None:
        model = DocumentModel(
            id=document.id,
            sha256=document.hashes.sha256,
            sha3_256=document.hashes.sha3_256,
            mime_type=document.mime_type,
            size_bytes=document.size_bytes,
            file_path=document.file_path,
            original_filename=document.original_filename,
            page_count=document.page_count,
            created_at=document.created_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Document(
            id=model.id,
            hashes=DocumentHash(sha256=model.sha256, sha3_256=model.sha3_256),
            mime_type=model.mime_type,
            size_bytes=model.size_bytes,
            file_path=model.file_path,
            original_filename=model.original_filename,
            page_count=model.page_count,
            created_at=model.created_at,
        )

    async def get_by_hash(self, sha256_hash: str) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.sha256 == sha256_hash)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Document(
            id=model.id,
            hashes=DocumentHash(sha256=model.sha256, sha3_256=model.sha3_256),
            mime_type=model.mime_type,
            size_bytes=model.size_bytes,
            file_path=model.file_path,
            original_filename=model.original_filename,
            page_count=model.page_count,
            created_at=model.created_at,
        )
