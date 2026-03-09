# LiftJournal — Backend

REST API для приложения дневника тренировок. Построен на **FastAPI** + **SQLAlchemy (async)** + **PostgreSQL**.

## Стек

| Слой | Технология |
|---|---|
| Framework | FastAPI 0.135 |
| ORM | SQLAlchemy 2.0 (asyncio) |
| БД | PostgreSQL (драйвер asyncpg) |
| Валидация | Pydantic 2 |
| Миграции | Alembic |
| Аутентификация | JWT (python-jose) + bcrypt |
| Зависимости | Poetry |
| Тесты | pytest + pytest-asyncio |
| Безопасность | Bandit |

## Архитектура

Луковая архитектура с паттерном Repository:

```
app/
├── api/
│   ├── routers/       # тонкие HTTP-обработчики (только парсинг запроса → сервис → ответ)
│   └── schemas.py     # Pydantic DTO (request / response)
├── services/          # бизнес-логика, оркестрация репозиториев
├── repositories/      # чистый доступ к БД через SQLAlchemy
├── domain/
│   └── models.py      # ORM-модели (SQLAlchemy)
└── core/
    ├── database.py    # engine, session, get_db dependency
    └── security.py    # JWT, bcrypt, get_current_user dependency
```

**Поток данных:**
```
HTTP Request → Router → Service → Repository → DB
                             ↓
HTTP Response ← DTO  ← Service ←────────────────
```

## Быстрый старт

### Требования

- Python 3.13+
- PostgreSQL
- Poetry

### Установка

```bash
# Клонировать репозиторий и перейти в backend/
cd backend

# Установить зависимости
poetry install

# Создать .env из примера
cp .env.example .env  # заполнить DATABASE_URL и SECRET_KEY
```

### Переменные окружения

Файл `.env` в корне `backend/`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gym
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### Миграции

```bash
# Применить все миграции
poetry run alembic upgrade head

# Создать новую миграцию
poetry run alembic revision --autogenerate -m "describe change"

# Откатить последнюю миграцию
poetry run alembic downgrade -1
```

### Запуск

```bash
# Режим разработки (с hot-reload)
poetry run uvicorn main:app --reload

# API доступен на http://localhost:8000
# Документация: http://localhost:8000/docs
```

## Запуск через Docker

```bash
docker build -t gym-backend .
docker run -p 8000:8000 --env-file .env gym-backend
```

## Тесты

```bash
# Запустить все тесты
poetry run pytest

# С подробным выводом
poetry run pytest -v

# Конкретный модуль
poetry run pytest tests/test_services/test_auth_service.py
```

Тесты — **чистые unit-тесты без обращений к БД**. Все зависимости (сессия, репозитории, сервисы) мокируются через `unittest.mock`.

```
tests/
├── conftest.py                  # фабрики мок-объектов
├── test_core/                   # тесты security (JWT, bcrypt)
├── test_services/               # тесты бизнес-логики
├── test_repositories/           # тесты слоя доступа к данным
└── test_api/                    # тесты HTTP-эндпоинтов (httpx AsyncClient)
```

## Проверка безопасности

```bash
# Сканирование кода на уязвимости (Bandit)
poetry run bandit -r app/ -c pyproject.toml
```

Конфигурация в `pyproject.toml` (`[tool.bandit]`): сканируется только `app/`, порог — medium severity/confidence.

## API

Полная документация доступна в Swagger UI после запуска: `http://localhost:8000/docs`

### Эндпоинты

| Метод | URL | Описание | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Регистрация | — |
| POST | `/api/auth/login` | Вход, получение JWT | — |
| GET | `/api/user` | Профиль пользователя | ✓ |
| PATCH | `/api/user/profile` | Обновление профиля | ✓ |
| POST | `/api/user/weight` | Записать вес | ✓ |
| DELETE | `/api/user/weight/{date}` | Удалить запись веса | ✓ |
| POST | `/api/user/goals` | Создать цель | ✓ |
| PATCH | `/api/user/goals/{id}/toggle` | Отметить цель выполненной | ✓ |
| DELETE | `/api/user/goals/{id}` | Удалить цель | ✓ |
| POST | `/api/user/maxes` | Сохранить личный максимум (ПМ) | ✓ |
| DELETE | `/api/user/maxes/{exercise}` | Удалить ПМ | ✓ |
| GET | `/api/exercises` | Список упражнений | — |
| POST | `/api/exercises` | Создать пользовательское упражнение | — |
| GET | `/api/workouts` | Список тренировок | ✓ |
| POST | `/api/workouts` | Создать тренировку | ✓ |
| GET | `/api/workouts/{id}` | Детали тренировки | ✓ |
| PATCH | `/api/workouts/{id}` | Обновить тренировку | ✓ |
| DELETE | `/api/workouts/{id}` | Удалить тренировку | ✓ |
| GET | `/api/cycles` | Список циклов (публичные + свои) | ✓ |
| POST | `/api/cycles` | Создать цикл | ✓ |
| GET | `/api/cycles/{id}` | Детали цикла | ✓ |
| PATCH | `/api/cycles/{id}` | Обновить цикл | ✓ |
| DELETE | `/api/cycles/{id}` | Удалить цикл | ✓ |
| POST | `/api/cycles/{id}/start` | Начать прохождение цикла | ✓ |
| GET | `/api/cycles/{id}/run` | Текущий активный прогон цикла | ✓ |
| POST | `/api/cycle-runs/{run_id}/workouts/{wid}/start` | Начать тренировку из цикла | ✓ |
| POST | `/api/cycle-runs/{run_id}/workouts/{wid}/complete` | Завершить тренировку цикла | ✓ |
| POST | `/api/cycle-runs/{run_id}/finish` | Завершить прогон цикла | ✓ |
| GET | `/api/health` | Health check | — |

## Миграции БД

| № | Файл | Описание |
|---|---|---|
| 001 | `001_initial.py` | Базовые таблицы: users, exercises, workouts |
| 002 | `002_auth.py` | Email + hashed_password для пользователей |
| 003 | `003_cycles.py` | Таблицы тренировочных циклов |
| 004 | `004_cycle_runs.py` | Прогоны циклов и логи тренировок |
| 005 | `005_cycle_exercise_id.py` | FK exercise_id в cycle_exercises |
| 006 | `006_cycle_run_completed_at.py` | Поле completed_at в user_cycle_runs |
