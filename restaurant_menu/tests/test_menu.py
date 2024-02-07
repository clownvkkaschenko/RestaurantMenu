"""Тест ручек, для работы с меню."""

from typing import Dict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.menu import models

from .conftest import async_session_maker


@pytest.mark.asyncio(scope='function')
async def test_all_empty_menus(async_client: AsyncClient):
    """Тестируем роутер для вывода списка со всеми меню, при условии, что меню не созданы."""

    response = await async_client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(scope='function')
async def test_new_menu(async_client: AsyncClient, fixture_current_menu: Dict):
    """Тестируем роутер для создания меню."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Тестовое меню 1',
        'description': 'Описание нового меню 1'
    })
    assert response.status_code == 201

    async with async_session_maker() as session:
        menu = await session.execute(
            select(models.Menu).order_by(models.Menu.id.desc()).limit(1)
        )
        menu = menu.scalars().one_or_none()

    assert menu.id is not None
    assert menu.title == 'Тестовое меню 1'
    assert menu.description == 'Описание нового меню 1'

    fixture_current_menu['obj'] = menu


@pytest.mark.asyncio(scope='function')
async def test_error_new_menu(async_client: AsyncClient):
    """Тестируем получение ошибки при создании меню с существующим названием."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Тестовое меню 1',
        'description': 'Описание нового меню 2'
    })
    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое меню уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_menus(async_client: AsyncClient):
    """Тестируем роутер для вывода списка со всеми меню."""

    response = await async_client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() != []


@pytest.mark.asyncio(scope='function')
async def test_get_menu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Тестируем роутер для вывода определённого меню по его «id»."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.get(f'/api/v1/menus/{menu.id}')
    assert response.status_code == 200
    assert menu.id == UUID(response.json()['id'])
    assert menu.title == response.json()['title']
    assert menu.title == 'Тестовое меню 1'
    assert menu.description == response.json()['description']
    assert menu.description == 'Описание нового меню 1'


@pytest.mark.asyncio(scope='function')
async def test_error_get_menu(async_client: AsyncClient):
    """Тестируем получение ошибки при выводе определённого меню с несуществующим «id»."""

    response = await async_client.get('/api/v1/menus/497f6eca-6276-4993-bfeb-53cbbbba6f08')
    assert response.status_code == 404
    assert response.json() == {'detail': 'menu not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_menu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Тестируем роутер для обновления информации о меню."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.patch(f'/api/v1/menus/{menu.id}', json={
        'title': 'Update title menu',
        'description': 'Update description menu'
    })
    assert response.status_code == 200

    async with async_session_maker() as session:
        update_menu = await session.execute(
            select(models.Menu).where(models.Menu.id == menu.id)
        )
        update_menu = update_menu.scalars().one_or_none()

    assert update_menu.id == menu.id
    assert update_menu.title == 'Update title menu'
    assert update_menu.description == 'Update description menu'


@pytest.mark.asyncio(scope='function')
async def test_delete_menu(
    async_client: AsyncClient,
    fixture_current_menu: Dict[str, models.Menu],
):
    """Тестируем роутер для удаления меню."""

    menu: models.Menu = fixture_current_menu['obj']

    response = await async_client.delete(f'/api/v1/menus/{menu.id}')
    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The menu has been deleted'}
