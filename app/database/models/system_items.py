import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.models.base import Base


class SystemItemType(str, enum.Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class SystemItem(Base):
    __tablename__ = "system_items"
    __table_args__ = {"comment": "Элементы файловой системы"}

    id = Column(
        String,
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        doc="Уникальный идентификатор объекта",
        comment="Уникальный идентификатор объекта",
    )
    url = Column(
        String(250),
        nullable=True,
        doc="Ссылка на файл",
        comment="Ссылка на файл",
    )
    parent_id = Column(
        String,
        ForeignKey("system_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="id родительской папки",
        comment="id родительской папки",
    )
    children = relationship("SystemItem", back_populates="parent")
    parent = relationship(
        "SystemItem", back_populates="children", remote_side=id, cascade="all,delete-orphan", single_parent=True
    )
    type = Column(
        Enum(SystemItemType, name="system_item_type"),
        nullable=False,
        doc="Тип элемента",
        comment="Тип элемента",
    )
    size = Column(
        Integer,
        nullable=True,
        doc="Размер файла",
        comment="Размер файла",
    )
    date_created = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Дата создания",
        comment="Дата создания",
    )
    date_updated = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc).astimezone,
        doc="Дата редактирования",
        comment="Дата редактирования",
    )
