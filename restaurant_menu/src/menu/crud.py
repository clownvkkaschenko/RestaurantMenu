"""CRUD-functions."""

from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Row, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.menu import models


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


# ==============================================================================
# ==============================================================================
#                           --- CRUD for Menu ---
# ==============================================================================
# ==============================================================================
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


# ==============================================================================
# ==============================================================================
#                           --- CRUD for Submenu ---
# ==============================================================================
# ==============================================================================
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


# ==============================================================================
# ==============================================================================
#                           --- CRUD for Dish ---
# ==============================================================================
# ==============================================================================
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
