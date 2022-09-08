# Проект YaMDb
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка».
# Техническое описание проекта YaMDb
Вам доступен репозиторий api_yamdb, в нём сохранён пустой Django-проект.
К проекту по адресу http://127.0.0.1:8000/redoc/ подключена документация API YaMDb. В ней описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа: пользовательские роли, которым разрешён запрос.
### Шаблон .env - файла
параметр=значение

SECRET_KEY=(str, 'тут значение секретного ключа')
DB_ENGINE=подключение к СУБД (django.db.backends.postgresql)
DB_NAME=имя базы данных (postgres)
POSTGRES_USER=логин для подключения к базе данных (postgres)
POSTGRES_PASSWORD=пароль для подключения к БД (postgres)
DB_HOST=название сервиса (db)
DB_PORT=порт для подключения к БД (5432)

### Как запустить проект:

Клонировать репозиторий с Github.
В терминале перейти в папку infra.
Последовательно выполнить команды:
```
docker-compose up
docker-compose exec web python manage.py makemigrations users
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
Готово!
# Примеры запросов

Регистрация нового пользователя:

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/signup/
   -H 'Content-Type: application/json'
   -d '{"email": "string","username": "string"}'
```
Получение JWT-токена

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/
   -H 'Content-Type: application/json'
   -d '{"username": "string", "confirmation_code":"string"}'
```

# Авторы
Александр Петров,
Сергей Ларин,
Алексей Андреев.