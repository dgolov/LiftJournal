"""
Seed the database with initial data from mockData.js equivalents.
Idempotent: skips if data already exists.
"""
import asyncio
from datetime import date, datetime

from sqlalchemy import select, func

from app.core.database import async_session
from app.domain.models import Exercise, Workout, WorkoutExercise, ExerciseSet, User, WeightEntry, Goal


EXERCISES = [
    {"id": "ex-001", "name": "Жим лёжа", "muscle_group": "Грудь", "secondary_muscles": ["Трицепс", "Плечи"], "equipment": "Штанга", "description": "Базовое упражнение для развития грудных мышц"},
    {"id": "ex-002", "name": "Жим гантелей лёжа", "muscle_group": "Грудь", "secondary_muscles": ["Трицепс", "Плечи"], "equipment": "Гантели", "description": "Жим гантелей на горизонтальной скамье"},
    {"id": "ex-003", "name": "Жим под углом", "muscle_group": "Грудь", "secondary_muscles": ["Плечи", "Трицепс"], "equipment": "Штанга", "description": "Жим штанги на наклонной скамье"},
    {"id": "ex-004", "name": "Разводка гантелей", "muscle_group": "Грудь", "secondary_muscles": [], "equipment": "Гантели", "description": "Изолирующее упражнение для грудных мышц"},
    {"id": "ex-005", "name": "Отжимания", "muscle_group": "Грудь", "secondary_muscles": ["Трицепс", "Плечи"], "equipment": "Собственный вес", "description": "Классические отжимания от пола"},
    {"id": "ex-006", "name": "Становая тяга", "muscle_group": "Спина", "secondary_muscles": ["Ягодицы", "Квадрицепс", "Бицепс бедра"], "equipment": "Штанга", "description": "Базовое многосуставное упражнение"},
    {"id": "ex-007", "name": "Подтягивания", "muscle_group": "Спина", "secondary_muscles": ["Бицепс"], "equipment": "Собственный вес", "description": "Подтягивания широким хватом"},
    {"id": "ex-008", "name": "Тяга штанги в наклоне", "muscle_group": "Спина", "secondary_muscles": ["Бицепс", "Плечи"], "equipment": "Штанга", "description": "Тяга штанги к поясу в наклоне"},
    {"id": "ex-009", "name": "Тяга гантели одной рукой", "muscle_group": "Спина", "secondary_muscles": ["Бицепс"], "equipment": "Гантели", "description": "Тяга гантели к поясу одной рукой в наклоне"},
    {"id": "ex-010", "name": "Тяга верхнего блока", "muscle_group": "Спина", "secondary_muscles": ["Бицепс"], "equipment": "Блок", "description": "Тяга рукояти блока к груди"},
    {"id": "ex-011", "name": "Горизонтальная тяга блока", "muscle_group": "Спина", "secondary_muscles": ["Бицепс"], "equipment": "Блок", "description": "Горизонтальная тяга в тренажёре"},
    {"id": "ex-012", "name": "Жим штанги стоя", "muscle_group": "Плечи", "secondary_muscles": ["Трицепс"], "equipment": "Штанга", "description": "Жим штанги над головой стоя"},
    {"id": "ex-013", "name": "Жим гантелей сидя", "muscle_group": "Плечи", "secondary_muscles": ["Трицепс"], "equipment": "Гантели", "description": "Жим гантелей над головой сидя"},
    {"id": "ex-014", "name": "Разводка гантелей в стороны", "muscle_group": "Плечи", "secondary_muscles": [], "equipment": "Гантели", "description": "Подъём гантелей в стороны для средней дельты"},
    {"id": "ex-015", "name": "Тяга штанги к подбородку", "muscle_group": "Плечи", "secondary_muscles": ["Трапеции", "Бицепс"], "equipment": "Штанга", "description": "Тяга штанги к подбородку узким хватом"},
    {"id": "ex-016", "name": "Подъём штанги на бицепс", "muscle_group": "Бицепс", "secondary_muscles": [], "equipment": "Штанга", "description": "Классический подъём штанги стоя"},
    {"id": "ex-017", "name": "Подъём гантелей на бицепс", "muscle_group": "Бицепс", "secondary_muscles": [], "equipment": "Гантели", "description": "Попеременный или одновременный подъём гантелей"},
    {"id": "ex-018", "name": "Молоток", "muscle_group": "Бицепс", "secondary_muscles": [], "equipment": "Гантели", "description": "Подъём гантелей нейтральным хватом"},
    {"id": "ex-019", "name": "Подъём на блоке", "muscle_group": "Бицепс", "secondary_muscles": [], "equipment": "Блок", "description": "Подъём на бицепс на нижнем блоке"},
    {"id": "ex-020", "name": "Жим узким хватом", "muscle_group": "Трицепс", "secondary_muscles": ["Грудь"], "equipment": "Штанга", "description": "Жим штанги узким хватом на горизонтальной скамье"},
    {"id": "ex-021", "name": "Французский жим", "muscle_group": "Трицепс", "secondary_muscles": [], "equipment": "Штанга", "description": "Французский жим лёжа"},
    {"id": "ex-022", "name": "Разгибание на блоке", "muscle_group": "Трицепс", "secondary_muscles": [], "equipment": "Блок", "description": "Разгибание рук на верхнем блоке"},
    {"id": "ex-023", "name": "Отжимания на брусьях", "muscle_group": "Трицепс", "secondary_muscles": ["Грудь", "Плечи"], "equipment": "Собственный вес", "description": "Отжимания на параллельных брусьях"},
    {"id": "ex-024", "name": "Приседания со штангой", "muscle_group": "Квадрицепс", "secondary_muscles": ["Ягодицы", "Бицепс бедра"], "equipment": "Штанга", "description": "Классические приседания со штангой на плечах"},
    {"id": "ex-025", "name": "Жим ногами", "muscle_group": "Квадрицепс", "secondary_muscles": ["Ягодицы"], "equipment": "Тренажёр", "description": "Жим ногами в тренажёре"},
    {"id": "ex-026", "name": "Разгибание ног", "muscle_group": "Квадрицепс", "secondary_muscles": [], "equipment": "Тренажёр", "description": "Разгибание ног в тренажёре"},
    {"id": "ex-027", "name": "Румынская тяга", "muscle_group": "Бицепс бедра", "secondary_muscles": ["Ягодицы", "Спина"], "equipment": "Штанга", "description": "Румынская тяга на прямых ногах"},
    {"id": "ex-028", "name": "Сгибание ног", "muscle_group": "Бицепс бедра", "secondary_muscles": [], "equipment": "Тренажёр", "description": "Сгибание ног лёжа в тренажёре"},
    {"id": "ex-029", "name": "Выпады с гантелями", "muscle_group": "Квадрицепс", "secondary_muscles": ["Ягодицы", "Бицепс бедра"], "equipment": "Гантели", "description": "Выпады с гантелями в руках"},
    {"id": "ex-030", "name": "Подъём на носки", "muscle_group": "Икры", "secondary_muscles": [], "equipment": "Тренажёр", "description": "Подъём на носки в тренажёре для икр"},
    {"id": "ex-031", "name": "Ягодичный мостик", "muscle_group": "Ягодицы", "secondary_muscles": ["Бицепс бедра"], "equipment": "Штанга", "description": "Ягодичный мостик со штангой"},
    {"id": "ex-032", "name": "Скручивания", "muscle_group": "Пресс", "secondary_muscles": [], "equipment": "Собственный вес", "description": "Классические скручивания на пресс"},
    {"id": "ex-033", "name": "Подъём ног", "muscle_group": "Пресс", "secondary_muscles": [], "equipment": "Собственный вес", "description": "Подъём прямых ног лёжа"},
    {"id": "ex-034", "name": "Планка", "muscle_group": "Пресс", "secondary_muscles": ["Плечи", "Ягодицы"], "equipment": "Собственный вес", "description": "Статическое упражнение — планка"},
    {"id": "ex-035", "name": "Бег", "muscle_group": "Кардио", "secondary_muscles": [], "equipment": "Беговая дорожка", "description": "Бег на дорожке или на улице"},
    {"id": "ex-036", "name": "Велотренажёр", "muscle_group": "Кардио", "secondary_muscles": [], "equipment": "Тренажёр", "description": "Кардио на велотренажёре"},
    {"id": "ex-037", "name": "Прыжки на скакалке", "muscle_group": "Кардио", "secondary_muscles": ["Икры"], "equipment": "Собственный вес", "description": "Прыжки на скакалке"},
    {"id": "ex-038", "name": "Гиря — мах", "muscle_group": "Ягодицы", "secondary_muscles": ["Спина", "Плечи"], "equipment": "Гиря", "description": "Мах гирей двумя руками"},
]

WORKOUTS = [
    {
        "date": date(2026, 3, 1), "type": "Силовая", "title": "Грудь и трицепс",
        "duration_minutes": 70, "notes": "Хорошая тренировка, жим пошёл хорошо",
        "created_at": datetime(2026, 3, 1),
        "exercises": [
            {"exercise_id": "ex-001", "exercise_name": "Жим лёжа", "sets": [
                {"weight": 80, "reps": 8}, {"weight": 80, "reps": 8},
                {"weight": 85, "reps": 6}, {"weight": 85, "reps": 5},
            ]},
            {"exercise_id": "ex-003", "exercise_name": "Жим под углом", "sets": [
                {"weight": 70, "reps": 10}, {"weight": 70, "reps": 9}, {"weight": 70, "reps": 8},
            ]},
            {"exercise_id": "ex-022", "exercise_name": "Разгибание на блоке", "sets": [
                {"weight": 35, "reps": 12}, {"weight": 35, "reps": 12}, {"weight": 40, "reps": 10},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 27), "type": "Силовая", "title": "Спина и бицепс",
        "duration_minutes": 65, "notes": "", "created_at": datetime(2026, 2, 27),
        "exercises": [
            {"exercise_id": "ex-006", "exercise_name": "Становая тяга", "sets": [
                {"weight": 120, "reps": 5}, {"weight": 120, "reps": 5}, {"weight": 130, "reps": 4},
            ]},
            {"exercise_id": "ex-007", "exercise_name": "Подтягивания", "sets": [
                {"weight": 0, "reps": 10}, {"weight": 0, "reps": 9}, {"weight": 0, "reps": 8},
            ]},
            {"exercise_id": "ex-016", "exercise_name": "Подъём штанги на бицепс", "sets": [
                {"weight": 45, "reps": 10}, {"weight": 45, "reps": 10}, {"weight": 50, "reps": 8},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 24), "type": "Силовая", "title": "Ноги",
        "duration_minutes": 80, "notes": "Тяжёлая тренировка, квадрицепсы горят",
        "created_at": datetime(2026, 2, 24),
        "exercises": [
            {"exercise_id": "ex-024", "exercise_name": "Приседания со штангой", "sets": [
                {"weight": 100, "reps": 8}, {"weight": 100, "reps": 8},
                {"weight": 105, "reps": 6}, {"weight": 105, "reps": 5},
            ]},
            {"exercise_id": "ex-025", "exercise_name": "Жим ногами", "sets": [
                {"weight": 180, "reps": 12}, {"weight": 180, "reps": 12}, {"weight": 200, "reps": 10},
            ]},
            {"exercise_id": "ex-027", "exercise_name": "Румынская тяга", "sets": [
                {"weight": 80, "reps": 10}, {"weight": 80, "reps": 10}, {"weight": 85, "reps": 8},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 21), "type": "Кардио", "title": "Кардио",
        "duration_minutes": 35, "notes": "Лёгкое кардио между силовыми",
        "created_at": datetime(2026, 2, 21),
        "exercises": [
            {"exercise_id": "ex-035", "exercise_name": "Бег", "sets": [{"weight": 0, "reps": 1}]},
        ],
    },
    {
        "date": date(2026, 2, 19), "type": "Силовая", "title": "Грудь и трицепс",
        "duration_minutes": 68, "notes": "", "created_at": datetime(2026, 2, 19),
        "exercises": [
            {"exercise_id": "ex-001", "exercise_name": "Жим лёжа", "sets": [
                {"weight": 80, "reps": 8}, {"weight": 80, "reps": 7}, {"weight": 82.5, "reps": 6},
            ]},
            {"exercise_id": "ex-004", "exercise_name": "Разводка гантелей", "sets": [
                {"weight": 18, "reps": 12}, {"weight": 18, "reps": 12}, {"weight": 20, "reps": 10},
            ]},
            {"exercise_id": "ex-021", "exercise_name": "Французский жим", "sets": [
                {"weight": 40, "reps": 10}, {"weight": 40, "reps": 10}, {"weight": 40, "reps": 9},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 17), "type": "Силовая", "title": "Спина и бицепс",
        "duration_minutes": 60, "notes": "", "created_at": datetime(2026, 2, 17),
        "exercises": [
            {"exercise_id": "ex-008", "exercise_name": "Тяга штанги в наклоне", "sets": [
                {"weight": 80, "reps": 8}, {"weight": 80, "reps": 8}, {"weight": 85, "reps": 6},
            ]},
            {"exercise_id": "ex-010", "exercise_name": "Тяга верхнего блока", "sets": [
                {"weight": 65, "reps": 12}, {"weight": 65, "reps": 11}, {"weight": 70, "reps": 10},
            ]},
            {"exercise_id": "ex-017", "exercise_name": "Подъём гантелей на бицепс", "sets": [
                {"weight": 18, "reps": 12}, {"weight": 18, "reps": 12}, {"weight": 20, "reps": 10},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 14), "type": "Силовая", "title": "Плечи",
        "duration_minutes": 55, "notes": "Фокус на средней дельте",
        "created_at": datetime(2026, 2, 14),
        "exercises": [
            {"exercise_id": "ex-012", "exercise_name": "Жим штанги стоя", "sets": [
                {"weight": 60, "reps": 8}, {"weight": 60, "reps": 8}, {"weight": 65, "reps": 6},
            ]},
            {"exercise_id": "ex-014", "exercise_name": "Разводка гантелей в стороны", "sets": [
                {"weight": 12, "reps": 15}, {"weight": 12, "reps": 15},
                {"weight": 14, "reps": 12}, {"weight": 14, "reps": 12},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 10), "type": "Силовая", "title": "Ноги",
        "duration_minutes": 75, "notes": "", "created_at": datetime(2026, 2, 10),
        "exercises": [
            {"exercise_id": "ex-024", "exercise_name": "Приседания со штангой", "sets": [
                {"weight": 95, "reps": 8}, {"weight": 100, "reps": 8},
                {"weight": 100, "reps": 7}, {"weight": 100, "reps": 6},
            ]},
            {"exercise_id": "ex-026", "exercise_name": "Разгибание ног", "sets": [
                {"weight": 50, "reps": 15}, {"weight": 50, "reps": 15}, {"weight": 55, "reps": 12},
            ]},
            {"exercise_id": "ex-028", "exercise_name": "Сгибание ног", "sets": [
                {"weight": 40, "reps": 15}, {"weight": 40, "reps": 14}, {"weight": 45, "reps": 12},
            ]},
            {"exercise_id": "ex-030", "exercise_name": "Подъём на носки", "sets": [
                {"weight": 70, "reps": 20}, {"weight": 70, "reps": 20}, {"weight": 80, "reps": 15},
            ]},
        ],
    },
    {
        "date": date(2026, 2, 7), "type": "Силовая", "title": "Грудь и трицепс",
        "duration_minutes": 65, "notes": "Новый личный рекорд в жиме!",
        "created_at": datetime(2026, 2, 7),
        "exercises": [
            {"exercise_id": "ex-001", "exercise_name": "Жим лёжа", "sets": [
                {"weight": 82.5, "reps": 8}, {"weight": 85, "reps": 6},
                {"weight": 87.5, "reps": 5}, {"weight": 90, "reps": 3},
            ]},
            {"exercise_id": "ex-003", "exercise_name": "Жим под углом", "sets": [
                {"weight": 70, "reps": 10}, {"weight": 72.5, "reps": 8}, {"weight": 72.5, "reps": 7},
            ]},
            {"exercise_id": "ex-023", "exercise_name": "Отжимания на брусьях", "sets": [
                {"weight": 10, "reps": 12}, {"weight": 10, "reps": 11}, {"weight": 15, "reps": 8},
            ]},
        ],
    },
    {
        "date": date(2026, 1, 31), "type": "HIIT", "title": "HIIT тренировка",
        "duration_minutes": 30, "notes": "Интенсивная круговая",
        "created_at": datetime(2026, 1, 31),
        "exercises": [
            {"exercise_id": "ex-034", "exercise_name": "Планка", "sets": [
                {"weight": 0, "reps": 60}, {"weight": 0, "reps": 60}, {"weight": 0, "reps": 45},
            ]},
            {"exercise_id": "ex-037", "exercise_name": "Прыжки на скакалке", "sets": [
                {"weight": 0, "reps": 100}, {"weight": 0, "reps": 100},
            ]},
        ],
    },
    {
        "date": date(2026, 1, 28), "type": "Силовая", "title": "Спина и бицепс",
        "duration_minutes": 60, "notes": "", "created_at": datetime(2026, 1, 28),
        "exercises": [
            {"exercise_id": "ex-006", "exercise_name": "Становая тяга", "sets": [
                {"weight": 115, "reps": 5}, {"weight": 120, "reps": 5}, {"weight": 120, "reps": 4},
            ]},
            {"exercise_id": "ex-007", "exercise_name": "Подтягивания", "sets": [
                {"weight": 0, "reps": 10}, {"weight": 0, "reps": 9}, {"weight": 0, "reps": 8},
            ]},
            {"exercise_id": "ex-018", "exercise_name": "Молоток", "sets": [
                {"weight": 20, "reps": 12}, {"weight": 20, "reps": 12}, {"weight": 22, "reps": 10},
            ]},
        ],
    },
    {
        "date": date(2026, 1, 24), "type": "Силовая", "title": "Ноги",
        "duration_minutes": 72, "notes": "", "created_at": datetime(2026, 1, 24),
        "exercises": [
            {"exercise_id": "ex-024", "exercise_name": "Приседания со штангой", "sets": [
                {"weight": 95, "reps": 8}, {"weight": 95, "reps": 8}, {"weight": 100, "reps": 6},
            ]},
            {"exercise_id": "ex-029", "exercise_name": "Выпады с гантелями", "sets": [
                {"weight": 20, "reps": 12}, {"weight": 20, "reps": 12}, {"weight": 22, "reps": 10},
            ]},
            {"exercise_id": "ex-031", "exercise_name": "Ягодичный мостик", "sets": [
                {"weight": 80, "reps": 12}, {"weight": 80, "reps": 12}, {"weight": 90, "reps": 10},
            ]},
        ],
    },
    {
        "date": date(2026, 1, 20), "type": "Растяжка", "title": "Растяжка и восстановление",
        "duration_minutes": 40, "notes": "Мышцы болят после тяжёлой недели",
        "created_at": datetime(2026, 1, 20),
        "exercises": [],
    },
    {
        "date": date(2026, 1, 17), "type": "Силовая", "title": "Грудь и трицепс",
        "duration_minutes": 60, "notes": "", "created_at": datetime(2026, 1, 17),
        "exercises": [
            {"exercise_id": "ex-001", "exercise_name": "Жим лёжа", "sets": [
                {"weight": 77.5, "reps": 8}, {"weight": 80, "reps": 7}, {"weight": 80, "reps": 6},
            ]},
            {"exercise_id": "ex-005", "exercise_name": "Отжимания", "sets": [
                {"weight": 0, "reps": 20}, {"weight": 0, "reps": 18}, {"weight": 0, "reps": 15},
            ]},
            {"exercise_id": "ex-020", "exercise_name": "Жим узким хватом", "sets": [
                {"weight": 60, "reps": 10}, {"weight": 60, "reps": 10}, {"weight": 65, "reps": 8},
            ]},
        ],
    },
    {
        "date": date(2025, 12, 29), "type": "Силовая", "title": "Последняя тренировка года",
        "duration_minutes": 55, "notes": "Итоги года — чувствую прогресс!",
        "created_at": datetime(2025, 12, 29),
        "exercises": [
            {"exercise_id": "ex-001", "exercise_name": "Жим лёжа", "sets": [
                {"weight": 75, "reps": 8}, {"weight": 77.5, "reps": 7}, {"weight": 77.5, "reps": 6},
            ]},
            {"exercise_id": "ex-024", "exercise_name": "Приседания со штангой", "sets": [
                {"weight": 90, "reps": 8}, {"weight": 90, "reps": 7}, {"weight": 90, "reps": 6},
            ]},
            {"exercise_id": "ex-006", "exercise_name": "Становая тяга", "sets": [
                {"weight": 110, "reps": 5}, {"weight": 110, "reps": 5}, {"weight": 115, "reps": 4},
            ]},
        ],
    },
]

USER = {
    "name": "Александр",
    "age": 28,
    "avatar_url": None,
    "weight_log": [
        {"date": date(2025, 11, 1), "kg": 84.0},
        {"date": date(2025, 12, 1), "kg": 82.5},
        {"date": date(2026, 1, 5), "kg": 81.0},
        {"date": date(2026, 1, 20), "kg": 80.5},
        {"date": date(2026, 2, 1), "kg": 80.0},
        {"date": date(2026, 2, 15), "kg": 79.5},
        {"date": date(2026, 3, 1), "kg": 79.0},
    ],
    "goals": [
        {"text": "Жим лёжа 100 кг", "target_date": date(2026, 6, 1), "done": False},
        {"text": "Похудеть до 77 кг", "target_date": date(2026, 7, 1), "done": False},
        {"text": "Становая тяга 150 кг", "target_date": date(2026, 9, 1), "done": False},
        {"text": "Тренироваться 3 раза в неделю", "target_date": date(2026, 4, 1), "done": False},
    ],
}


async def seed():
    async with async_session() as db:
        # Exercises
        count = await db.scalar(select(func.count()).select_from(Exercise))
        if count == 0:
            print("Seeding exercises...")
            for ex in EXERCISES:
                db.add(Exercise(
                    id=ex["id"],
                    name=ex["name"],
                    muscle_group=ex["muscle_group"],
                    secondary_muscles=ex["secondary_muscles"],
                    equipment=ex["equipment"],
                    description=ex["description"],
                    is_custom=False,
                ))
            await db.commit()

        # User
        user_count = await db.scalar(select(func.count()).select_from(User))
        if user_count == 0:
            print("Seeding user...")
            user = User(id=1, name=USER["name"], age=USER["age"], avatar_url=USER["avatar_url"])
            db.add(user)
            await db.flush()
            for entry in USER["weight_log"]:
                db.add(WeightEntry(user_id=1, date=entry["date"], kg=entry["kg"]))
            for goal in USER["goals"]:
                db.add(Goal(
                    user_id=1,
                    text=goal["text"],
                    target_date=goal["target_date"],
                    done=goal["done"],
                ))
            await db.commit()

        # Workouts
        workout_count = await db.scalar(select(func.count()).select_from(Workout))
        if workout_count == 0:
            print("Seeding workouts...")
            for w_data in WORKOUTS:
                workout = Workout(
                    date=w_data["date"],
                    type=w_data["type"],
                    title=w_data["title"],
                    duration_minutes=w_data["duration_minutes"],
                    notes=w_data["notes"],
                    created_at=w_data["created_at"],
                )
                db.add(workout)
                await db.flush()
                for i, ex_data in enumerate(w_data["exercises"]):
                    we = WorkoutExercise(
                        workout_id=workout.id,
                        exercise_id=ex_data["exercise_id"],
                        exercise_name=ex_data["exercise_name"],
                        order=i,
                    )
                    db.add(we)
                    await db.flush()
                    for j, set_data in enumerate(ex_data["sets"]):
                        db.add(ExerciseSet(
                            workout_exercise_id=we.id,
                            weight=set_data["weight"],
                            reps=set_data["reps"],
                            completed=True,
                            order=j,
                        ))
            await db.commit()

    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
