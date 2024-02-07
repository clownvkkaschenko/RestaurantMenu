from uuid import UUID, uuid4

from sqlalchemy import delete
from src.menu import models

from .conftest import async_session_maker


class MenuHandler:
    """"""

    async def create_menu(self, title: str, description: str):
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
        async with async_session_maker() as session:
            await session.execute(delete(models.Menu).where(models.Menu.id == menu_id))
            await session.commit()


class SubMenuHandler:
    """"""

    async def create_submenu(self, menu_id: UUID, title: str, description: str):
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
        async with async_session_maker() as session:
            await session.execute(
                delete(models.SubMenu).where(models.SubMenu.id == submenu_id)
            )
            await session.commit()


class DishHandler:
    """"""

    async def create_dish(self, submenu_id: UUID, title: str, description: str, price: float):
        async with async_session_maker() as session:
            dish = models.Dish(
                id=uuid4(),
                submenu_id=submenu_id,
                title=title,
                description=description,
                price=price
            )
            session.add(dish)
            await session.commit()
            return dish

    async def delete_dish(self, dish_id: UUID):
        async with async_session_maker() as session:
            await session.execute(delete(models.Dish).where(models.Dish.id == dish_id))
            await session.commit()
