# BookFlow

Серверное приложение для управления личной библиотекой и онлайн-чтения книг.

## Описание

BookFlow - это REST API приложение, построенное на FastAPI, которое позволяет:

- Управлять личной библиотекой книг (публичные и приватные)
- Добавлять книги по ISBN без загрузки PDF (метаданные из Google Books)
- Отслеживать статусы книг (запланировано, читаю, прочитано)
- Читать PDF-книги онлайн (streaming)
- Отслеживать прогресс чтения по страницам
- Устанавливать цели чтения и отслеживать streak (серии дней)
- Интегрироваться с Google Books API для поиска и получения метаданных книг
- Публиковать события через RabbitMQ

## Архитектура

Проект построен на основе **Clean Architecture (Layered)**:

```
app/
├── api/              # FastAPI routers
├── application/      # UseCases / Services 
├── domain/           # Entities / Value Objects
├── infrastructure/  # DB / Storage / External APIs / MQ
└── tests/           # Тесты
```

### Модули

1. **users** - Пользователи и авторизация (JWT)
2. **books** - Управление книгами (публичные/приватные)
3. **reading** - Прогресс чтения и привычки
4. **integrations** - Google Books API

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Запуск через Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd bookflow
```

2. Запустите все сервисы:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

### Доступ к сервисам

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 
- **MinIO Console**: http://localhost:9001 

## API Endpoints

### Пользователи

- `POST /api/v1/users/register` - Регистрация
- `POST /api/v1/users/login` - Авторизация
- `GET /api/v1/users/me` - Получить текущего пользователя

### Книги

- `GET /api/v1/books/public` - Получить публичные книги
- `POST /api/v1/books/private` - Загрузить приватную книгу (автоматически добавляется в библиотеку)
- `GET /api/v1/books/{book_id}/read` - Читать книгу (PDF stream)
- `DELETE /api/v1/books/{book_id}` - Удалить приватную книгу

### Библиотека пользователя

- `GET /api/v1/users/me/library` - Получить библиотеку пользователя (с фильтром по статусу)
- `POST /api/v1/users/me/library/isbn` - Добавить книгу в библиотеку по ISBN (без PDF)
- `POST /api/v1/users/me/library/public` - Добавить публичную книгу в библиотеку
- `PUT /api/v1/users/me/library/{book_id}/status` - Изменить статус книги в библиотеке
- `DELETE /api/v1/users/me/library/{book_id}` - Удалить книгу из библиотеки

**Статусы книг:**
- `planned` - Запланировано к прочтению
- `reading` - Читаю
- `finished` - Прочитано

### Прогресс чтения

- `PUT /api/v1/reading/progress/{book_id}` - Обновить прогресс
- `GET /api/v1/reading/progress/{book_id}` - Получить прогресс
- `GET /api/v1/reading/habit` - Получить привычку чтения
- `PUT /api/v1/reading/habit` - Обновить цель чтения
- `GET /api/v1/reading/stats` - Получить статистику

### Интеграции

- `GET /api/v1/integrations/google-books/search?query=...` - Поиск книг
- `GET /api/v1/integrations/google-books/isbn/{isbn}` - Получить книгу по ISBN

## Тестирование

Запуск тестов:

```bash
pytest
```

С покрытием:

```bash
pytest --cov=app --cov-report=html
```

Требуемое покрытие: ≥30%

## База данных

Используется PostgreSQL. Миграции выполняются автоматически при запуске через Alembic.

### Таблицы

- `users` - Пользователи
- `books` - Книги (публичные и приватные, с поддержкой ISBN)
- `user_books` - Библиотека пользователя (статусы: planned, reading, finished)
- `reading_progress` - Прогресс чтения по страницам
- `reading_habits` - Привычки чтения (цели и streak)

## Конфигурация

Все настройки вынесены в переменные окружения.

Основные параметры:

- `DATABASE_URL` - URL подключения к PostgreSQL
- `SECRET_KEY` - Секретный ключ для JWT
- `MINIO_ENDPOINT` - Endpoint MinIO
- `RABBITMQ_URL` - URL подключения к RabbitMQ
- `GOOGLE_BOOKS_API_URL` - URL Google Books API

## Технологии

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Миграции БД
- **PostgreSQL** - База данных
- **MinIO** - Хранилище файлов (S3-compatible)
- **RabbitMQ** - Брокер сообщений
- **JWT** - Авторизация
- **pytest** - Тестирование



