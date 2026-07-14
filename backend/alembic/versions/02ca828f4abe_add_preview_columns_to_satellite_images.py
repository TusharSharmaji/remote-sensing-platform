"""add_preview_columns_to_satellite_images

Revision ID: 02ca828f4abe
Revises: b2c3d4e5f6a7
Create Date: 2026-07-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "02ca828f4abe"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "satellite_images",
        sa.Column("preview_path", sa.String(length=512), nullable=True),
    )

    op.add_column(
        "satellite_images",
        sa.Column("thumbnail_path", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("satellite_images", "thumbnail_path")
    op.drop_column("satellite_images", "preview_path")