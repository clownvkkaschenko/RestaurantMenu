import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.configs import (DB_HOST_TEST, DB_NAME, DB_PORT, POSTGRES_PASSWORD,
                         POSTGRES_USER)
from src.database import Base
from src.main import app

DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
    f'{DB_HOST_TEST}:{DB_PORT}/{DB_NAME}'
)

async_engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    async_engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)
Base.bind = async_engine_test


@pytest.fixture(scope='function')
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
def fixture_new_menu():
    """Фикстура для меню."""

    return {}


@pytest.fixture(scope='session')
def fixture_new_submenu():
    """Фикстура для подменю."""

    return {}


@pytest.fixture(scope='session')
def fixture_new_dish():
    """Фикстура для нового блюда."""

    return {}


# Сразу создаём меню и подменю, для возможности создать зависимые от них объекты.
# @pytest.fixture(scope='session')
# async def fixture_create_menu(override_get_db):
#     """Фикстура с меню, для тестирования."""

#     stmt = insert(models.Menu).values(
#         title='Тестовое меню 1',
#         description='Описание тестового меню 1'
#     )

#     await override_get_db.execute(stmt)
#     await override_get_db.commit()

#     query = (
#         select(models.Menu).
#         order_by(models.Menu.id.desc()).limit(1)
#     )
#     result = await override_get_db.execute(query)
#     result = result.scalars().one_or_none()
#     assert result is not None, 'Меню не добавилось.'

#     return result


# @pytest.fixture(scope='session')
# async def fixture_create_submenu(override_get_db, fixture_create_menu):
#     """Фикстура с подменю, для тестирования."""

#     stmt = insert(models.SubMenu).values(
#         menu_id=fixture_create_menu.id,
#         title='Тестовое подменю 1',
#         description='Описание тестового подменю 1'
#     )

#     await override_get_db.execute(stmt)
#     await override_get_db.commit()

#     query = (
#         select(models.SubMenu).
#         order_by(models.SubMenu.id.desc()).limit(1)
#     )
#     result = await override_get_db.execute(query)
#     result = result.scalars().one_or_none()
#     assert result is not None, 'Подменю не добавилось.'

#     return result
