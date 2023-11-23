"""Initial migration

Revision ID: 7a5a2a9787af
Revises:
Create Date: 2023-10-28 01:20:51.800226

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "7a5a2a9787af"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("invite_link", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expire_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "telegram_username", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "leetcode_profile", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
        sa.UniqueConstraint("leetcode_profile"),
        sa.UniqueConstraint("telegram_username"),
    )
    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hard", sa.Integer(), nullable=False),
        sa.Column("medium", sa.Integer(), nullable=False),
        sa.Column("easy", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
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
