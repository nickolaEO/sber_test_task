import json
from datetime import timedelta

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import alias, delete, select
from sqlalchemy.dialects.postgresql import insert

from app.api.models.system_items import ItemUpdatesOut, SystemItemImportData
from app.api.routers.utils import (
    build_system_item_dict,
    build_system_items_hierarchy,
    calculate_size,
    check_parent_exists,
    check_system_item_exists,
    validate_item_size,
    validate_item_type,
    validate_str_to_date_iso,
)
from app.database import SystemItem
from app.database.models.system_items import SystemItemType
from app.session_manager import session_manager

system_items_router = APIRouter(tags=["System Items"])


@system_items_router.post("/imports")
async def import_system_items(input_data: SystemItemImportData):
    items = input_data.items
    update_date = validate_str_to_date_iso(input_data.update_date)
    async with session_manager.transactional_session() as session:
        for item in items:
            validate_item_type(item.id, item.type)
            validate_item_size(item.id, item.size, item.type)
            if item.parent_id is not None:
                await check_parent_exists(session, item.id, item.parent_id)
            dict_item = item.dict()
            dict_item["date_updated"] = update_date
            query = (
                insert(SystemItem)
                .values(**dict_item)
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_=dict_item,
                )
            )
            await session.execute(query)
        await session.commit()
    content = {"message": "Вставка или обновление прошли успешно."}
    return JSONResponse(status_code=status.HTTP_200_OK, content=json.dumps(content))


@system_items_router.delete("/delete/{id}")
async def delete_system_item(id: str, date: str):
    # Согласно ТЗ, здесь в query_params принимается date как обязательный параметр. В рамках реализованного api
    # эндпоинта этот параметр не используется. Чтобы не ломать схему запроса и сохранить совместимость,
    # параметр принимается и просто валидируется на корректность формата даты.
    validate_str_to_date_iso(date)
    async with session_manager.transactional_session() as session:
        await check_system_item_exists(session, id)
        query = delete(SystemItem).filter(SystemItem.id == id)
        await session.execute(query)
        await session.commit()
    return Response(status_code=status.HTTP_200_OK)


@system_items_router.get("/nodes/{id}")
async def get_system_item_nodes(id: str):
    async with session_manager.transactional_session() as session:
        system_item = await check_system_item_exists(session, id)
        system_item_cte = select(SystemItem.id).filter(SystemItem.id == id).cte(recursive=True)
        parent_alias = alias(system_item_cte, name="p")
        child_alias = alias(SystemItem, name="c")
        system_item_cte = system_item_cte.union_all(
            select(child_alias.c.id).where(child_alias.c.parent_id == parent_alias.c.id)
        )
        query = select(SystemItem).filter(SystemItem.id.in_(system_item_cte))
        result = await session.scalars(query)
        system_items = result.all()

        hierarchy = build_system_item_dict(system_item)
        hierarchy["children"] = (
            build_system_items_hierarchy(system_item.id, system_items)
            if system_item.type == SystemItemType.FOLDER
            else None
        )
        calculate_size(hierarchy)
    return hierarchy


@system_items_router.get("/updates", response_model=ItemUpdatesOut)
async def get_system_item_updates(date: str):
    date_to = validate_str_to_date_iso(date)
    date_from = date_to - timedelta(hours=24)
    async with session_manager.transactional_session() as session:
        query = select(SystemItem).filter(
            SystemItem.type == SystemItemType.FILE.name, SystemItem.date_updated.between(date_from, date_to)
        )
        result = await session.scalars(query)
        system_items = result.all()
    response = {"items": system_items}
    return response
