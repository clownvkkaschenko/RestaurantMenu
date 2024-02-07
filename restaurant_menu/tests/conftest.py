from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.configs import (DB_HOST_TEST, DB_NAME, DB_PORT, POSTGRES_PASSWORD,
                         POSTGRES_USER)
from src.database import Base, get_db
from src.main import app

DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
    f'{DB_HOST_TEST}:{DB_PORT}/{DB_NAME}'
)

async_engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)

async_session_maker = sessionmaker(
    async_engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base.bind = async_engine_test


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session', autouse=True)
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
def menu_data():
    return {
        'title': 'Фикстура меню 1',
        'description': 'Описание фикстуры меню 1'}


@pytest.fixture(scope='session')
def submenu_data():
    return {'title': 'Фикстура подменю 1',
            'description': 'Описание фикстуры подменю 1'}


@pytest.fixture(scope='session')
def dish_data():
    return {'title': 'Фикстура блюда 1',
            'description': 'Описание фикстуры блюда 1',
            'price': 111.11}


@pytest.fixture(scope='session')
async def fixture_current_menu():
    """Хранение текущего меню в тестах."""

    return {}


@pytest.fixture(scope='session')
async def fixture_current_submenu():
    """Хранение текущего подменю в тестах."""

    return {}


@pytest.fixture(scope='session')
async def fixture_current_dish():
    """Хранение текущего блюда в тестах."""

    return {}
