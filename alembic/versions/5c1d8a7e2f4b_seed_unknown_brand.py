"""seed the Unknown brand

Revision ID: 5c1d8a7e2f4b
Revises: 959033705b7d
Create Date: 2026-10-13 02:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c1d8a7e2f4b"
down_revision: Union[str, Sequence[str], None] = "959033705b7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create one active Unknown brand without changing converter records."""
    bind = op.get_bind()
    brands = sa.table(
        "brands",
        sa.column("id", sa.Integer),
        sa.column("external_id", sa.String(length=100)),
        sa.column("name", sa.String(length=100)),
        sa.column("logo_url", sa.String(length=500)),
        sa.column("is_active", sa.Boolean),
    )

    unknown = bind.execute(
        sa.select(brands.c.id)
        .where(brands.c.name == "Unknown")
        .limit(1)
    ).first()
    if unknown is not None:
        bind.execute(
            brands.update()
            .where(brands.c.id == unknown.id)
            .values(is_active=True)
        )
        return

    external_id = "malik-internal-unknown"
    suffix = 1
    while bind.execute(
        sa.select(brands.c.id)
        .where(brands.c.external_id == external_id)
        .limit(1)
    ).first() is not None:
        external_id = f"malik-internal-unknown-{suffix}"
        suffix += 1

    bind.execute(
        brands.insert().values(
            external_id=external_id,
            name="Unknown",
            logo_url=None,
            is_active=True,
        )
    )


def downgrade() -> None:
    """Keep the seed row because it may be referenced by converter records."""
