"""Тестовый сценарий «Проверка количества блюд и подменю в меню»."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.menu import models


@pytest.fixture(scope='session')
def fixture_script_new_menu():
    return {}


@pytest.fixture(scope='session')
def fixture_script_new_submenu():
    return {}


@pytest.mark.asyncio(scope='function')
async def test_script_new_menu(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu
):
    """Создаём меню."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Новое меню, для тестового сценария, 1',
        'description': 'Описание нового меню, для тестового сценария, 1'
    })

    assert response.status_code == 201

    new_menu_info = response.json()

    menu = await override_get_db.execute(
        select(models.Menu).where(models.Menu.id == new_menu_info['id'])
    )
    menu = menu.scalars().one_or_none()

    assert menu.title == new_menu_info['title']
    assert menu.description == new_menu_info['description']
    assert menu.submenus_count == new_menu_info['submenus_count']
    assert menu.dishes_count == new_menu_info['dishes_count']

    fixture_script_new_menu['id'] = new_menu_info['id']


@pytest.mark.asyncio(scope='function')
async def test_script_new_submenu(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu,
    fixture_script_new_submenu
):
    """Создаём подменю."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.post(f'/api/v1/menus/{menu_id}/submenus', json={
        'title': 'Новое подменю, для тестового сценария, 1',
        'description': 'Описание нового подменю, для тестового сценария, 1'
    })

    assert response.status_code == 201

    new_submenu_info = response.json()

    submenu = await override_get_db.execute(
        select(models.SubMenu).where(models.SubMenu.id == new_submenu_info['id'])
    )
    submenu = submenu.scalars().one_or_none()

    assert submenu.title == new_submenu_info['title']
    assert submenu.description == new_submenu_info['description']
    assert submenu.dishes_count == new_submenu_info['dishes_count']

    fixture_script_new_submenu['id'] = new_submenu_info['id']


@pytest.mark.asyncio(scope='function')
async def test_script_new_dish_1(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu,
    fixture_script_new_submenu,
):
    """Создаём блюдо 1."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
        json={
            'title': 'Новое блюдо, для тестового сценария, 1',
            'description': 'Описание нового блюда, для тестового сценария, 1',
            'price': 120.22
        }
    )

    assert response.status_code == 201

    new_dish_info = response.json()
    dish = await override_get_db.execute(
        select(models.Dish).where(models.Dish.id == new_dish_info['id'])
    )
    dish = dish.scalars().one_or_none()

    assert dish.title == new_dish_info['title']
    assert dish.description == new_dish_info['description']
    assert dish.price == float(new_dish_info['price'])


@pytest.mark.asyncio(scope='function')
async def test_script_new_dish_2(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu,
    fixture_script_new_submenu,
):
    """Создаём блюдо 2."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
        json={
            'title': 'Новое блюдо, для тестового сценария, 2',
            'description': 'Описание нового блюда, для тестового сценария, 2',
            'price': 322.22
        }
    )

    assert response.status_code == 201

    new_dish_info = response.json()
    dish = await override_get_db.execute(
        select(models.Dish).where(models.Dish.id == new_dish_info['id'])
    )
    dish = dish.scalars().one_or_none()

    assert dish.title == new_dish_info['title']
    assert dish.description == new_dish_info['description']
    assert dish.price == float(new_dish_info['price'])


@pytest.mark.asyncio(scope='function')
async def test_script_get_menu_1(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu
):
    """Просматриваем определенноё меню первый раз."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200

    menu = await override_get_db.execute(
        select(models.Menu).where(models.Menu.id == menu_id)
    )
    menu = menu.scalars().one_or_none()

    assert menu.id == uuid.UUID(response.json()['id'])
    assert menu.title == response.json()['title']
    assert menu.description == response.json()['description']
    assert menu.submenus_count == response.json()['submenus_count']
    assert menu.dishes_count == response.json()['dishes_count']


@pytest.mark.asyncio(scope='function')
async def test_script_get_submenu(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu,
    fixture_script_new_submenu,
):
    """Просматриваем определенноё подменю."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

    assert response.status_code == 200

    submenu = await override_get_db.execute(
        select(models.SubMenu).where(models.SubMenu.id == submenu_id)
    )
    submenu = submenu.scalars().one_or_none()

    assert submenu.id == uuid.UUID(response.json()['id'])
    assert submenu.title == response.json()['title']
    assert submenu.description == response.json()['description']
    assert submenu.dishes_count == response.json()['dishes_count']


@pytest.mark.asyncio(scope='function')
async def test_script_delete_submenu(
    async_client: AsyncClient,
    fixture_script_new_menu,
    fixture_script_new_submenu
):
    """Удаляем подменю."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The submenu has been deleted'}


@pytest.mark.asyncio(scope='function')
async def test_script_all_submenus(async_client: AsyncClient, fixture_script_new_menu):
    """Просматриваем список подменю."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_script_all_dishes(
    async_client: AsyncClient,
    fixture_script_new_menu,
    fixture_script_new_submenu
):
    """Просматриваем список блюд."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_script_get_menu_2(
    async_client: AsyncClient,
    override_get_db,
    fixture_script_new_menu
):
    """Просматриваем определенноё меню второй раз."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200

    menu = await override_get_db.execute(
        select(models.Menu).where(models.Menu.id == menu_id)
    )
    menu = menu.scalars().one_or_none()

    assert menu.id == uuid.UUID(response.json()['id'])
    assert menu.title == response.json()['title']
    assert menu.description == response.json()['description']
    assert menu.submenus_count == response.json()['submenus_count']
    assert menu.dishes_count == response.json()['dishes_count']


@pytest.mark.asyncio(scope='function')
async def test_script_delete_menu(async_client: AsyncClient, fixture_script_new_menu):
    """Удаляем меню."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.delete(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The menu has been deleted'}


@pytest.mark.asyncio(scope='function')
async def test_script_all_menus(async_client: AsyncClient):
    """Просматриваем список меню."""

    response = await async_client.get('/api/v1/menus')

    assert response.status_code == 200
    assert response.json() == []
