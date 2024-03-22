from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    id: str
    url: Optional[str]
    parent_id: Optional[str] = Field(validation_alias="parentId")
    size: Optional[int]
    type: str


class SystemItemImportData(BaseModel):
    items: list[Item]
    update_date: str = Field(validation_alias="updateDate")


class ItemUpdates(BaseModel):
    id: str
    url: str
    date: datetime = Field(validation_alias="date_updated")
    parentId: Optional[str] = Field(validation_alias="parent_id")
    size: int
    type: str

    class Config:
        orm_mode = True


class ItemUpdatesOut(BaseModel):
    items: list[ItemUpdates]
