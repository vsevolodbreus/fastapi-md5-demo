"""Setup initial tables

Revision ID: a999a491d71c
Revises:
Create Date: 2023-12-08 01:07:39.957019

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a999a491d71c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "file_hash",
        sa.Column("req_id", sa.UUID(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("md5_hash", sa.String()),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime()),
        sa.PrimaryKeyConstraint("req_id"),
    )
    op.create_index(op.f("ix_file_hash_req_id"), "file_hash", ["req_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_file_hash_req_id"), table_name="file_hash")
    op.drop_table("file_hash")
