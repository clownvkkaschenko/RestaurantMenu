"""Pydantic models."""

from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DeleteObjPyd(BaseModel):
    """Pydantic модель для удаления меню/подменю/блюда.

    Fields:
        - status: bool
        - message: str
    """
    status: bool = Field(description='Статус удаления.')
    message: str = Field(description='Сообщение, с описанием результата.')


# --- Pydantic models for Menu or Submenu ---
class BaseMenuPyd(BaseModel):
    """Pydantic модель c базовой информацией о меню/подменю.

    Fields:
        - title: str
        - description: str
    """

    title: str = Field(description='Название меню')
    description: str = Field(description='Описание меню')


class UpdateMenuPyd(BaseModel):
    """Pydantic модель для обновления меню/подменю.

    Fields:
        - title: str | None
        - description: str | None
    """

    title: Optional[str] = Field(None, description='Название меню')
    description: Optional[str] = Field(None, description='Описание меню')


# --- Pydantic models for Menu ---
class DetailedMenuInfoPyd(BaseMenuPyd):
    """Pydantic модель с подробной информацией о меню.

    Fields:
        - id: UUID
        - title: str
        - description: str
        - submenus_count: int
        - dishes_count: int
    """

    id: UUID = Field(description='id меню в БД')
    submenus_count: int = Field(description='Количество подменю')
    dishes_count: int = Field(description='Количество блюд')


class SmallMenuInfoPyd(BaseMenuPyd):
    """Pydantic модель c информацией о меню, без количества блюд и подменю.

    Количество блюд и подменю будем получать с помощью ORM запроса.

    Fields:
        - id: UUID
        - title: str
        - description: str
    """

    id: UUID = Field(description='id меню в БД')


# --- Pydantic models for Submenu ---
class DetailedSubmenuInfoPyd(BaseMenuPyd):
    """Pydantic модель с подробной информацией о подменю.

    Fields:
        - id: UUID
        - title: str
        - description: str
        - dishes_count: int
    """

    id: UUID = Field(description='id подменю в БД')
    dishes_count: int = Field(description='Количество блюд')


# --- Pydantic models for Dish ---
class BaseDishPyd(BaseModel):
    """Pydantic модель c базовой информацией о блюде.

    Fields:
        - title: str
        - description: str
        - price: float
    """

    title: str = Field(description='Название блюда')
    description: str = Field(description='Описание блюда')
    price: float = Field(description='Цена блюда')


class DetailedDishInfoPyd(BaseModel):
    """Pydantic модель с подробной информацией о блюде.

    Fields:
        - id: UUID
        - title: str
        - description: str
        - price: Union[float, str]
    """

    id: UUID = Field(description='id блюда в БД')
    title: str = Field(description='Название блюда')
    description: str = Field(description='Описание блюда')
    price: Union[float, str] = Field(description='Цена блюда')

    @field_validator('price')
    @classmethod
    def check_price(cls, value):
        # Использую тип str, что-бы тесты в postman прошли
        return str(round(value, 2))


class UpdateDishPyd(BaseModel):
    """Pydantic модель для обновления информации о блюде.

    Fields:
        - title: str | None
        - description: str | None
        - price: float | None
    """

    title: Optional[str] = Field(None, description='Название блюда')
    description: Optional[str] = Field(None, description='Описание блюда')
    price: Optional[float] = Field(None, description='Цена блюда')
