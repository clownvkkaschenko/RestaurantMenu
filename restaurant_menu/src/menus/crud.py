"""CRUD-functions."""

from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Row, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src import models


async def get_counts_submenus_and_dishes_from_menu(
        db: AsyncSession,
        menu_id: UUID
) -> Row[Tuple[models.Menu, int, int]]:
    """ORM запрос для вывода количества подменю и количества блюд для меню."""

    query = (
        select(
            models.Menu,
            func.count(models.SubMenu.id.distinct()).label('submenus_count'),
            func.count(models.Dish.id.distinct()).label('dishes_count')
        )
        .where(models.Menu.id == menu_id)
        .select_from(models.Menu).outerjoin(models.SubMenu).outerjoin(models.Dish)
        .group_by(models.Menu.id)
    )

    result = await db.execute(query)
    menu_info: Row[Tuple[models.Menu, int, int]] | None = result.fetchone()

    if menu_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found',
        )

    return menu_info


async def create_menu(
        db: AsyncSession,
        title: str,
        description: str,
) -> models.Menu:
    """Создаём новое меню.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - title (str): Название меню.
        - description (str): Описание меню.

    Returns:
        - Menu: Объект меню, если нет ошибок при создании.
    """

    new_menu = models.Menu(title=title, description=description)

    try:
        db.add(new_menu)
        await db.commit()
        await db.refresh(new_menu)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое меню уже зарегестрировано.'
        )

    return new_menu


async def get_all_menus(db: AsyncSession) -> List[Optional[models.Menu]]:
    """Получаем все объекты из модели «Menu»

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.

    Returns:
        - List[Menu | None]: Список меню, если найдены, иначе None.
    """

    menus = await db.execute(select(models.Menu))
    return menus.scalars().all()


async def get_menu_by_id(
        db: AsyncSession,
        menu_id: UUID,
) -> Optional[models.Menu]:
    """Получаем один объект из модели «Menu» по полю «id».

    - Проверяем меню на существование.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu_id (UUID): id меню.

    Returns:
        - Menu | None: Объект меню, если найден.
    """

    menu = await db.execute(select(models.Menu).where(models.Menu.id == menu_id))
    menu = menu.scalars().one_or_none()

    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found',
        )

    return menu


async def update_menu_by_id(
        db: AsyncSession,
        menu: models.Menu,
        title: Optional[str],
        description: Optional[str],
) -> models.Menu:
    """Обновляем объект модели «Menu» (название или описание).

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu (models.Menu): Объект меню.
        - title (str | None): Новое название.
        - description (str | None): Новое описание.

    Returns:
        - Menu : Объект меню.
    """

    if title or description:
        if title:
            menu.title = title
        if description:
            menu.description = description
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ни одно из значений (title, description) не предоставлено для обновления.'
        )

    try:
        await db.commit()
        await db.refresh(menu)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое меню уже зарегестрировано.'
        )

    return menu


async def delete_menu_by_id(
        db: AsyncSession,
        menu_id: UUID,
) -> None:
    """Удаляем один объект из модели «Menu» по полю «id».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu_id (UUID): id меню.

    Returns:
        - None
    """

    await db.execute(delete(models.Menu).where(models.Menu.id == menu_id))
    await db.commit()
