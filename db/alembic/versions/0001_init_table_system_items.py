"""Init table system_items

Revision ID: 95004f85a577
Revises: 
Create Date: 2024-03-17 14:12:17.612549

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "95004f85a577"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_items",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
            comment="Уникальный идентификатор объекта",
        ),
        sa.Column("url", sa.String(length=250), nullable=True, comment="Ссылка на файл"),
        sa.Column("parent_id", sa.String(), nullable=True, comment="id родительской папки"),
        sa.Column("type", sa.Enum("FILE", "FOLDER", name="system_item_type"), nullable=False, comment="Тип элемента"),
        sa.Column("size", sa.Integer(), nullable=True, comment="Размер файла"),
        sa.Column(
            "date_created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата создания",
        ),
        sa.Column(
            "date_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата редактирования",
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["system_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        comment="Элементы файловой системы",
    )
    op.create_index(op.f("ix_system_items_id"), "system_items", ["id"], unique=True)
    op.create_index(op.f("ix_system_items_parent_id"), "system_items", ["parent_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_items_parent_id"), table_name="system_items")
    op.drop_index(op.f("ix_system_items_id"), table_name="system_items")
    op.drop_table("system_items")
    op.execute("DROP TYPE IF EXISTS system_item_type")
