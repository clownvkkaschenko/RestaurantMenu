"""Тест ручек, для работы с блюдами."""

from typing import Dict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src import models

from .conftest import async_session_maker
from .handlers import MenuHandler, SubMenuHandler


@pytest.fixture(scope='session')
async def fixture_menu_for_dish(menu_data: Dict[str, str]) -> models.Menu:
    """Создаём объект меню, для создания подменю."""

    menu_handler = MenuHandler()
    return await menu_handler.create_menu(**menu_data)


@pytest.fixture(scope='session')
async def fixture_submenu_for_dish(
    fixture_menu_for_dish: models.Menu,
    submenu_data: Dict[str, str],
) -> models.SubMenu:
    """Создаём объект подменю, для создания блюда."""

    menu: models.Menu = fixture_menu_for_dish

    submenu_handler = SubMenuHandler()
    return await submenu_handler.create_submenu(menu.id, **submenu_data)


@pytest.mark.asyncio(scope='function')
async def test_all_empty_dishes(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
):
    """Тестируем роутер для вывода списка всех блюд, при условии, что блюдо не создано."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish

    response = await async_client.get(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_new_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
    fixture_current_dish: Dict,
):
    """Тестируем роутер для создания нового блюда."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish

    response = await async_client.post(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes',
        json={
            'title': 'Новое блюдо 1',
            'description': 'Описание нового блюда 1',
            'price': 120.22
        }
    )
    assert response.status_code == 201

    async with async_session_maker() as session:
        dish = await session.execute(
            select(models.Dish).order_by(models.Dish.id.desc()).limit(1)
        )
        dish = dish.scalars().one_or_none()

    assert dish.id is not None
    assert dish.submenu_id == submenu.id
    assert dish.title == 'Новое блюдо 1'
    assert dish.description == 'Описание нового блюда 1'
    assert dish.price == 120.22

    fixture_current_dish['obj'] = dish


@pytest.mark.asyncio(scope='function')
async def test_error_new_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
):
    """Тестируем получение ошибки при создании блюда с существующим названием."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish

    response = await async_client.post(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes',
        json={
            'title': 'Новое блюдо 1',
            'description': 'Описание нового блюда 2',
            'price': 120.22
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое блюдо уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_dishes(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
):
    """Тестируем роутер для вывода списка всех блюд, для определённого подменю."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish

    response = await async_client.get(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes'
    )
    assert response.status_code == 200
    assert response.json() != []


@pytest.mark.asyncio(scope='function')
async def test_get_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
    fixture_current_dish: Dict[str, models.Dish],
):
    """Тестируем роутер для вывода определённого блюда."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish
    dish: models.Dish = fixture_current_dish['obj']

    response = await async_client.get(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}'
    )
    assert response.status_code == 200
    assert dish.id == UUID(response.json()['id'])
    assert dish.submenu_id == fixture_submenu_for_dish.id
    assert dish.title == response.json()['title']
    assert dish.description == response.json()['description']
    assert dish.price == float(response.json()['price'])


@pytest.mark.asyncio(scope='function')
async def test_error_get_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
):
    """Тестируем получение ошибки при выводе определённого блюда с несуществующим «id»."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish

    response = await async_client.get(
        (f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/'
         f'dishes/497f6eca-6276-4993-bfeb-53cbbbba6f08')
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'dish not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
    fixture_current_dish: Dict[str, models.Dish],
):
    """Тестируем роутер для обновления информации о блюде."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish
    dish: models.Dish = fixture_current_dish['obj']

    response = await async_client.patch(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}',
        json={
            'title': 'Update title dish',
            'description': 'Update description dish',
            'price': 220.11
        }
    )
    assert response.status_code == 200

    async with async_session_maker() as session:
        update_dish = await session.execute(
            select(models.Dish).where(models.Dish.id == dish.id)
        )
        update_dish = update_dish.scalars().one_or_none()

    assert update_dish.id == dish.id
    assert update_dish.title == 'Update title dish'
    assert update_dish.description == 'Update description dish'
    assert update_dish.price == 220.11


@pytest.mark.asyncio(scope='function')
async def test_delete_dish(
    async_client: AsyncClient,
    fixture_menu_for_dish: models.Menu,
    fixture_submenu_for_dish: models.SubMenu,
    fixture_current_dish: Dict[str, models.Dish],
):
    """Тестируем роутер для удаления блюда."""

    menu: models.Menu = fixture_menu_for_dish
    submenu: models.SubMenu = fixture_submenu_for_dish
    dish: models.Dish = fixture_current_dish['obj']

    response = await async_client.delete(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}',
    )
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The dish has been deleted'}

    submenu_handler = SubMenuHandler()
    await submenu_handler.delete_submenu(fixture_submenu_for_dish.id)

    menu_handler = MenuHandler()
    await menu_handler.delete_menu(fixture_menu_for_dish.id)
