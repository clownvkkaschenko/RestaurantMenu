from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.menu import crud, models, schemas

menu_router = APIRouter()


# --- Routes for Menu ---
@menu_router.post('/api/v1/menus', response_model=schemas.DetailedMenuInfoPyd, status_code=201,
                  summary='Создать меню', tags=['Меню'])
async def new_menu(
    menu: schemas.BaseMenuPyd,
    db: AsyncSession = Depends(get_db),
) -> models.Menu:
    """Создаём новое меню."""

    menu_data: Dict[str, str] = menu.model_dump()

    return await crud.create_menu(db=db, **menu_data)


@menu_router.get('/api/v1/menus', response_model=List[schemas.DetailedMenuInfoPyd],
                 summary='Список меню', tags=['Меню'])
async def all_menus(db: AsyncSession = Depends(get_db)) -> List[Optional[models.Menu]]:
    """Выводим список со всеми меню."""

    return await crud.get_all_menus(db=db)


@menu_router.get('/api/v1/menus/{menu_id}', response_model=schemas.DetailedMenuInfoPyd,
                 summary='Определённое меню', tags=['Меню'])
async def get_menu(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> Optional[models.Menu]:
    """Выводим определённое меню по его «id»."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(db=db, menu_id=menu_id)

    return menu


@menu_router.patch('/api/v1/menus/{menu_id}', response_model=schemas.DetailedMenuInfoPyd,
                   summary='Обновить меню', tags=['Меню'])
async def update_menu(
    update_data: schemas.UpdateMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> models.Menu:
    """Обновляем информацию о меню."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(db=db, menu_id=menu_id)

    updated_menu: models.Menu = await crud.update_menu_by_id(
        db=db, menu=menu, **update_data.model_dump()
    )

    return updated_menu


@menu_router.delete('/api/v1/menus/{menu_id}',
                    response_model=schemas.DeleteObjPyd,
                    summary='Удалить меню', tags=['Меню'])
async def delete_menu(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем меню."""

    # Получаем объект меню, и проверяем его.
    await crud.get_menu_by_id(db=db, menu_id=menu_id)

    await crud.delete_menu_by_id(db=db, menu_id=menu_id)
    return {"status": True, "message": "The menu has been deleted"}


# --- Routes for Submenu ---
@menu_router.post('/api/v1/menus/{menu_id}/submenus',
                  response_model=schemas.DetailedSubmenuInfoPyd,
                  status_code=201, summary='Создать подменю', tags=['Подменю'])
async def new_submenu(
    submenu: schemas.BaseMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> models.SubMenu:
    """Создаём новое подменю, для определённого меню."""

    submenu_data: Dict[str, str] = submenu.model_dump()
    return await crud.create_submenu(db=db, menu_id=menu_id, **submenu_data)


@menu_router.get('/api/v1/menus/{menu_id}/submenus',
                 response_model=List[schemas.DetailedSubmenuInfoPyd],
                 summary='Список подменю', tags=['Подменю'])
async def all_submenus(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> List[Optional[models.SubMenu]]:
    """Выводим список со всеми подменю, для определённого меню."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(db=db, menu_id=menu_id)

    return menu.submenus


@menu_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                 response_model=schemas.DetailedSubmenuInfoPyd,
                 summary='Определённое подменю', tags=['Подменю'])
async def get_submenu(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> Optional[models.SubMenu]:
    """Выводим определённое подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    return submenu


@menu_router.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                   response_model=schemas.DetailedSubmenuInfoPyd,
                   summary='Обновить подменю', tags=['Подменю'])
async def update_submenu(
    update_data: schemas.UpdateMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> models.SubMenu:
    """Обновляем информацию о подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    updated_submenu: models.SubMenu = await crud.update_submenu_by_id(
        db=db, submenu=submenu, **update_data.model_dump()
    )

    return updated_submenu


@menu_router.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                    response_model=schemas.DeleteObjPyd,
                    summary='Удалить подменю', tags=['Подменю'])
async def delete_submenu(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    await crud.delete_submenu_by_id(
        db=db, submenu=submenu, menu_id=menu_id, submenu_id=submenu_id
    )

    return {"status": True, "message": "The submenu has been deleted"}


# --- Routes for Dish ---
@menu_router.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
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


@menu_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
                 response_model=List[schemas.DetailedDishInfoPyd],
                 summary='Список блюд', tags=['Блюдо'])
async def all_dishes(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> List[Optional[models.Dish]]:
    """Выводим список со всеми блюдами, для определённого подменю."""

    # Не могу использовать crud.get_submenu_by_id, так-как тесты в postman ожидают
    # получить пустой список, а мой метод возвращает ошибку 404 из-за отсутсвия подменю.
    submenu = await db.execute(select(models.SubMenu).where(models.SubMenu.id == submenu_id))
    submenu = submenu.scalars().one_or_none()

    if not submenu:
        return []
    return submenu.dishes


@menu_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
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


@menu_router.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
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


@menu_router.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                    response_model=schemas.DeleteObjPyd,
                    summary='Удалить блюдо', tags=['Блюдо'])
async def delete_dish(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    dish_id: UUID = Path(..., description='id блюда'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем блюдо."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    await crud.delete_dish_by_id(db=db, submenu=submenu, dish_id=dish_id)

    return {"status": True, "message": "The dish has been deleted"}
