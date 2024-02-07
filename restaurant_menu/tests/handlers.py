from uuid import UUID, uuid4

from sqlalchemy import delete
from src.menu import models

from .conftest import async_session_maker


class MenuHandler:
    """Класс для выполнения операций, связанных с меню."""

    async def create_menu(self, title: str, description: str):
        """Создаём новое меню.

        Args:
            - title (str): Заголовок меню.
            - description (str): Описание меню.

        Returns:
            - models.Menu: Объект созданного меню.
        """

        async with async_session_maker() as session:
            menu = models.Menu(
                id=uuid4(),
                title=title,
                description=description
            )
            session.add(menu)
            await session.commit()
            return menu

    async def delete_menu(self, menu_id: UUID):
        """Удаляем меню по «id».

        Args:
            - menu_id (UUID): ID меню, которое нужно удалить.
        """

        async with async_session_maker() as session:
            await session.execute(delete(models.Menu).where(models.Menu.id == menu_id))
            await session.commit()


class SubMenuHandler:
    """Класс для выполнения операций, связанных с подменю."""

    async def create_submenu(self, menu_id: UUID, title: str, description: str):
        """Создаём новое подменю.

        Args:
            - menu_id (UUID): ID главного меню.
            - title (str): Заголовок подменю.
            - description (str): Описание подменю.

        Returns:
            - models.SubMenu: Объект созданного подменю.
        """

        async with async_session_maker() as session:
            submenu = models.SubMenu(
                id=uuid4(),
                menu_id=menu_id,
                title=title,
                description=description
            )
            session.add(submenu)
            await session.commit()
            return submenu

    async def delete_submenu(self, submenu_id: UUID):
        """Удаляем подменю по «id».

        Args:
            - submenu_id (UUID): ID подменю, которое нужно удалить.
        """

        async with async_session_maker() as session:
            await session.execute(
                delete(models.SubMenu).where(models.SubMenu.id == submenu_id)
            )
            await session.commit()
