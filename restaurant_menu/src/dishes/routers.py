from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src import models, schemas
from src.database import get_db
from src.dishes import crud

dish_router = APIRouter()


@dish_router.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                  response_model=schemas.DetailedDishInfoPyd,
                  status_code=201, summary='Создать блюдо', tags=['Блюдо'])
async def new_dish(
    dish: schemas.BaseDishPyd,
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> models.Dish:
    """Создаём новое блюдо, для определённого подменю."""

    dish_data: Dict[str, str] = dish.model_dump()

    return await crud.create_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, **dish_data)


@dish_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                 response_model=List[schemas.DetailedDishInfoPyd],
                 summary='Список блюд', tags=['Блюдо'])
async def all_dishes(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> List[Optional[models.Dish]]:
    """Выводим список со всеми блюдами, для определённого подменю."""

    # Не могу использовать get_submenu_by_id, так-как тесты в postman ожидают
    # получить пустой список, а мой метод возвращает ошибку 404 из-за отсутсвия подменю.
    submenu = await db.execute(select(models.SubMenu).where(models.SubMenu.id == submenu_id))
    submenu = submenu.scalars().one_or_none()

    if not submenu:
        return []
    return submenu.dishes


@dish_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                 response_model=schemas.DetailedDishInfoPyd,
                 summary='Определённое блюдо', tags=['Блюдо'])
async def get_dish(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    dish_id: UUID = Path(..., description='id блюда'),
    db: AsyncSession = Depends(get_db),
) -> Optional[models.Dish]:
    """Выводим определённое блюдо."""

    # Получаем объект подменю, и проверяем его.
    await crud.get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id)

    return await crud.get_dish_by_id(db=db, submenu_id=submenu_id, dish_id=dish_id)


@dish_router.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                   response_model=schemas.DetailedDishInfoPyd,
                   summary='Обновить блюдо', tags=['Блюдо'])
async def update_dish(
    update_data: schemas.UpdateDishPyd,
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    dish_id: UUID = Path(..., description='id блюда'),
    db: AsyncSession = Depends(get_db),
) -> models.Dish:
    """Обновляем информацию о блюде."""

    # Получаем объект подменю, и проверяем его.
    await crud.get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id)

    dish: Optional[models.Dish] = await crud.get_dish_by_id(
        db=db, submenu_id=submenu_id, dish_id=dish_id
    )

    return await crud.update_dish_by_id(db=db, dish=dish, **update_data.model_dump())


@dish_router.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                    response_model=schemas.DeleteObjPyd,
                    summary='Удалить блюдо', tags=['Блюдо'])
async def delete_dish(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    dish_id: UUID = Path(..., description='id блюда'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем блюдо."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(
        db=db, menu_id=menu_id
    )

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    await crud.delete_dish_by_id(db=db, menu=menu, submenu=submenu, dish_id=dish_id)

    return {"status": True, "message": "The dish has been deleted"}
