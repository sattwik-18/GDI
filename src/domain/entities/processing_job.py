"""ProcessingJob domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class ProcessingJob:
    """Document processing job domain entity."""

    id: uuid.UUID
    document_id: uuid.UUID
    status: str  # INGESTED, PROCESSING, COMPLETED, FAILED
    error_details: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    @classmethod
    def create(cls, document_id: uuid.UUID) -> "ProcessingJob":
        return cls(
            id=uuid.uuid4(),
            document_id=document_id,
            status="INGESTED",
        )

    def mark_completed(self) -> None:
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self, error_details: dict[str, Any]) -> None:
        self.status = "FAILED"
        self.error_details = error_details
        self.completed_at = datetime.now(timezone.utc)
