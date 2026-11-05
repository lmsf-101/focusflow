"""rename pomodoro preference to preset

Revision ID: f10feb828058
Revises: ad83c4c77ebe
Create Date: 2026-11-05 11:21:07.141833

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f10feb828058"
down_revision: str | Sequence[str] | None = "ad83c4c77ebe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("pomodoro_preference", "pomodoro_preset")

    op.add_column(
        table_name="pomodoro_preset",
        column=sa.Column("name", sa.String(length=75), nullable=False),
    )

    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preference_single_scope
        TO ck_pomodoro_preset_single_scope
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preference_classic_parameters
        TO ck_pomodoro_preset_classic_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preference_incremental_parameters
        TO ck_pomodoro_preset_incremental_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preference_flexible_parameters
        TO ck_pomodoro_preset_flexible_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT pomodoro_preference_owner_id_fkey
        TO pomodoro_preset_owner_id_fkey
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT pomodoro_preference_pkey
        TO pomodoro_preset_pkey
    """
    )

    op.create_unique_constraint(
        constraint_name="uq_pomodoro_preset_owner_id_name",
        table_name="pomodoro_preset",
        columns=["owner_id", "name"],
    )

    op.drop_constraint(
        constraint_name="pomodoro_preference_category_id_fkey",
        table_name="pomodoro_preset",
        type_="foreignkey",
    )

    op.drop_constraint(
        constraint_name="pomodoro_preference_project_id_fkey",
        table_name="pomodoro_preset",
        type_="foreignkey",
    )

    op.create_foreign_key(
        constraint_name="pomodoro_preset_project_id_fkey",
        source_table="pomodoro_preset",
        referent_table="project",
        local_cols=["project_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        constraint_name="pomodoro_preset_category_id_fkey",
        source_table="pomodoro_preset",
        referent_table="category",
        local_cols=["category_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        constraint_name="pomodoro_preset_project_id_fkey",
        table_name="pomodoro_preset",
        type_="foreignkey",
    )
    op.drop_constraint(
        constraint_name="pomodoro_preset_category_id_fkey",
        table_name="pomodoro_preset",
        type_="foreignkey",
    )

    op.create_foreign_key(
        constraint_name="pomodoro_preference_project_id_fkey",
        source_table="pomodoro_preset",
        referent_table="project",
        local_cols=["project_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        constraint_name="pomodoro_preference_category_id_fkey",
        source_table="pomodoro_preset",
        referent_table="category",
        local_cols=["category_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        constraint_name="uq_pomodoro_preset_owner_id_name",
        table_name="pomodoro_preset",
        type_="unique",
    )

    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preset_single_scope
        TO ck_pomodoro_preference_single_scope
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preset_classic_parameters
        TO ck_pomodoro_preference_classic_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preset_incremental_parameters
        TO ck_pomodoro_preference_incremental_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT ck_pomodoro_preset_flexible_parameters
        TO ck_pomodoro_preference_flexible_parameters
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT pomodoro_preset_owner_id_fkey
        TO pomodoro_preference_owner_id_fkey
    """
    )
    op.execute(
        """
        ALTER TABLE pomodoro_preset
        RENAME CONSTRAINT pomodoro_preset_pkey
        TO pomodoro_preference_pkey
    """
    )

    op.drop_column(table_name="pomodoro_preset", column_name="name")

    op.rename_table(
        old_table_name="pomodoro_preset", new_table_name="pomodoro_preference"
    )
