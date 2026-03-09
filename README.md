# LiftJournal

Дневник тренировок с поддержкой тренировочных циклов, отслеживанием прогресса и расчётом рабочих весов по % от ПМ.

## Структура монорепозитория

```
gym/
├── backend/      # FastAPI REST API
├── ui/           # Vue 3 SPA
└── docker-compose.yml
```

## Стек

| | Технология |
|---|---|
| **Frontend** | Vue 3 (Composition API) · Vuex 4 · Vue Router 4 · Tailwind CSS 3 · Chart.js |
| **Backend** | FastAPI · SQLAlchemy 2.0 async · PostgreSQL · Alembic · JWT |
| **Инфраструктура** | Docker · Docker Compose · Poetry |

## Функциональность

- **Тренировки** — создание, редактирование, история, фильтрация по типу и дате
- **Упражнения** — библиотека с фильтрацией по группе мышц и оборудованию, пользовательские упражнения, прогресс и PR
- **Тренировочные циклы** — создание программ с % от ПМ, запуск/завершение цикла, отслеживание прогресса
- **Профиль** — дневник веса, цели, личные максимумы (1RM) для расчёта весов в циклах
- **Аутентификация** — регистрация и вход по JWT

---

## Быстрый старт (Docker Compose)

Самый простой способ поднять всё сразу:

```bash
git clone <repo>
cd gym

# Создать .env для бэкенда
cp backend/.env.example backend/.env

# Запустить PostgreSQL + API (с автомиграциями и seed-данными)
docker compose up --build
```

| Сервис | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

Frontend запускается отдельно (см. ниже) — в dev-режиме он проксирует запросы к `localhost:8000`.

---

## Разработка

### Backend

**Требования:** Python 3.13+, Poetry, PostgreSQL

```bash
cd backend

# Установить зависимости
poetry install

# Настроить окружение
cp .env.example .env   # заполнить DATABASE_URL и SECRET_KEY

# Применить миграции
poetry run alembic upgrade head

# Запустить API
poetry run uvicorn main:app --reload
# → http://localhost:8000
```

**Тесты и проверка безопасности:**

```bash
poetry run pytest                              # 239 unit-тестов, без обращений к БД
poetry run bandit -r app/ -c pyproject.toml   # статический анализ уязвимостей
```

### Frontend

**Требования:** Node.js 18+

```bash
cd ui

npm install
npm run dev
# → http://localhost:5173
```

**Сборка для продакшна:**

```bash
npm run build    # dist/
npm run preview  # превью сборки
```

---

## Архитектура

### Backend — луковая архитектура

```
backend/app/
├── api/
│   ├── routers/       # HTTP-обработчики (тонкий слой: запрос → сервис → ответ)
│   └── schemas.py     # Pydantic DTO
├── services/          # бизнес-логика
├── repositories/      # доступ к БД (SQLAlchemy)
├── domain/
│   └── models.py      # ORM-модели
└── core/
    ├── database.py    # подключение, get_db
    └── security.py    # JWT, bcrypt, get_current_user
```

### Frontend — Vuex + Vue Router

```
ui/src/
├── views/             # страницы (по одной на роут)
├── components/
│   ├── ui/            # базовые компоненты (BaseButton, BaseModal …)
│   ├── layout/        # AppSidebar, AppTopbar, AppBottomNav
│   ├── workout/
│   ├── exercises/
│   └── profile/
├── store/modules/     # auth · workouts · exercises · cycles · user · ui
├── services/
│   └── workoutService.js   # единая точка обмена с API
└── router/
```

**Поток данных:**
```
workoutService.js → Vuex actions → Vuex state → компоненты
```
При добавлении нового API-метода достаточно изменить только `workoutService.js`.

### Роуты

| Путь | Вид |
|---|---|
| `/login`, `/register` | Аутентификация |
| `/history` | История тренировок |
| `/workouts/new` | Создание тренировки (3 шага) |
| `/workouts/:id` | Детали тренировки |
| `/exercises` | Библиотека упражнений |
| `/exercises/:id` | Прогресс по упражнению |
| `/cycles` | Список тренировочных циклов |
| `/cycles/:id` | Детали цикла (список / таблица) |
| `/cycles/:id/edit` | Редактор цикла |
| `/profile` | Профиль, вес, цели, ПМ |

---

## Переменные окружения

Файл `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://gym:gym@localhost:5432/gym
SECRET_KEY=your-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

---

## Миграции

```bash
cd backend

poetry run alembic upgrade head        # применить все
poetry run alembic downgrade -1        # откатить последнюю
poetry run alembic revision --autogenerate -m "описание"  # создать новую
```

| Миграция | Изменение |
|---|---|
| 001 | Базовые таблицы: users, exercises, workouts |
| 002 | Аутентификация: email + hashed_password |
| 003 | Тренировочные циклы |
| 004 | Прогоны циклов и логи |
| 005 | Связь упражнений цикла с библиотекой (exercise_id FK) |
| 006 | Поле completed_at в user_cycle_runs |
