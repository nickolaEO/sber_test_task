from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from app.database import SystemItem
from app.database.models.system_items import SystemItemType


async def check_system_item_exists(session, id: str):
    """
    Проверяет, существует ли элемент файловой системы по его идентификатору.
    Возвращает найденный элемент.
    Если элемент не найден, вызывает исключение HTTPException со статусом HTTP_404_NOT_FOUND.
    """
    query = select(SystemItem).filter(SystemItem.id == id)
    result = await session.scalars(query)
    system_item = result.first()
    if not system_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Элемента с id: '{id}' не существует.")
    return system_item


async def check_parent_exists(session, item_id: str, parent_id: str):
    """
    Проверяет, есть ли такой элемент в базе, который является строго FOLDER, чтобы записать валидный parent_id в базу.
    Если элемент не найден, вызывает исключение HTTPException со статусом HTTP_400_BAD_REQUEST.
    """
    query = select(SystemItem).filter(SystemItem.id == parent_id, SystemItem.type == SystemItemType.FOLDER.name)
    result = await session.execute(query)
    result = result.all()
    if not result:
        detail = f"id: '{item_id}'. parent_id '{parent_id}' указывает либо не на папку, либо такой папки не существует."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


def validate_item_type(item_id: str, item_type: str):
    """
    Проверяет поле type. Вызывает исключение HTTPException со статусом HTTP_400_BAD_REQUEST,
    если type отличен от тех типов SystemItemType, которые содержит элемент.
    """
    if item_type not in SystemItemType.__members__.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"id: '{item_id}'. Неправильно указан тип элемента.",
        )


def validate_item_size(item_id: str, size: int, item_type: str):
    """
    Проверяет поле size для типов элементов FOLDER и FILE.
    Вызывает исключение HTTPException со статусом HTTP_400_BAD_REQUEST,
    если в FILE size=None или отрицательное значение, а в FOLDER указано какое либо число.
    """
    if item_type == SystemItemType.FOLDER.name:
        if size is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"id: '{item_id}'. Поле size при импорте папки всегда должно быть равно null.",
            )
    elif item_type == SystemItemType.FILE.name:
        if size is None or size <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"id: '{item_id}'. Поле size при импорте файла должно быть не null и строго больше 0.",
            )


def validate_str_to_date_iso(date: str) -> datetime:
    """
    Проверяет строковую дату, что она по ISO 8601: '%Y-%m-%dT%H:%M:%S.%fZ'.
    При этом, в Python3.10 fromisoformat не умеет преобразовывать символ 'Z' на '+00:00' по UTC.
    Вызывает исключение HTTPException со статусом HTTP_400_BAD_REQUEST, если дата не по ISO 8601.
    """
    try:
        validated_date = datetime.fromisoformat(date[:-1] + "+00:00")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поле updateDate должно быть в формате ISO 8601: '%Y-%m-%dT%H:%M:%S.%fZ'.",
        )
    return validated_date


def validate_date_to_str_iso(date: datetime) -> str:
    """
    Преобразовывает дату из объекта datetime в строку, заменяя '+00:00' на 'Z'
    """
    return date.isoformat().replace("+00:00", "Z")


def build_system_item_dict(item) -> dict:
    item_size = item.size or 0
    return {
        "id": item.id,
        "url": item.url,
        "parentId": item.parent_id,
        "size": item_size,
        "type": item.type,
        "date": validate_date_to_str_iso(item.date_updated),
    }


def build_system_items_hierarchy(parent_id, nodes) -> list:
    children = []
    for node in nodes:
        if node.parent_id == parent_id:
            node_dict = build_system_item_dict(node)
            node_dict["children"] = (
                build_system_items_hierarchy(node.id, nodes) if node.type == SystemItemType.FOLDER else None
            )
            children.append(node_dict)
    return children


def calculate_size(item):
    if item["type"] == SystemItemType.FILE:
        return item["size"]
    elif item["type"] == SystemItemType.FOLDER:
        total_size = 0
        for child in item.get("children", []):
            total_size += calculate_size(child)
        item["size"] = total_size
        return total_size
    else:
        return 0
