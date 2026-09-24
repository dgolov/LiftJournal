# LiftForge

Дневник тренировок с поддержкой тренировочных циклов, планирования, шаблонов, социальных функций и расчётом рабочих весов по % от ПМ.

## Структура монорепозитория

```
gym/
├── backend/      # FastAPI REST API + WebSocket
├── ui/           # Vue 3 SPA — основное приложение
├── admin/        # Vue 3 SPA — админ-панель (модерация)
└── docker-compose.yml
```

## Стек

| | Технология |
|---|---|
| **Frontend** (`ui/`, `admin/`) | Vue 3 (Composition API) · Vuex 4 · Vue Router 4 · Tailwind CSS 3 · Chart.js |
| **Backend** | FastAPI · SQLAlchemy 2.0 async · PostgreSQL (asyncpg) · Alembic · JWT · WebSocket |
| **Инфраструктура** | Docker · Docker Compose · Poetry |

## Функциональность

- **Тренировки** — создание, редактирование, история (календарь/список), фильтрация, экспорт в CSV/PDF
- **Шаблоны тренировок** — сохранение тренировки как шаблона, применение и редактирование шаблонов
- **Планирование** — план тренировок наперёд, повторяющиеся планы (recurrence), пропуск/перенос, связь с тренировочными циклами
- **Упражнения** — библиотека с фильтрацией по группе мышц и оборудованию, пользовательские упражнения (с модерацией), прогресс и PR
- **Тренировочные циклы** — программы с % от ПМ, запуск/прохождение цикла, публичные циклы с модерацией
- **Социальные функции** — подписки, лента активности (feed), лайки и комментарии к тренировкам, публичные профили пользователей
- **Уведомления** — в реальном времени через WebSocket (лайки, комментарии, подписки), счётчик непрочитанных
- **Достижения** — автоматическая разблокировка по прогрессу (стрики, тоннаж, количество тренировок)
- **Профиль** — дневник веса, цели, личные максимумы (1ПМ), тема оформления
- **Админ-панель** (`admin/`) — отдельное SPA для модерации пользователей, упражнений и циклов
- **Аутентификация** — регистрация, вход по JWT, смена пароля

---

## Быстрый старт (Docker Compose)

Самый простой способ поднять всё сразу:

```bash
git clone <repo>
cd gym

# Создать .env в корне репозитория (креды Postgres + секрет JWT)
cp .env.example .env

docker compose up --build
```

При старте `backend`-контейнер сам применяет миграции (`alembic upgrade head`) и засеивает базу демо-данными (`python -m app.seed`).

| Сервис | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Frontend (`ui/`) | http://localhost:80 |
| Admin (`admin/`) | http://127.0.0.1:8081 (проброшен только на localhost) |
| PostgreSQL | localhost:5432 |

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

# (опционально) засеять демо-данными
poetry run python -m app.seed

# Запустить API
poetry run uvicorn main:app --reload
# → http://localhost:8000
```

**Тесты и проверка безопасности:**

```bash
poetry run pytest                             # 540+ unit-тестов, без обращений к БД
poetry run bandit -r app/ -c pyproject.toml   # статический анализ уязвимостей
```

### Frontend (`ui/`)

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

### Admin (`admin/`)

Отдельное SPA для модерации; требует пользователя с `is_admin = true` (см. `backend/app/repositories/user.py` / seed-данные).

```bash
cd admin

npm install
npm run dev
# → см. вывод vite (обычно другой порт, чем ui/)
```

---

## Архитектура

### Backend — луковая архитектура

```
backend/app/
├── api/
│   ├── routers/       # HTTP-обработчики: auth, workouts, exercises, cycles,
│   │                   cycle_runs, users, planned_workouts, achievements,
│   │                   social, notifications, templates, admin
│   └── schemas.py     # Pydantic DTO
├── services/          # бизнес-логика
├── repositories/      # доступ к БД (SQLAlchemy)
├── domain/
│   └── models.py      # ORM-модели
├── core/
│   ├── database.py    # подключение, get_db
│   ├── security.py    # JWT, bcrypt, get_current_user
│   └── ws_manager.py  # менеджер WebSocket-соединений (уведомления)
└── seed.py             # сид демо-данных для dev/Docker
```

`main.py` также поднимает `/api/ws` — WebSocket-эндпоинт для push-уведомлений (лайки, комментарии, подписки), авторизуется тем же JWT через query-параметр `token`.

### Frontend — Vuex + Vue Router (`ui/`)

```
ui/src/
├── views/             # страницы (по одной на роут)
├── components/
│   ├── ui/            # базовые компоненты (BaseButton, BaseModal …)
│   ├── layout/        # AppSidebar, AppTopbar, AppBottomNav
│   ├── workout/
│   ├── exercises/
│   ├── profile/
│   ├── social/         # лента, публичный профиль, карточки чужих тренировок
│   └── notifications/  # панель и элементы уведомлений
├── store/modules/     # auth · workouts · exercises · cycles · user · ui ·
│                        achievements · notifications · planned · social · templates
├── services/
│   ├── workoutService.js  # единая точка обмена с REST API
│   └── wsClient.js        # клиент WebSocket-уведомлений
└── router/
```

**Поток данных:**
```
workoutService.js → Vuex actions → Vuex state → компоненты
```
При добавлении нового API-метода достаточно изменить только `workoutService.js`.

`admin/` — отдельный, независимый Vue 3 SPA (свой `package.json`, роутер, стор компоненты) со схожим стеком; ходит в тот же backend через `adminService.js`.

### Роуты (`ui/`)

| Путь | Вид |
|---|---|
| `/login`, `/register` | Аутентификация |
| `/dashboard` | Главная (по умолчанию `/`) |
| `/history` | История тренировок (календарь/список, фильтры, экспорт) |
| `/workouts/new` | Создание тренировки (3 шага) |
| `/workouts/:id` | Детали тренировки |
| `/exercises` | Библиотека упражнений |
| `/exercises/:id` | Прогресс по упражнению |
| `/cycles`, `/cycles/new`, `/cycles/:id`, `/cycles/:id/edit` | Тренировочные циклы |
| `/cycle-runs/:runId/workouts/:cycleWorkoutId` | Выполнение тренировки внутри прогона цикла |
| `/planning`, `/planning/new`, `/planning/:id`, `/planning/:id/edit` | Планирование тренировок |
| `/templates`, `/templates/new`, `/templates/:id` | Шаблоны тренировок |
| `/profile` | Профиль, вес, цели, ПМ |
| `/feed` | Лента активности подписок |
| `/users/:id` | Публичный профиль пользователя (календарь/список его тренировок) |
| `/about` | О приложении, подсказки, достижения, история версий |

---

## Переменные окружения

Есть два независимых набора — для Docker Compose и для локальной разработки backend.

**`.env` в корне репозитория** (использует `docker-compose.yml`):

```env
POSTGRES_USER=gym
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=gym

SECRET_KEY=change_me_minimum_32_chars_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

**`backend/.env`** (для `poetry run uvicorn` без Docker):

```env
DATABASE_URL=postgresql+asyncpg://gym:gym@localhost:5432/gym
SECRET_KEY=your-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

**`ui/.env`** и **`admin/.env`** — указывают, куда ходить за API:

```env
VITE_API_URL=http://localhost:8000/api
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
| 007 | Тема оформления пользователя |
| 008 | Запланированные тренировки (planned_workouts) |
| 009 | Повторяющиеся планы (recurrence) |
| 010 | Поле failed у подхода упражнения |
| 011 | Достижения пользователя |
| 012 | Дата рождения пользователя |
| 013 | Подписки между пользователями (user_follows) |
| 014 | Лайки и комментарии к тренировкам |
| 015 | Уведомления |
| 016 | Шаблоны тренировок |
| 017 | Подходы в шаблонах |
| 018 | Флаг is_admin у пользователя |
| 019 | Модерация упражнений |
| 020 | Приватные упражнения (is_private) |
| 021 | Модерация циклов |
| 022 | Статус упражнения (exercise_status) |
| 023 | Дата создания пользователя |

Полный список миграций всегда актуален в `backend/alembic/versions/`.
