"""add PostgreSQL trigram indexes for converter search

Revision ID: d781e83c2a10
Revises: 5c1d8a7e2f4b
Create Date: 2026-10-18 17:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d781e83c2a10"
down_revision: Union[str, Sequence[str], None] = "5c1d8a7e2f4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create trigram indexes used by substring search."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    with op.get_context().autocommit_block():
        op.create_index(
            "ix_converters_code_reference_trgm",
            "converters",
            ["code_reference"],
            postgresql_using="gin",
            postgresql_ops={"code_reference": "gin_trgm_ops"},
            postgresql_where=sa.text("is_active IS TRUE"),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_converters_model_trgm",
            "converters",
            ["model"],
            postgresql_using="gin",
            postgresql_ops={"model": "gin_trgm_ops"},
            postgresql_where=sa.text("is_active IS TRUE"),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_converters_local_lingo_trgm",
            "converters",
            ["local_lingo"],
            postgresql_using="gin",
            postgresql_ops={"local_lingo": "gin_trgm_ops"},
            postgresql_where=sa.text("is_active IS TRUE"),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_converters_remarks_trgm",
            "converters",
            ["remarks"],
            postgresql_using="gin",
            postgresql_ops={"remarks": "gin_trgm_ops"},
            postgresql_where=sa.text("is_active IS TRUE"),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_brands_name_trgm",
            "brands",
            ["name"],
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    """Remove converter search indexes without dropping the shared extension."""
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_brands_name_trgm",
            table_name="brands",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_converters_remarks_trgm",
            table_name="converters",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_converters_local_lingo_trgm",
            table_name="converters",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_converters_model_trgm",
            table_name="converters",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_converters_code_reference_trgm",
            table_name="converters",
            postgresql_concurrently=True,
        )
