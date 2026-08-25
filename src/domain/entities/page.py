"""Page domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Page:
    """Document Page domain entity."""

    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    width_px: int
    height_px: int
    dpi: int
    orientation_deg: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        document_id: uuid.UUID,
        page_number: int,
        width_px: int,
        height_px: int,
        dpi: int,
        orientation_deg: int = 0,
    ) -> "Page":
        return cls(
            id=uuid.uuid4(),
            document_id=document_id,
            page_number=page_number,
            width_px=width_px,
            height_px=height_px,
            dpi=dpi,
            orientation_deg=orientation_deg,
        )
