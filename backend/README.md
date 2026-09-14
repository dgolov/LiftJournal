# LiftJournal — Backend

REST API + WebSocket для приложения дневника тренировок. Построен на **FastAPI** + **SQLAlchemy (async)** + **PostgreSQL**.

## Стек

| Слой | Технология |
|---|---|
| Framework | FastAPI ^0.135 |
| ORM | SQLAlchemy ^2.0 (asyncio) |
| БД | PostgreSQL (драйвер asyncpg) |
| Валидация | Pydantic ^2.12 |
| Миграции | Alembic ^1.18 |
| Аутентификация | JWT (python-jose) + bcrypt |
| Realtime | WebSocket (`/api/ws`) через встроенный `ws_manager` |
| Зависимости | Poetry |
| Тесты | pytest + pytest-asyncio |
| Безопасность | Bandit |

## Архитектура

Луковая архитектура с паттерном Repository:

```
app/
├── api/
│   ├── routers/       # тонкие HTTP-обработчики (только парсинг запроса → сервис → ответ)
│   │                   auth · workouts · exercises · cycles · cycle_runs · users ·
│   │                   planned_workouts · achievements · social · notifications ·
│   │                   templates · admin
│   └── schemas.py     # Pydantic DTO (request / response)
├── services/          # бизнес-логика, оркестрация репозиториев
├── repositories/      # чистый доступ к БД через SQLAlchemy
├── domain/
│   └── models.py      # ORM-модели (SQLAlchemy)
├── core/
│   ├── database.py    # engine, session, get_db dependency
│   ├── security.py    # JWT, bcrypt, get_current_user dependency
│   └── ws_manager.py  # реестр активных WebSocket-соединений по user_id
└── seed.py             # сид демо-данных (упражнения, демо-пользователи) для dev/Docker
```

**Поток данных (HTTP):**
```
HTTP Request → Router → Service → Repository → DB
                             ↓
HTTP Response ← DTO  ← Service ←────────────────
```

**Realtime:** сервисы (`social`, `notifications`) пушат события через `ws_manager` тому же пользователю, чей клиент подключён к `/api/ws?token=<JWT>` — используется для мгновенных уведомлений о лайках, комментариях, подписках.

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

### Сид демо-данных

```bash
poetry run python -m app.seed
```

Наполняет базу справочником упражнений и демо-пользователями (в т.ч. администратором для `admin/`). В `docker-compose.yml` запускается автоматически при старте контейнера.

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

Продакшн-образ при старте сам выполняет `alembic upgrade head && python -m app.seed` перед запуском `uvicorn` (см. `docker-compose.yml`).

## Тесты

```bash
# Запустить все тесты
poetry run pytest

# С подробным выводом
poetry run pytest -v

# Конкретный модуль
poetry run pytest tests/test_services/test_auth_service.py
```

Тесты — **чистые unit-тесты без обращений к БД**. Все зависимости (сессия, репозитории, сервисы) мокируются через `unittest.mock`. На момент актуализации — 540+ тестов.

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

Полная и всегда актуальная документация — в Swagger UI после запуска: `http://localhost:8000/docs`. Ниже — обзор по ресурсам (Auth ✓ = требует `Authorization: Bearer <JWT>`).

### Аутентификация (`/api/auth`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| POST | `/register` | Регистрация | — |
| POST | `/login` | Вход, получение JWT | — |

### Профиль пользователя (`/api/user`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Профиль пользователя | ✓ |
| PATCH | `/profile` | Обновление профиля | ✓ |
| PATCH | `/password` | Смена пароля | ✓ |
| PATCH | `/theme` | Смена темы оформления | ✓ |
| POST | `/weight` | Записать вес | ✓ |
| DELETE | `/weight/{entry_date}` | Удалить запись веса | ✓ |
| POST | `/goals` | Создать цель | ✓ |
| PATCH | `/goals/{id}/toggle` | Отметить цель выполненной | ✓ |
| DELETE | `/goals/{id}` | Удалить цель | ✓ |
| POST | `/maxes` | Сохранить личный максимум (ПМ) | ✓ |
| DELETE | `/maxes/{exercise_name}` | Удалить ПМ | ✓ |

### Упражнения (`/api/exercises`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Список упражнений | — |
| POST | `` | Создать пользовательское упражнение (на модерацию) | — |

### Тренировки (`/api/workouts`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Список тренировок (фильтры: `from`, `to`, `search`) | ✓ |
| POST | `` | Создать тренировку | ✓ |
| GET | `/{id}` | Детали тренировки | ✓ |
| PATCH | `/{id}` | Обновить тренировку | ✓ |
| DELETE | `/{id}` | Удалить тренировку | ✓ |

### Тренировочные циклы (`/api/cycles`, `/api`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `/cycles` | Список циклов (публичные + свои) | ✓ |
| POST | `/cycles` | Создать цикл | ✓ |
| GET | `/cycles/{id}` | Детали цикла | ✓ |
| PATCH | `/cycles/{id}` | Обновить цикл | ✓ |
| DELETE | `/cycles/{id}` | Удалить цикл | ✓ |
| GET | `/cycle-runs/active` | Активный прогон цикла (любой) | ✓ |
| POST | `/cycles/{id}/start` | Начать прохождение цикла | ✓ |
| GET | `/cycles/{id}/run` | Текущий активный прогон конкретного цикла | ✓ |
| POST | `/cycle-runs/{run_id}/workouts/{wid}/start` | Начать тренировку из цикла | ✓ |
| POST | `/cycle-runs/{run_id}/workouts/{wid}/complete` | Завершить тренировку цикла | ✓ |
| POST | `/cycle-runs/{run_id}/finish` | Завершить прогон цикла | ✓ |

### Планирование (`/api/planned-workouts`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Список запланированных тренировок | ✓ |
| POST | `` | Создать план (в т.ч. повторяющийся) | ✓ |
| PATCH | `/{id}` | Обновить план (пропуск/перенос/статус) | ✓ |
| DELETE | `/{id}` | Удалить план | ✓ |

### Шаблоны тренировок (`/api/templates`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Список шаблонов | ✓ |
| POST | `` | Создать шаблон | ✓ |
| PATCH | `/{id}` | Обновить шаблон | ✓ |
| DELETE | `/{id}` | Удалить шаблон | ✓ |

### Достижения (`/api/achievements`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `` | Список разблокированных достижений | ✓ |
| POST | `/evaluate` | Пересчитать/разблокировать новые достижения | ✓ |

### Социальные функции (`/api/social`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `/users/search` | Поиск пользователей | ✓ |
| GET | `/users/{id}` | Публичный профиль | ✓ |
| POST | `/users/{id}/follow` | Подписаться | ✓ |
| DELETE | `/users/{id}/follow` | Отписаться | ✓ |
| GET | `/users/{id}/workouts` | Тренировки пользователя (фильтры `from`, `to`) | ✓ |
| GET | `/users/{id}/activity` | Тепловая карта активности | ✓ |
| GET | `/users/{id}/maxes` | Публичные личные максимумы | ✓ |
| GET | `/users/{id}/goals` | Публичные цели | ✓ |
| GET | `/users/{id}/achievements` | Публичные достижения | ✓ |
| GET | `/me/followers` | Мои подписчики | ✓ |
| GET | `/me/following` | Мои подписки | ✓ |
| GET | `/feed` | Лента тренировок подписок (`limit`, `offset`) | ✓ |
| GET | `/workouts/{id}` | Тренировка из ленты | ✓ |
| GET | `/workouts/meta` | Лайки/комментарии батчем по списку id | ✓ |
| POST | `/workouts/{id}/like` | Лайк/анлайк тренировки | ✓ |
| GET | `/workouts/{id}/comments` | Комментарии к тренировке | ✓ |
| POST | `/workouts/{id}/comments` | Добавить комментарий | ✓ |
| DELETE | `/workouts/{id}/comments/{comment_id}` | Удалить комментарий | ✓ |

### Уведомления (`/api/notifications`)

| Метод | URL | Описание | Auth |
|---|---|---|---|
| GET | `/unread-count` | Счётчик непрочитанных | ✓ |
| GET | `` | Страница уведомлений (`unread_only`, `page`, `per_page`) | ✓ |
| POST | `/read-all` | Отметить все прочитанными | ✓ |
| PATCH | `/{id}/read` | Отметить одно прочитанным | ✓ |

### WebSocket

| Протокол | URL | Описание |
|---|---|---|
| WS | `/api/ws?token=<JWT>` | Push-уведомления в реальном времени (лайк, комментарий, подписка) |

### Админ-панель (`/api/admin`, требует `is_admin`)

| Метод | URL | Описание |
|---|---|---|
| GET | `/users` | Список пользователей |
| GET | `/stats` | Общая статистика |
| PATCH | `/users/{id}` | Изменить пользователя |
| POST | `/users/{id}/reset-password` | Сбросить пароль |
| GET | `/exercises` | Список упражнений (в т.ч. на модерации) |
| POST | `/exercises` | Создать упражнение |
| POST | `/exercises/{id}/approve` | Одобрить упражнение |
| POST | `/exercises/{id}/revoke` | Отклонить/отозвать упражнение |
| PATCH | `/exercises/{id}` | Изменить упражнение |
| DELETE | `/exercises/{id}` | Удалить (мягко) упражнение |
| DELETE | `/exercises/{id}/permanent` | Удалить упражнение безвозвратно |
| GET | `/cycles` | Список циклов (в т.ч. на модерации) |
| POST | `/cycles/{id}/approve` | Одобрить публичный цикл |
| POST | `/cycles/{id}/revoke` | Отклонить/отозвать цикл |
| DELETE | `/cycles/{id}` | Удалить цикл |

### Прочее

| Метод | URL | Описание | Auth |
|---|---|---|---|
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
| 007 | `007_user_theme.py` | Тема оформления пользователя |
| 008 | `008_planned_workouts.py` | Запланированные тренировки |
| 009 | `009_recurrence.py` | Повторяющиеся планы |
| 010 | `010_exercise_set_failed.py` | Поле failed у подхода |
| 011 | `011_user_achievements.py` | Достижения пользователя |
| 012 | `012_user_birth_date.py` | Дата рождения пользователя |
| 013 | `013_user_follows.py` | Подписки между пользователями |
| 014 | `014_workout_likes_comments.py` | Лайки и комментарии к тренировкам |
| 015 | `015_notifications.py` | Уведомления |
| 016 | `016_workout_templates.py` | Шаблоны тренировок |
| 017 | `017_template_sets.py` | Подходы в шаблонах |
| 018 | `018_user_is_admin.py` | Флаг is_admin |
| 019 | `019_exercise_moderation.py` | Модерация упражнений |
| 020 | `020_exercise_is_private.py` | Приватные упражнения |
| 021 | `021_cycle_moderation.py` | Модерация циклов |
| 022 | `022_exercise_status.py` | Статус упражнения |
| 023 | `023_user_created_at.py` | Дата создания пользователя |
