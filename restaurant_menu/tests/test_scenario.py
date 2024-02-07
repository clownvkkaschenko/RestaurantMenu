"""Тестовый сценарий «Проверка количества блюд и количества подменю в меню» из Postman."""

from typing import Dict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src import models

from .conftest import async_session_maker


@pytest.mark.asyncio(scope='function')
async def test_scenario_new_menu(async_client: AsyncClient, fixture_current_menu: Dict):
    """Создаём меню."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Новое меню, для тестового сценария, 1',
        'description': 'Описание нового меню, для тестового сценария, 1'
    })
    assert response.status_code == 201

    async with async_session_maker() as session:
        menu = await session.execute(
            select(models.Menu).order_by(models.Menu.id.desc()).limit(1)
        )
        menu = menu.scalars().one_or_none()

    assert menu.id is not None
    assert menu.title == 'Новое меню, для тестового сценария, 1'
    assert menu.description == 'Описание нового меню, для тестового сценария, 1'
    assert menu.submenus_count == 0
    assert menu.dishes_count == 0

    fixture_current_menu['obj'] = menu


@pytest.mark.asyncio(scope='function')
async def test_scenario_new_submenu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict,
):
    """Создаём подменю."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.post(f'/api/v1/menus/{menu.id}/submenus', json={
        'title': 'Новое подменю, для тестового сценария, 1',
        'description': 'Описание нового подменю, для тестового сценария, 1'
    })
    assert response.status_code == 201

    async with async_session_maker() as session:
        submenu = await session.execute(
            select(models.SubMenu).order_by(models.SubMenu.id.desc()).limit(1)
        )
        submenu = submenu.scalars().one_or_none()

    assert submenu.id is not None
    assert submenu.menu_id == menu.id
    assert submenu.title == 'Новое подменю, для тестового сценария, 1'
    assert submenu.description == 'Описание нового подменю, для тестового сценария, 1'
    assert submenu.dishes_count == 0

    fixture_current_submenu['obj'] = submenu


@pytest.mark.asyncio(scope='function')
async def test_scenario_new_dish_1(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict[str, models.SubMenu],
):
    """Создаём блюдо 1."""

    menu: models.Menu = fixture_current_menu['obj']
    submenu: models.SubMenu = fixture_current_submenu['obj']

    response = await async_client.post(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes',
        json={
            'title': 'Новое блюдо, для тестового сценария, 1',
            'description': 'Описание нового блюда, для тестового сценария, 1',
            'price': 120.22
        }
    )
    assert response.status_code == 201

    async with async_session_maker() as session:
        dish = await session.execute(
            select(models.Dish).where(models.Dish.id == response.json()['id'])
        )
        dish = dish.scalars().one_or_none()

    assert dish.id is not None
    assert dish.submenu_id == submenu.id
    assert dish.title == 'Новое блюдо, для тестового сценария, 1'
    assert dish.description == 'Описание нового блюда, для тестового сценария, 1'
    assert dish.price == 120.22


@pytest.mark.asyncio(scope='function')
async def test_scenario_new_dish_2(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict[str, models.SubMenu],
):
    """Создаём блюдо 2."""

    menu: models.Menu = fixture_current_menu['obj']
    submenu: models.SubMenu = fixture_current_submenu['obj']

    response = await async_client.post(
        f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes',
        json={
            'title': 'Новое блюдо, для тестового сценария, 2',
            'description': 'Описание нового блюда, для тестового сценария, 2',
            'price': 120.22
        }
    )
    assert response.status_code == 201

    async with async_session_maker() as session:
        dish = await session.execute(
            select(models.Dish).where(models.Dish.id == response.json()['id'])
        )
        dish = dish.scalars().one_or_none()

    assert dish.id is not None
    assert dish.submenu_id == submenu.id
    assert dish.title == 'Новое блюдо, для тестового сценария, 2'
    assert dish.description == 'Описание нового блюда, для тестового сценария, 2'
    assert dish.price == 120.22


@pytest.mark.asyncio(scope='function')
async def test_scenario_get_menu_1(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Просматриваем определенноё меню первый раз."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}')
    assert response.status_code == 200

    async with async_session_maker() as session:
        current_menu = await session.execute(
            select(models.Menu).where(models.Menu.id == menu.id)
        )
        current_menu = current_menu.scalars().one_or_none()

    assert current_menu.id == UUID(response.json()['id'])
    assert current_menu.title == response.json()['title']
    assert current_menu.description == response.json()['description']
    assert current_menu.submenus_count == response.json()['submenus_count']
    assert current_menu.dishes_count == response.json()['dishes_count']
    assert current_menu.submenus_count == 1
    assert current_menu.dishes_count == 2


@pytest.mark.asyncio(scope='function')
async def test_scenario_get_submenu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict[str, models.SubMenu],
):
    """Просматриваем определенноё подменю."""

    menu: models.Menu = fixture_current_menu['obj']
    submenu: models.SubMenu = fixture_current_submenu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}')
    assert response.status_code == 200

    async with async_session_maker() as session:
        current_submenu = await session.execute(
            select(models.SubMenu).where(models.SubMenu.id == submenu.id)
        )
        current_submenu = current_submenu.scalars().one_or_none()

    assert current_submenu.id == UUID(response.json()['id'])
    assert current_submenu.title == response.json()['title']
    assert current_submenu.description == response.json()['description']
    assert current_submenu.dishes_count == response.json()['dishes_count']
    assert current_submenu.dishes_count == 2


@pytest.mark.asyncio(scope='function')
async def test_scenario_delete_submenu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict[str, models.SubMenu],
):
    """Удаляем подменю."""

    menu: models.Menu = fixture_current_menu['obj']
    submenu: models.SubMenu = fixture_current_submenu['obj']

    response = await async_client.delete(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}')
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The submenu has been deleted'}


@pytest.mark.asyncio(scope='function')
async def test_scenario_all_submenus(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Просматриваем список подменю."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}/submenus')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_scenario_all_dishes(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
    fixture_current_submenu: Dict,
):
    """Просматриваем список блюд."""

    menu: models.Menu = fixture_current_menu['obj']
    submenu: None = fixture_current_submenu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_scenario_get_menu_2(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Просматриваем определенноё меню второй раз."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}')
    assert response.status_code == 200

    async with async_session_maker() as session:
        current_menu = await session.execute(
            select(models.Menu).where(models.Menu.id == menu.id)
        )
        current_menu = current_menu.scalars().one_or_none()

    assert current_menu.id == UUID(response.json()['id'])
    assert current_menu.title == response.json()['title']
    assert current_menu.description == response.json()['description']
    assert current_menu.submenus_count == response.json()['submenus_count']
    assert current_menu.dishes_count == response.json()['dishes_count']
    assert current_menu.submenus_count == 0
    assert current_menu.dishes_count == 0


@pytest.mark.asyncio(scope='function')
async def test_scenario_delete_menu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Удаляем меню."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.delete(f'/api/v1/menus/{menu.id}')
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The menu has been deleted'}


@pytest.mark.asyncio(scope='function')
async def test_scenario_all_menus(async_client: AsyncClient):
    """Просматриваем список меню."""

    response = await async_client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == []
