# Проект YaMDb
### Описание
- Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором. Пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведениям оценки. Реализован REST API для основных моделей проекта, а также система регистрации и аутентификации пользователей. Для аутентификации используются JWT-токены. 
### Технологии
- Python 3.7
- Django 2.2.16
- Django Rest Framework 3.12.4
- Pytest 6.2.4
- PyJWT 2.1.0
- Django-filter 22.1
- Python-dotenv 0.20.0
- gunicorn==20.0.4
- psycopg2-binary==2.8.6
### Шаблон заполнения .env
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- DB_HOST=db
- DB_PORT=1111

### Бейдж

https://github.com/mihailkasev/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg

### Запуск проекта 
- Клонируйте репозиторий:
```
git clone https://github.com/mihailkasev/yamdb_final.git
```
- Собрать и запустить контейнеры:
```
docker-compose up -d
```
- Запустить миграции:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
- Создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
- Собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```
### Автор:
- Михаил Касев