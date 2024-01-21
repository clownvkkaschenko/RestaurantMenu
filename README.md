<div id="header" align="center">
  <h1>Restaurant Menu API</h1>
  <img src="https://img.shields.io/badge/Python-3.10.11-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-F8F8FF?style=for-the-badge&logo=FastAPI&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/PostgreSQL-555555?style=for-the-badge&logo=postgresql&logoColor=F5F5DC">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.25-F8F8FF?style=for-the-badge&logo=SQLAlchemy&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/Docker-555555?style=for-the-badge&logo=docker&logoColor=2496ED">
</div>


# Документация API
Restaurant Menu - **[API redoc](https://clownvkkaschenko.github.io/RestaurantMenuAPI/)**

<details><summary><h1>Запуск проекта без докера</h1></summary>

- Клонируйте репозиторий и перейдите в него.
- Установите и активируйте виртуальное окружение(venv).
- Создайте файл **.env**, с переменными окружения.
    ```
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    ```
- Перейдите в папку **restaurant_menu**. Установите зависимости из файла requirements.txt
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ``` 
- Выполните миграции.
  ```
  alembic upgrade head
  ```
- Запустите сервер:
  ```
  uvicorn src.main:app --reload
  ```
- Документация к API будет доступна по url-адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

</details>

<details><summary><h1>Запуск проекта через докер</h1></summary>

- Клонируйте репозиторий и перейдите в него.
- Перейдите в папку **infra**. Создайте файл **.env**, с переменными окружения.
    ```
  DB_HOST=db
  DB_PORT=5432
  DB_NAME=postgres
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres
    ``` 
- Находясь в папке **infra** запустите docker-compose:
  ```
  ~$ docker-compose up -d --build
  ```
- В контейнере **backend** выполните миграции:
  ```
  ~$ docker-compose exec backend alembic upgrade head
  ```

Документация к API будет доступна по url-адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

</details>

# ТЗ проекта
Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции.

Даны 3 сущности: Меню, Подменю, Блюдо.

Зависимости:

- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

Условия:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.
