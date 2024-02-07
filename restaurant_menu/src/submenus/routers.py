from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src import models, schemas
from src.database import get_db
from src.submenus import crud

submenu_router = APIRouter()


@submenu_router.post('/api/v1/menus/{menu_id}/submenus',
                     response_model=schemas.DetailedSubmenuInfoPyd,
                     status_code=201, summary='Создать подменю', tags=['Подменю'])
async def new_submenu(
    submenu: schemas.BaseMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> models.SubMenu:
    """Создаём новое подменю, для определённого меню."""

    submenu_data: Dict[str, str] = submenu.model_dump()
    return await crud.create_submenu(db=db, menu_id=menu_id, **submenu_data)


@submenu_router.get('/api/v1/menus/{menu_id}/submenus',
                    response_model=List[schemas.DetailedSubmenuInfoPyd],
                    summary='Список подменю', tags=['Подменю'])
async def all_submenus(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> List[Optional[models.SubMenu]]:
    """Выводим список со всеми подменю, для определённого меню."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(db=db, menu_id=menu_id)

    return menu.submenus


@submenu_router.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                    response_model=schemas.DetailedSubmenuInfoPyd,
                    summary='Определённое подменю', tags=['Подменю'])
async def get_submenu(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> Optional[models.SubMenu]:
    """Выводим определённое подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    return submenu


@submenu_router.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                      response_model=schemas.DetailedSubmenuInfoPyd,
                      summary='Обновить подменю', tags=['Подменю'])
async def update_submenu(
    update_data: schemas.UpdateMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> models.SubMenu:
    """Обновляем информацию о подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    updated_submenu: models.SubMenu = await crud.update_submenu_by_id(
        db=db, submenu=submenu, **update_data.model_dump()
    )

    return updated_submenu


@submenu_router.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}',
                       response_model=schemas.DeleteObjPyd,
                       summary='Удалить подменю', tags=['Подменю'])
async def delete_submenu(
    menu_id: UUID = Path(..., description='id меню'),
    submenu_id: UUID = Path(..., description='id подменю'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем подменю."""

    submenu: Optional[models.SubMenu] = await crud.get_submenu_by_id(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )

    await crud.delete_submenu_by_id(
        db=db, submenu=submenu, menu_id=menu_id, submenu_id=submenu_id
    )

    return {"status": True, "message": "The submenu has been deleted"}
