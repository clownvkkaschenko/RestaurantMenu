"""Тест ручек."""

import uuid

import pytest
from httpx import AsyncClient


# Сразу создаём меню и подменю, что-бы передать данные в фикстуры.
@pytest.mark.asyncio(scope='function')
async def test_new_menu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем роутер для создания нового меню."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Новое меню 1',
        'description': 'Описание нового меню 1'
    })

    assert response.status_code == 201

    menu = response.json()
    assert uuid.UUID(menu['id'])
    assert menu['title'] == 'Новое меню 1'
    assert menu['description'] == 'Описание нового меню 1'
    assert menu['submenus_count'] == 0
    assert menu['dishes_count'] == 0

    fixture_new_menu['id'] = menu['id']


@pytest.mark.asyncio(scope='function')
async def test_new_submenu(async_client: AsyncClient, fixture_new_menu, fixture_new_submenu):
    """Тестируем роутер для создания нового подменю."""

    menu_id = fixture_new_menu['id']
    response = await async_client.post(f'/api/v1/menus/{menu_id}/submenus', json={
        'title': 'Новое подменю 1',
        'description': 'Описание нового подменю 1'
    })

    assert response.status_code == 201

    submenu = response.json()
    assert uuid.UUID(submenu['id'])
    assert submenu['title'] == 'Новое подменю 1'
    assert submenu['description'] == 'Описание нового подменю 1'
    assert submenu['dishes_count'] == 0

    fixture_new_submenu['id'] = submenu['id']


# ==============================================================================
# ==============================================================================
#                           --- Tests for Dish ---
# ==============================================================================
# ==============================================================================
@pytest.mark.asyncio(scope='function')
async def test_new_dish(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
    fixture_new_dish,
):
    """Тестируем роутер для создания нового блюда, для определённого подменю."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
        json={
            'title': 'Новое блюдо 1',
            'description': 'Описание нового блюда 1',
            'price': 120.22
        }
    )

    assert response.status_code == 201

    dish = response.json()
    assert uuid.UUID(dish['id'])
    assert dish['title'] == 'Новое блюдо 1'
    assert dish['description'] == 'Описание нового блюда 1'
    assert dish['price'] == '120.22'

    fixture_new_dish['id'] = dish['id']


@pytest.mark.asyncio(scope='function')
async def test_error_new_dish(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
):
    """Тестируем получение ошибки при создании блюда с существующим названием."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
        json={
            'title': 'Новое блюдо 1',
            'description': 'Описание нового блюда 2',
            'price': 340.33
        }
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое блюдо уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_dishes(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
):
    """Тестируем роутер для вывода списка всех блюд, для определённого подменю."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')

    assert response.status_code == 200


@pytest.mark.asyncio(scope='function')
async def test_get_dish(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
    fixture_new_dish,
):
    """Тестируем роутер для вывода определённого блюда."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    dish_id = fixture_new_dish['id']
    response = await async_client.get(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
    )

    assert response.status_code == 200

    dish = response.json()
    assert dish['id'] == dish_id
    assert dish['title'] == 'Новое блюдо 1'


@pytest.mark.asyncio(scope='function')
async def test_error_get_dish(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
):
    """Тестируем получение ошибки при выводе определённого блюда с несуществующим «id»."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.get(
        (f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes'
         '/497f6eca-6276-4993-bfeb-53cbbbba6f08')
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'dish not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_dish(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu,
    fixture_new_dish,
):
    """Тестируем роутер для обновления информации о блюде."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    dish_id = fixture_new_dish['id']
    response = await async_client.patch(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
        json={
            'title': 'update title dish',
            'description': 'update description dish',
            'price': 220.11
        }
    )

    assert response.status_code == 200

    dish = response.json()
    assert dish['id'] == dish_id
    assert dish['title'] == 'update title dish'
    assert dish['description'] == 'update description dish'
    assert dish['price'] == '220.11'


@pytest.mark.asyncio(scope='function')
async def test_delete_dish(async_client: AsyncClient, fixture_new_menu, fixture_new_submenu):
    """Тестируем роутер для удаления блюда.

    Сначала мы создаём новое блюдо, что-бы не удалять фикстуру.
    """

    # Создаем блюдо
    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response_dish = await async_client.post(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
        json={
            'title': 'title dish for test delete dish',
            'description': 'description dish for test delete dish',
            'price': 100.11
        }
    )
    assert response_dish.status_code == 201
    dish_id = response_dish.json()['id']

    # Удаляем блюдо
    response = await async_client.delete(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    )

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The dish has been deleted'}


# ==============================================================================
# ==============================================================================
#                           --- Tests for Submenu ---
# ==============================================================================
# ==============================================================================
@pytest.mark.asyncio(scope='function')
async def test_error_new_submenu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем получение ошибки при создании подменю с существующим названием."""

    menu_id = fixture_new_menu['id']
    response = await async_client.post(f'/api/v1/menus/{menu_id}/submenus', json={
        'title': 'Новое подменю 1',
        'description': 'Описание нового подменю 2'
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое подменю уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_submenus(async_client: AsyncClient, fixture_new_menu):
    """Тестируем вывод списка со всеми подменю, для определённого меню."""

    menu_id = fixture_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus')

    assert response.status_code == 200


@pytest.mark.asyncio(scope='function')
async def test_get_submenu(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu
):
    """Тестируем вывод определённого подменю."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

    assert response.status_code == 200

    submenu = response.json()
    assert submenu['id'] == submenu_id
    assert submenu['title'] == 'Новое подменю 1'


@pytest.mark.asyncio(scope='function')
async def test_error_get_submenu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем получение ошибки при выводе определённого подменю с несуществующим «id»."""

    menu_id = fixture_new_menu['id']
    response = await async_client.get(
        f'/api/v1/menus/{menu_id}/submenus/497f6eca-6276-4993-bfeb-53cbbbba6f08',
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'submenu not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_submenu(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu
):
    """Тестируем роутер для обновления информации о подменю."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.patch(
        f'/api/v1/menus/{menu_id}/submenus/{submenu_id}',
        json={
            'title': 'update title submenu',
            'description': 'update description submenu'
        }
    )

    assert response.status_code == 200

    submenu = response.json()
    assert submenu['id'] == submenu_id
    assert submenu['title'] == 'update title submenu'
    assert submenu['description'] == 'update description submenu'


@pytest.mark.asyncio(scope='function')
async def test_delete_submenu(
    async_client: AsyncClient,
    fixture_new_menu,
    fixture_new_submenu
):
    """Тестируем роутер для удаления подменю."""

    menu_id = fixture_new_menu['id']
    submenu_id = fixture_new_submenu['id']
    response = await async_client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The submenu has been deleted'}


# ==============================================================================
# ==============================================================================
#                           --- Tests for Menu ---
# ==============================================================================
# ==============================================================================
@pytest.mark.asyncio(scope='function')
async def test_error_new_menu(async_client: AsyncClient):
    """Тестируем получение ошибки при создании меню с существующим названием."""

    response = await async_client.post('/api/v1/menus', json={
        'title': 'Новое меню 1',
        'description': 'Описание нового меню 2'
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое меню уже зарегестрировано.'}


@pytest.mark.asyncio(scope='function')
async def test_all_menus(async_client: AsyncClient):
    """Тестируем роутер для вывода списка со всеми меню."""

    response = await async_client.get('/api/v1/menus')

    assert response.status_code == 200


@pytest.mark.asyncio(scope='function')
async def test_get_menu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем роутер для вывода определённого меню по его «id»."""

    menu_id = fixture_new_menu['id']
    response = await async_client.get(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200

    menu = response.json()
    assert menu['id'] == menu_id
    assert menu['title'] == 'Новое меню 1'


@pytest.mark.asyncio(scope='function')
async def test_error_get_menu(async_client: AsyncClient):
    """Тестируем получение ошибки при выводе определённого меню с несуществующим «id»."""

    response = await async_client.get('/api/v1/menus/497f6eca-6276-4993-bfeb-53cbbbba6f08')

    assert response.status_code == 404
    assert response.json() == {'detail': 'menu not found'}


@pytest.mark.asyncio(scope='function')
async def test_update_menu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем роутер для обновления информации о меню."""

    menu_id = fixture_new_menu['id']
    response = await async_client.patch(f'/api/v1/menus/{menu_id}', json={
        'title': 'update title menu',
        'description': 'update description menu'
    })

    assert response.status_code == 200

    menu = response.json()
    assert menu['id'] == menu_id
    assert menu['title'] == 'update title menu'
    assert menu['description'] == 'update description menu'


@pytest.mark.asyncio(scope='function')
async def test_delete_menu(async_client: AsyncClient, fixture_new_menu):
    """Тестируем роутер для удаления меню."""

    menu_id = fixture_new_menu['id']
    response = await async_client.delete(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200
    assert response.json() == {'status': True, 'message': 'The menu has been deleted'}
