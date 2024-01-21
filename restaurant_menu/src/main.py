from fastapi import FastAPI
from src.menu.routers import menu_router

app = FastAPI(title='Restaurant Menu API', description='REST API по работе с меню ресторана.')

app.include_router(menu_router)
