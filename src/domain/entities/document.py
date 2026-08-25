"""Document domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from src.domain.value_objects.document_hash import DocumentHash


@dataclass
class Document:
    """Canonical Document domain entity."""

    id: uuid.UUID
    hashes: DocumentHash
    mime_type: str
    size_bytes: int
    file_path: str
    original_filename: str
    page_count: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        hashes: DocumentHash,
        mime_type: str,
        size_bytes: int,
        file_path: str,
        original_filename: str,
        page_count: int = 1,
    ) -> "Document":
        return cls(
            id=uuid.uuid4(),
            hashes=hashes,
            mime_type=mime_type,
            size_bytes=size_bytes,
            file_path=file_path,
            original_filename=original_filename,
            page_count=page_count,
        )
