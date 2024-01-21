"""SQLAlchemy models."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class Menu(Base):
    """Таблица SQLAlchemy «Меню»."""

    __tablename__ = 'menus'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=False)
    submenus_count = Column(Integer, default=0)
    dishes_count = Column(Integer, default=0)

    # Связь с таблицей SubMenu
    submenus = relationship('SubMenu', back_populates='menus', lazy='selectin')


class SubMenu(Base):
    """Таблица SQLAlchemy «Подменю»."""

    __tablename__ = 'submenus'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    menu_id = Column(
        UUID(as_uuid=True), ForeignKey('menus.id', ondelete='CASCADE'), nullable=False,
        comment='Внешний ключ, связывающий подменю с родительским меню (таблица «Menu»).'
    )
    title = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=False)
    dishes_count = Column(Integer, default=0)

    # Связь с таблицами «Menu» и «Dish»
    menus = relationship('Menu', back_populates='submenus', lazy='selectin')
    dishes = relationship('Dish', back_populates='submenus', lazy='selectin')


class Dish(Base):
    """Таблица SQLAlchemy «Блюда»."""

    __tablename__ = 'dishes'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    submenu_id = Column(
        UUID(as_uuid=True), ForeignKey('submenus.id', ondelete='CASCADE'), nullable=False,
        comment='Внешний ключ, связывающий блюдо с подменю (таблица «SubMenu»).'
    )
    title = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # Связь с таблицей SubMenu
    submenus = relationship('SubMenu', back_populates='dishes', lazy='selectin')
