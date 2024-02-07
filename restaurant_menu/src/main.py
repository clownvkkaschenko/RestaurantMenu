from fastapi import FastAPI
from src.dishes.routers import dish_router
from src.menus.routers import menu_router
from src.submenus.routers import submenu_router

app = FastAPI(title='Restaurant Menu API', description='REST API по работе с меню ресторана.')

app.include_router(dish_router)
app.include_router(menu_router)
app.include_router(submenu_router)
