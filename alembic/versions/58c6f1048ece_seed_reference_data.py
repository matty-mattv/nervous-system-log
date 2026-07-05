"""seed reference data

Revision ID: 58c6f1048ece
Revises: 3640eea27128
Create Date: 2026-07-03 15:41:02.903510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58c6f1048ece'
down_revision: Union[str, Sequence[str], None] = '3640eea27128'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Lightweight table references for bulk_insert - these describe just
# enough of the table shape to insert rows. We don't need the full
# ORM model here; Alembic migrations intentionally stay decoupled from
# api/models.py so that old migrations still run correctly even if the
# models change later (a migration is a snapshot in time, not a live
# reference to current code - same principle as a Flyway script never
# changing after it's been applied).
entry_types_table = sa.table(
    "entry_types", sa.column("code", sa.String), sa.column("label", sa.String)
)
origins_table = sa.table(
    "origins", sa.column("code", sa.String), sa.column("label", sa.String)
)
sensation_locations_table = sa.table(
    "sensation_locations", sa.column("code", sa.String), sa.column("label", sa.String)
)
intensities_table = sa.table(
    "intensities", sa.column("code", sa.String), sa.column("label", sa.String)
)
trigger_categories_table = sa.table(
    "trigger_categories", sa.column("code", sa.String), sa.column("label", sa.String)
)
resolutions_table = sa.table(
    "resolutions", sa.column("code", sa.String), sa.column("label", sa.String)
)


def upgrade() -> None:
    """Seed all reference/lookup tables with Matt's taxonomy."""

    op.bulk_insert(
        entry_types_table,
        [
            {"code": "activation", "label": "Activation"},
            {"code": "completion", "label": "Completion"},
            {"code": "reparenting", "label": "Reparenting (Minh Thuc)"},
            {"code": "reflection", "label": "Reflection"},
        ],
    )

    op.bulk_insert(
        origins_table,
        [
            {"code": "thought", "label": "Thought"},
            {"code": "sensation", "label": "Sensation"},
            {"code": "both", "label": "Both"},
            {"code": "unclear", "label": "Unclear"},
        ],
    )

    op.bulk_insert(
        sensation_locations_table,
        [
            {"code": "chest", "label": "Chest"},
            {"code": "throat_neck_back", "label": "Throat / Neck / Back"},
            {"code": "stomach", "label": "Stomach"},
            {"code": "other", "label": "Other"},
        ],
    )

    op.bulk_insert(
        intensities_table,
        [
            {"code": "wave", "label": "Wave"},
            {"code": "storm", "label": "Storm"},
        ],
    )

    op.bulk_insert(
        trigger_categories_table,
        [
            {"code": "social_uncertainty", "label": "Social Uncertainty"},
            {"code": "attachment_relevant", "label": "Attachment-Relevant"},
            {"code": "work", "label": "Work"},
            {"code": "unprompted_memory", "label": "Unprompted Memory"},
            {"code": "other", "label": "Other"},
        ],
    )

    op.bulk_insert(
        resolutions_table,
        [
            {"code": "discharged", "label": "Discharged"},
            {"code": "interrupted", "label": "Interrupted"},
            {"code": "ongoing", "label": "Ongoing"},
        ],
    )


def downgrade() -> None:
    """Remove seeded reference data."""
    op.execute("DELETE FROM entry_types")
    op.execute("DELETE FROM origins")
    op.execute("DELETE FROM sensation_locations")
    op.execute("DELETE FROM intensities")
    op.execute("DELETE FROM trigger_categories")
    op.execute("DELETE FROM resolutions")