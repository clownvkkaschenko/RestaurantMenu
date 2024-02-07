"""CRUD-functions."""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src import models
from src.menus.crud import get_menu_by_id
from src.submenus.crud import get_submenu_by_id


async def create_dish(
        db: AsyncSession,
        menu_id: UUID,
        submenu_id: UUID,
        title: str,
        description: str,
        price: float,
) -> models.Dish:
    """Создаём новое блюдо, для определённого, по полю «id», подменю.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu_id (UUID): id меню.
        - submenu_id (UUID): id подменю.
        - title (str): Название блюда.
        - description (str): Описание блюда.
        - price (float): Цена блюда

    Returns:
        - Dish: Объект блюда, если нет ошибок при создании.
    """

    menu = await get_menu_by_id(db=db, menu_id=menu_id)
    submenu = await get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id)

    new_dish = models.Dish(
        submenu_id=submenu_id,
        title=title,
        description=description,
        price=price,
    )

    try:
        db.add(new_dish)
        await db.commit()
        await db.refresh(new_dish)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое блюдо уже зарегестрировано.'
        )

    submenu.dishes_count += 1
    menu.dishes_count += 1
    await db.commit()

    return new_dish


async def get_dish_by_id(
        db: AsyncSession,
        submenu_id: UUID,
        dish_id: UUID,
) -> Optional[models.Dish]:
    """Получаем один объект из модели «Dish» по полю «id».

    - Проверяем блюдо на существование.
    - Проверяем принадлежит ли блюдо, к переданному id подменю.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - submenu_id (UUID): id подменю.
        - dish_id (UUID): id блюда.

    Returns:
        - Dish | None: Объект блюда, если найден.
    """

    dish = await db.execute(select(models.Dish).where(models.Dish.id == dish_id))
    dish = dish.scalars().one_or_none()

    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found',
        )
    if dish.submenu_id != submenu_id:
        raise HTTPException(
            status_code=404,
            detail=f'Блюдо с id {dish_id} не принадлежит к подменю с id {submenu_id}.'
        )

    return dish


async def update_dish_by_id(
        db: AsyncSession,
        dish: models.Dish,
        title: Optional[str],
        description: Optional[str],
        price: Optional[float],
) -> models.Dish:
    """Обновляем объект модели «Dish» (название, описание или цену).

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - dish (models.Dish): Объект блюда.
        - title (str | None): Новое название.
        - description (str | None): Новое описание.
        - price (float | None): Новая цена.

    Returns:
        - Dish : Объект блюда.
    """

    if title or description or price:
        if title:
            dish.title = title
        if description:
            dish.description = description
        if price:
            dish.price = price
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=('Ни одно из значений (title, description, price) '
                    'не предоставлено для обновления.')
        )

    try:
        await db.commit()
        await db.refresh(dish)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое блюдо уже зарегестрировано.'
        )

    return dish


async def delete_dish_by_id(
        db: AsyncSession,
        menu: models.Menu,
        submenu: models.SubMenu,
        dish_id: UUID,
) -> None:
    """Удаляем один объект из модели «Dish» по полю «id».

    Меняем количество блюд в меню и подменю.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu: Объект меню.
        - submenu: Объект подменю.
        - dish_id (UUID): id блюда.

    Returns:
        - None
    """

    await db.execute(delete(models.Dish).where(models.Dish.id == dish_id))
    await db.commit()

    menu.dishes_count -= 1
    submenu.dishes_count -= 1
    await db.commit()
