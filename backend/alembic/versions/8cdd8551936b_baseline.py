"""baseline

Revision ID: 8cdd8551936b
Revises:
Create Date: 2026-09-17 13:03:54.646434

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "8cdd8551936b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
