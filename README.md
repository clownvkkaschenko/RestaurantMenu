<div id="header" align="center">
  <h1>Restaurant Menu API</h1>
  <img src="https://img.shields.io/badge/Python-3.10.11-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-F8F8FF?style=for-the-badge&logo=FastAPI&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/PostgreSQL-555555?style=for-the-badge&logo=postgresql&logoColor=F5F5DC">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.25-F8F8FF?style=for-the-badge&logo=SQLAlchemy&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/Docker-555555?style=for-the-badge&logo=docker&logoColor=2496ED">
  <img src="https://img.shields.io/badge/Pytest-555555?style=for-the-badge&logo=pytest&logoColor=0A9EDC">
</div>

# Документация API:
Restaurant Menu - **[API redoc](https://clownvkkaschenko.github.io/RestaurantMenuAPI/)**

# Запуск проекта через докер:

- Клонируйте репозиторий и перейдите в него.
- Перейдите в папку **infra**. Создайте файл **.env**, с переменными окружения.
  ```
  DB_HOST=db
  DB_PORT=5432
  DB_NAME=postgres
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres

  # data db for tests
  DB_HOST_TEST=db_for_tests
  ``` 
- Находясь в папке **infra** запустите docker-compose:
  ```
  ~$ docker-compose up -d --build
  ```
- В контейнере **backend** выполните миграции:
  ```
  ~$ docker-compose exec backend alembic upgrade head
  ```
- Для запуска тестов выполните команду: 
  ```
  ~$ docker-compose up tests
  ```

Документация к API будет доступна по url-адресу [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)


# Техническое задание проекта:
Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции.

Даны 3 сущности: Меню, Подменю, Блюдо.

Зависимости:

- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

Условия первого задания:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.

Условия второго задания:
- Написать CRUD тесты для ранее разработанного API с помощью библиотеки pytest.
- Подготовить отдельный контейнер для запуска тестов.
- Реализовать вывод количества подменю и количества блюд для меню через один ORM запрос.
- Реализовать тестовый сценарий «Проверка количества блюд и количества подменю в меню» из тестов Postman с помощью pytest.


