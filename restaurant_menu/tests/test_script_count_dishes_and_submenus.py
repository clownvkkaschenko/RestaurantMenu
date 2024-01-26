"""Тестовый сценарий «Проверка количества блюд и подменю в меню»."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.fixture(scope='session')
def fixture_script_new_menu():
    return {}


@pytest.fixture(scope='session')
def fixture_script_new_submenu():
    return {}


@pytest.mark.asyncio(scope='function')
async def test_script_new_menu(async_client: AsyncClient, fixture_script_new_menu):
    """Создаём меню."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Новое меню, для тестового сценария, 1',
        'description': 'Описание нового меню, для тестового сценария, 1'
    })

    assert response.status_code == 201

    menu = response.json()
    assert uuid.UUID(menu['id'])
    assert menu['title'] == 'Новое меню, для тестового сценария, 1'
    assert menu['description'] == 'Описание нового меню, для тестового сценария, 1'
    assert menu['submenus_count'] == 0
    assert menu['dishes_count'] == 0

    fixture_script_new_menu['id'] = menu['id']


@pytest.mark.asyncio(scope='function')
async def test_script_new_submenu(
    async_client: AsyncClient,
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

    submenu = response.json()
    assert uuid.UUID(submenu['id'])
    assert submenu['title'] == 'Новое подменю, для тестового сценария, 1'
    assert submenu['description'] == 'Описание нового подменю, для тестового сценария, 1'
    assert submenu['dishes_count'] == 0

    fixture_script_new_submenu['id'] = submenu['id']


@pytest.mark.asyncio(scope='function')
async def test_script_new_dish_1(
    async_client: AsyncClient,
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

    dish = response.json()
    assert uuid.UUID(dish['id'])
    assert dish['title'] == 'Новое блюдо, для тестового сценария, 1'
    assert dish['description'] == 'Описание нового блюда, для тестового сценария, 1'
    assert dish['price'] == '120.22'


@pytest.mark.asyncio(scope='function')
async def test_script_new_dish_2(
    async_client: AsyncClient,
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

    dish = response.json()
    assert uuid.UUID(dish['id'])
    assert dish['title'] == 'Новое блюдо, для тестового сценария, 2'
    assert dish['description'] == 'Описание нового блюда, для тестового сценария, 2'
    assert dish['price'] == '322.22'


@pytest.mark.asyncio(scope='function')
async def test_script_get_menu_1(async_client: AsyncClient, fixture_script_new_menu):
    """Просматриваем определенноё меню первый раз."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200

    menu = response.json()
    assert menu['id'] == menu_id
    assert menu['title'] == 'Новое меню, для тестового сценария, 1'
    assert menu['description'] == 'Описание нового меню, для тестового сценария, 1'
    assert menu['submenus_count'] == 1
    assert menu['dishes_count'] == 2


@pytest.mark.asyncio(scope='function')
async def test_script_get_submenu(
    async_client: AsyncClient,
    fixture_script_new_menu,
    fixture_script_new_submenu,
):
    """Просматриваем определенноё подменю."""

    menu_id = fixture_script_new_menu['id']
    submenu_id = fixture_script_new_submenu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

    assert response.status_code == 200

    submenu = response.json()
    assert submenu['id'] == submenu_id
    assert submenu['title'] == 'Новое подменю, для тестового сценария, 1'
    assert submenu['description'] == 'Описание нового подменю, для тестового сценария, 1'
    assert submenu['dishes_count'] == 2


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
async def test_script_get_menu_2(async_client: AsyncClient, fixture_script_new_menu):
    """Просматриваем определенноё меню второй раз."""

    menu_id = fixture_script_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200

    menu = response.json()
    assert menu['id'] == menu_id
    assert menu['title'] == 'Новое меню, для тестового сценария, 1'
    assert menu['description'] == 'Описание нового меню, для тестового сценария, 1'
    assert menu['submenus_count'] == 0
    assert menu['dishes_count'] == 0


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
