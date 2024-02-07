from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src import models, schemas
from src.database import get_db
from src.menus import crud

menu_router = APIRouter()


@menu_router.post('/api/v1/menus', response_model=schemas.DetailedMenuInfoPyd, status_code=201,
                  summary='Создать меню', tags=['Меню'])
async def new_menu(
    menu: schemas.BaseMenuPyd,
    db: AsyncSession = Depends(get_db),
) -> models.Menu:
    """Создаём новое меню."""

    menu_data: Dict[str, str] = menu.model_dump()

    return await crud.create_menu(db=db, **menu_data)


@menu_router.get('/api/v1/menus', response_model=List[schemas.DetailedMenuInfoPyd],
                 summary='Список меню', tags=['Меню'])
async def all_menus(db: AsyncSession = Depends(get_db)) -> List[Optional[models.Menu]]:
    """Выводим список со всеми меню."""

    return await crud.get_all_menus(db=db)


@menu_router.get('/api/v1/menus/{menu_id}', response_model=schemas.DetailedMenuInfoPyd,
                 summary='Определённое меню', tags=['Меню'])
async def get_menu(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> schemas.DetailedMenuInfoPyd:
    """Выводим определённое меню по его «id»."""

    menu, submenus_count, dishes_count = await crud.get_counts_submenus_and_dishes_from_menu(
        db=db,
        menu_id=menu_id,
    )

    menu_info = schemas.SmallMenuInfoPyd.model_validate({**menu.__dict__})

    return schemas.DetailedMenuInfoPyd.model_validate(
        {
            **menu_info.model_dump(),
            **{'submenus_count': submenus_count, 'dishes_count': dishes_count}
        })


@menu_router.patch('/api/v1/menus/{menu_id}', response_model=schemas.DetailedMenuInfoPyd,
                   summary='Обновить меню', tags=['Меню'])
async def update_menu(
    update_data: schemas.UpdateMenuPyd,
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> models.Menu:
    """Обновляем информацию о меню."""

    menu: Optional[models.Menu] = await crud.get_menu_by_id(db=db, menu_id=menu_id)

    updated_menu: models.Menu = await crud.update_menu_by_id(
        db=db, menu=menu, **update_data.model_dump()
    )

    return updated_menu


@menu_router.delete('/api/v1/menus/{menu_id}',
                    response_model=schemas.DeleteObjPyd,
                    summary='Удалить меню', tags=['Меню'])
async def delete_menu(
    menu_id: UUID = Path(..., description='id меню'),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Union[bool, str]]:
    """Удалаяем меню."""

    # Получаем объект меню, и проверяем его.
    await crud.get_menu_by_id(db=db, menu_id=menu_id)

    await crud.delete_menu_by_id(db=db, menu_id=menu_id)
    return {"status": True, "message": "The menu has been deleted"}
