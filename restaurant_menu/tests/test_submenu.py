"""Тест ручек, для работы с подменю."""

from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.menu import models

from .conftest import async_session_maker
from .handlers import MenuHandler


@pytest.fixture(scope='session')
async def fixture_menu_for_submenu(menu_data):
    """"""

    menu_handler = MenuHandler()
    return await menu_handler.create_menu(**menu_data)


@pytest.mark.asyncio(scope='function')
async def test_all_empty_submenus(async_client: AsyncClient, fixture_menu_for_submenu):
    """Тестируем вывод списка со всеми подменю, для определённого меню."""

    response = await async_client.get(f'/api/v1/menus/{fixture_menu_for_submenu.id}/submenus')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_new_submenu(
    async_client: AsyncClient,
    fixture_menu_for_submenu,
    fixture_current_submenu
):
    """Тестируем роутер для создания подменю."""

    response = await async_client.post(
        f'/api/v1/menus/{fixture_menu_for_submenu.id}/submenus',
        json={
            'title': 'Тестовое подменю 1',
            'description': 'Описание нового подменю 1'
        }
    )

    assert response.status_code == 201

    async with async_session_maker() as session:
        submenu = await session.execute(
            select(models.SubMenu).order_by(models.SubMenu.id.desc()).limit(1)
        )
        submenu = submenu.scalars().one_or_none()

    assert submenu.id is not None
    assert submenu.menu_id == fixture_menu_for_submenu.id
    assert submenu.title == 'Тестовое подменю 1'
    assert submenu.description == 'Описание нового подменю 1'

    fixture_current_submenu['obj'] = submenu


@pytest.mark.asyncio(scope='function')
async def test_error_new_submenu(async_client: AsyncClient, fixture_menu_for_submenu):
    """Тестируем получение ошибки при создании подменю с существующим названием."""

    menu_id = fixture_menu_for_submenu.id
    response = await async_client.post(f'/api/v1/menus/{menu_id}/submenus', json={
        'title': 'Тестовое подменю 1',
        'description': 'Описание нового подменю 2'
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое подменю уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_submenus(async_client: AsyncClient, fixture_menu_for_submenu):
    """Тестируем вывод списка со всеми подменю, для определённого меню."""

    response = await async_client.get(f'/api/v1/menus/{fixture_menu_for_submenu.id}/submenus')

    assert response.status_code == 200
    assert response.json() != []


@pytest.mark.asyncio(scope='function')
async def test_get_submenu(
    async_client: AsyncClient,
    fixture_menu_for_submenu,
    fixture_current_submenu
):
    """Тестируем вывод определённого подменю."""

    menu_id = fixture_menu_for_submenu.id
    submenu = fixture_current_submenu['obj']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu.id}')

    assert response.status_code == 200

    assert submenu.id == UUID(response.json()['id'])
    assert submenu.menu_id == menu_id
    assert submenu.title == response.json()['title']
    assert submenu.description == response.json()['description']


@pytest.mark.asyncio(scope='function')
async def test_error_get_submenu(async_client: AsyncClient, fixture_menu_for_submenu):
    """Тестируем получение ошибки при выводе определённого подменю с несуществующим «id»."""

    menu_id = fixture_menu_for_submenu.id
    response = await async_client.get(
        f'/api/v1/menus/{menu_id}/submenus/497f6eca-6276-4993-bfeb-53cbbbba6f08',
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_submenu(
    async_client: AsyncClient,
    fixture_menu_for_submenu,
    fixture_current_submenu
):
    """Тестируем роутер для обновления информации о подменю."""

    menu_id = fixture_menu_for_submenu.id
    submenu = fixture_current_submenu['obj']
    response = await async_client.patch(
        f'/api/v1/menus/{menu_id}/submenus/{submenu.id}',
        json={
            'title': 'Update title submenu',
            'description': 'Update description submenu'
        }
    )

    assert response.status_code == 200

    async with async_session_maker() as session:
        update_submenu = await session.execute(
            select(models.SubMenu).where(models.SubMenu.id == submenu.id)
        )
        update_submenu = update_submenu.scalars().one_or_none()

    assert update_submenu.id == submenu.id
    assert update_submenu.menu_id == menu_id
    assert update_submenu.title == 'Update title submenu'
    assert update_submenu.description == 'Update description submenu'


@pytest.mark.asyncio(scope='function')
async def test_delete_submenu(
    async_client: AsyncClient,
    fixture_menu_for_submenu,
    fixture_current_submenu
):
    """Тестируем роутер для удаления подменю."""

    menu_id = fixture_menu_for_submenu.id
    submenu = fixture_current_submenu['obj']
    response = await async_client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu.id}')

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The submenu has been deleted'}

    menu_handler = MenuHandler()
    await menu_handler.delete_menu(fixture_menu_for_submenu.id)
