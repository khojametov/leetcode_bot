"""Initial migration

Revision ID: ff8ce74a22f6
Revises:
Create Date: 2022-11-29 18:41:22.335150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ff8ce74a22f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("invite_link", sa.String(), nullable=False),
        sa.Column("expire_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
        sa.UniqueConstraint("invite_link"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("telegram_username", sa.String(), nullable=False),
        sa.Column("leetcode_profile", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
        sa.UniqueConstraint("leetcode_profile"),
        sa.UniqueConstraint("telegram_username"),
    )
    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("hard", sa.Integer(), nullable=True),
        sa.Column("medium", sa.Integer(), nullable=True),
        sa.Column("easy", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("statistics")
    op.drop_table("users")
    op.drop_table("links")
    # ### end Alembic commands ###
