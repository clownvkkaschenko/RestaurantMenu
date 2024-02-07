from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src import models
from src.menus.crud import get_menu_by_id


async def create_submenu(
        db: AsyncSession,
        menu_id: UUID,
        title: str,
        description: str,
) -> models.SubMenu:
    """Создаём новое подменю, для определённого, по полю «id», меню.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu_id (UUID): id меню.
        - title (str): Название подменю.
        - description (str): Описание подменю.

    Returns:
        - SubMenu: Объект подменю, если нет ошибок при создании.
    """

    new_submenu = models.SubMenu(menu_id=menu_id, title=title, description=description)

    try:
        db.add(new_submenu)
        await db.commit()
        await db.refresh(new_submenu)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое подменю уже зарегестрировано.'
        )

    menu = await get_menu_by_id(db=db, menu_id=menu_id)
    menu.submenus_count += 1
    await db.commit()

    return new_submenu


async def get_submenu_by_id(
        db: AsyncSession,
        menu_id: UUID,
        submenu_id: UUID,
) -> Optional[models.SubMenu]:
    """Получаем один объект из модели «SubMenu» по полю «id».

    - Проверяем подменю на существование.
    - Проверяем принадлежит ли подменю, к переданному id родителя(меню).

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - menu_id (UUID): id меню.
        - submenu_id (UUID): id подменю.

    Returns:
        - SubMenu | None: Объект подменю, если найден.
    """

    submenu = await db.execute(select(models.SubMenu).where(models.SubMenu.id == submenu_id))
    submenu = submenu.scalars().one_or_none()

    if submenu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='submenu not found',
        )
    if submenu.menu_id != menu_id:
        raise HTTPException(
            status_code=404,
            detail=f'Подменю с id {submenu_id} не принадлежит к меню с id {menu_id}.'
        )

    return submenu


async def update_submenu_by_id(
        db: AsyncSession,
        submenu: models.SubMenu,
        title: Optional[str],
        description: Optional[str],
) -> models.SubMenu:
    """Обновляем объект модели «SubMenu» (название или описание).

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - submenu (models.SubMenu): Объект подменю.
        - title (str | None): Новое название.
        - description (str | None): Новое описание.

    Returns:
        - SubMenu : Объект подменю.
    """

    if title or description:
        if title:
            submenu.title = title
        if description:
            submenu.description = description
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ни одно из значений (title, description) не предоставлено для обновления.'
        )

    try:
        await db.commit()
        await db.refresh(submenu)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое подменю уже зарегестрировано.'
        )

    return submenu


async def delete_submenu_by_id(
        db: AsyncSession,
        submenu: models.SubMenu,
        menu_id: UUID,
        submenu_id: UUID,
) -> None:
    """Удаляем один объект из модели «SubMenu» по полю «id».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - submenu: Объект подменю.
        - menu_id (UUID): id меню.
        - submenu_id (UUID): id подменю.

    Returns:
        - None
    """

    await db.execute(delete(models.SubMenu).where(models.SubMenu.id == submenu_id))
    await db.commit()

    menu = await get_menu_by_id(db=db, menu_id=menu_id)
    menu.submenus_count -= 1
    menu.dishes_count -= submenu.dishes_count
    await db.commit()
