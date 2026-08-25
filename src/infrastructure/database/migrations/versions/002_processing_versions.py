"""Add processing_versions table for pipeline version tracking.

Revision ID: 002
Revises: 001
Create Date: 2026-07-22
"""

from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "processing_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("release_date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("description", sa.VARCHAR(255), nullable=False),
        sa.Column("is_compatible", sa.BOOLEAN, nullable=False, server_default="true"),
        sa.Column("migration_notes", sa.TEXT, nullable=True),
    )

    op.execute(
        """
        INSERT INTO processing_versions (id, version, release_date, description, is_compatible, migration_notes)
        VALUES (gen_random_uuid(), '1.0.0', NOW(), 'GDI Prototype 1 initial processing pipeline version', true, 'Initial version')
        """
    )


def downgrade() -> None:
    op.drop_table("processing_versions")
