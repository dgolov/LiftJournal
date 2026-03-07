export const WORKOUT_TYPES = ['Силовая', 'Кардио', 'Растяжка', 'HIIT', 'Другое']

export const MUSCLE_GROUPS = [
  'Грудь', 'Спина', 'Плечи', 'Бицепс', 'Трицепс',
  'Пресс', 'Квадрицепс', 'Бицепс бедра', 'Икры', 'Ягодицы', 'Кардио'
]

export const EQUIPMENT_TYPES = [
  'Штанга', 'Гантели', 'Тренажёр', 'Собственный вес', 'Гиря', 'Блок', 'Беговая дорожка'
]

/** @type {import('@/models/types').ExerciseDefinition[]} */
export const exerciseLibrary = [
  // Грудь
  { id: 'ex-001', name: 'Жим лёжа', muscleGroup: 'Грудь', secondaryMuscles: ['Трицепс', 'Плечи'], equipment: 'Штанга', description: 'Базовое упражнение для развития грудных мышц', isCustom: false },
  { id: 'ex-002', name: 'Жим гантелей лёжа', muscleGroup: 'Грудь', secondaryMuscles: ['Трицепс', 'Плечи'], equipment: 'Гантели', description: 'Жим гантелей на горизонтальной скамье', isCustom: false },
  { id: 'ex-003', name: 'Жим под углом', muscleGroup: 'Грудь', secondaryMuscles: ['Плечи', 'Трицепс'], equipment: 'Штанга', description: 'Жим штанги на наклонной скамье', isCustom: false },
  { id: 'ex-004', name: 'Разводка гантелей', muscleGroup: 'Грудь', secondaryMuscles: [], equipment: 'Гантели', description: 'Изолирующее упражнение для грудных мышц', isCustom: false },
  { id: 'ex-005', name: 'Отжимания', muscleGroup: 'Грудь', secondaryMuscles: ['Трицепс', 'Плечи'], equipment: 'Собственный вес', description: 'Классические отжимания от пола', isCustom: false },

  // Спина
  { id: 'ex-006', name: 'Становая тяга', muscleGroup: 'Спина', secondaryMuscles: ['Ягодицы', 'Квадрицепс', 'Бицепс бедра'], equipment: 'Штанга', description: 'Базовое многосуставное упражнение', isCustom: false },
  { id: 'ex-007', name: 'Подтягивания', muscleGroup: 'Спина', secondaryMuscles: ['Бицепс'], equipment: 'Собственный вес', description: 'Подтягивания широким хватом', isCustom: false },
  { id: 'ex-008', name: 'Тяга штанги в наклоне', muscleGroup: 'Спина', secondaryMuscles: ['Бицепс', 'Плечи'], equipment: 'Штанга', description: 'Тяга штанги к поясу в наклоне', isCustom: false },
  { id: 'ex-009', name: 'Тяга гантели одной рукой', muscleGroup: 'Спина', secondaryMuscles: ['Бицепс'], equipment: 'Гантели', description: 'Тяга гантели к поясу одной рукой в наклоне', isCustom: false },
  { id: 'ex-010', name: 'Тяга верхнего блока', muscleGroup: 'Спина', secondaryMuscles: ['Бицепс'], equipment: 'Блок', description: 'Тяга рукояти блока к груди', isCustom: false },
  { id: 'ex-011', name: 'Горизонтальная тяга блока', muscleGroup: 'Спина', secondaryMuscles: ['Бицепс'], equipment: 'Блок', description: 'Горизонтальная тяга в тренажёре', isCustom: false },

  // Плечи
  { id: 'ex-012', name: 'Жим штанги стоя', muscleGroup: 'Плечи', secondaryMuscles: ['Трицепс'], equipment: 'Штанга', description: 'Жим штанги над головой стоя', isCustom: false },
  { id: 'ex-013', name: 'Жим гантелей сидя', muscleGroup: 'Плечи', secondaryMuscles: ['Трицепс'], equipment: 'Гантели', description: 'Жим гантелей над головой сидя', isCustom: false },
  { id: 'ex-014', name: 'Разводка гантелей в стороны', muscleGroup: 'Плечи', secondaryMuscles: [], equipment: 'Гантели', description: 'Подъём гантелей в стороны для средней дельты', isCustom: false },
  { id: 'ex-015', name: 'Тяга штанги к подбородку', muscleGroup: 'Плечи', secondaryMuscles: ['Трапеции', 'Бицепс'], equipment: 'Штанга', description: 'Тяга штанги к подбородку узким хватом', isCustom: false },

  // Бицепс
  { id: 'ex-016', name: 'Подъём штанги на бицепс', muscleGroup: 'Бицепс', secondaryMuscles: [], equipment: 'Штанга', description: 'Классический подъём штанги стоя', isCustom: false },
  { id: 'ex-017', name: 'Подъём гантелей на бицепс', muscleGroup: 'Бицепс', secondaryMuscles: [], equipment: 'Гантели', description: 'Попеременный или одновременный подъём гантелей', isCustom: false },
  { id: 'ex-018', name: 'Молоток', muscleGroup: 'Бицепс', secondaryMuscles: [], equipment: 'Гантели', description: 'Подъём гантелей нейтральным хватом', isCustom: false },
  { id: 'ex-019', name: 'Подъём на блоке', muscleGroup: 'Бицепс', secondaryMuscles: [], equipment: 'Блок', description: 'Подъём на бицепс на нижнем блоке', isCustom: false },

  // Трицепс
  { id: 'ex-020', name: 'Жим узким хватом', muscleGroup: 'Трицепс', secondaryMuscles: ['Грудь'], equipment: 'Штанга', description: 'Жим штанги узким хватом на горизонтальной скамье', isCustom: false },
  { id: 'ex-021', name: 'Французский жим', muscleGroup: 'Трицепс', secondaryMuscles: [], equipment: 'Штанга', description: 'Французский жим лёжа', isCustom: false },
  { id: 'ex-022', name: 'Разгибание на блоке', muscleGroup: 'Трицепс', secondaryMuscles: [], equipment: 'Блок', description: 'Разгибание рук на верхнем блоке', isCustom: false },
  { id: 'ex-023', name: 'Отжимания на брусьях', muscleGroup: 'Трицепс', secondaryMuscles: ['Грудь', 'Плечи'], equipment: 'Собственный вес', description: 'Отжимания на параллельных брусьях', isCustom: false },

  // Ноги
  { id: 'ex-024', name: 'Приседания со штангой', muscleGroup: 'Квадрицепс', secondaryMuscles: ['Ягодицы', 'Бицепс бедра'], equipment: 'Штанга', description: 'Классические приседания со штангой на плечах', isCustom: false },
  { id: 'ex-025', name: 'Жим ногами', muscleGroup: 'Квадрицепс', secondaryMuscles: ['Ягодицы'], equipment: 'Тренажёр', description: 'Жим ногами в тренажёре', isCustom: false },
  { id: 'ex-026', name: 'Разгибание ног', muscleGroup: 'Квадрицепс', secondaryMuscles: [], equipment: 'Тренажёр', description: 'Разгибание ног в тренажёре', isCustom: false },
  { id: 'ex-027', name: 'Румынская тяга', muscleGroup: 'Бицепс бедра', secondaryMuscles: ['Ягодицы', 'Спина'], equipment: 'Штанга', description: 'Румынская тяга на прямых ногах', isCustom: false },
  { id: 'ex-028', name: 'Сгибание ног', muscleGroup: 'Бицепс бедра', secondaryMuscles: [], equipment: 'Тренажёр', description: 'Сгибание ног лёжа в тренажёре', isCustom: false },
  { id: 'ex-029', name: 'Выпады с гантелями', muscleGroup: 'Квадрицепс', secondaryMuscles: ['Ягодицы', 'Бицепс бедра'], equipment: 'Гантели', description: 'Выпады с гантелями в руках', isCustom: false },
  { id: 'ex-030', name: 'Подъём на носки', muscleGroup: 'Икры', secondaryMuscles: [], equipment: 'Тренажёр', description: 'Подъём на носки в тренажёре для икр', isCustom: false },
  { id: 'ex-031', name: 'Ягодичный мостик', muscleGroup: 'Ягодицы', secondaryMuscles: ['Бицепс бедра'], equipment: 'Штанга', description: 'Ягодичный мостик со штангой', isCustom: false },

  // Пресс
  { id: 'ex-032', name: 'Скручивания', muscleGroup: 'Пресс', secondaryMuscles: [], equipment: 'Собственный вес', description: 'Классические скручивания на пресс', isCustom: false },
  { id: 'ex-033', name: 'Подъём ног', muscleGroup: 'Пресс', secondaryMuscles: [], equipment: 'Собственный вес', description: 'Подъём прямых ног лёжа', isCustom: false },
  { id: 'ex-034', name: 'Планка', muscleGroup: 'Пресс', secondaryMuscles: ['Плечи', 'Ягодицы'], equipment: 'Собственный вес', description: 'Статическое упражнение — планка', isCustom: false },

  // Кардио
  { id: 'ex-035', name: 'Бег', muscleGroup: 'Кардио', secondaryMuscles: [], equipment: 'Беговая дорожка', description: 'Бег на дорожке или на улице', isCustom: false },
  { id: 'ex-036', name: 'Велотренажёр', muscleGroup: 'Кардио', secondaryMuscles: [], equipment: 'Тренажёр', description: 'Кардио на велотренажёре', isCustom: false },
  { id: 'ex-037', name: 'Прыжки на скакалке', muscleGroup: 'Кардио', secondaryMuscles: ['Икры'], equipment: 'Собственный вес', description: 'Прыжки на скакалке', isCustom: false },
  { id: 'ex-038', name: 'Гиря — мах', muscleGroup: 'Ягодицы', secondaryMuscles: ['Спина', 'Плечи'], equipment: 'Гиря', description: 'Мах гирей двумя руками', isCustom: false }
]

/** @type {import('@/models/types').Workout[]} */
export const mockWorkouts = [
  {
    id: 'w-001',
    date: '2026-03-01',
    type: 'Силовая',
    title: 'Грудь и трицепс',
    durationMinutes: 70,
    notes: 'Хорошая тренировка, жим пошёл хорошо',
    createdAt: new Date('2026-03-01').getTime(),
    exercises: [
      {
        exerciseId: 'ex-001',
        exerciseName: 'Жим лёжа',
        sets: [
          { id: 's-001-1', weight: 80, reps: 8, completed: true },
          { id: 's-001-2', weight: 80, reps: 8, completed: true },
          { id: 's-001-3', weight: 85, reps: 6, completed: true },
          { id: 's-001-4', weight: 85, reps: 5, completed: true }
        ]
      },
      {
        exerciseId: 'ex-003',
        exerciseName: 'Жим под углом',
        sets: [
          { id: 's-001-5', weight: 70, reps: 10, completed: true },
          { id: 's-001-6', weight: 70, reps: 9, completed: true },
          { id: 's-001-7', weight: 70, reps: 8, completed: true }
        ]
      },
      {
        exerciseId: 'ex-022',
        exerciseName: 'Разгибание на блоке',
        sets: [
          { id: 's-001-8', weight: 35, reps: 12, completed: true },
          { id: 's-001-9', weight: 35, reps: 12, completed: true },
          { id: 's-001-10', weight: 40, reps: 10, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-002',
    date: '2026-02-27',
    type: 'Силовая',
    title: 'Спина и бицепс',
    durationMinutes: 65,
    notes: '',
    createdAt: new Date('2026-02-27').getTime(),
    exercises: [
      {
        exerciseId: 'ex-006',
        exerciseName: 'Становая тяга',
        sets: [
          { id: 's-002-1', weight: 120, reps: 5, completed: true },
          { id: 's-002-2', weight: 120, reps: 5, completed: true },
          { id: 's-002-3', weight: 130, reps: 4, completed: true }
        ]
      },
      {
        exerciseId: 'ex-007',
        exerciseName: 'Подтягивания',
        sets: [
          { id: 's-002-4', weight: 0, reps: 10, completed: true },
          { id: 's-002-5', weight: 0, reps: 9, completed: true },
          { id: 's-002-6', weight: 0, reps: 8, completed: true }
        ]
      },
      {
        exerciseId: 'ex-016',
        exerciseName: 'Подъём штанги на бицепс',
        sets: [
          { id: 's-002-7', weight: 45, reps: 10, completed: true },
          { id: 's-002-8', weight: 45, reps: 10, completed: true },
          { id: 's-002-9', weight: 50, reps: 8, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-003',
    date: '2026-02-24',
    type: 'Силовая',
    title: 'Ноги',
    durationMinutes: 80,
    notes: 'Тяжёлая тренировка, квадрицепсы горят',
    createdAt: new Date('2026-02-24').getTime(),
    exercises: [
      {
        exerciseId: 'ex-024',
        exerciseName: 'Приседания со штангой',
        sets: [
          { id: 's-003-1', weight: 100, reps: 8, completed: true },
          { id: 's-003-2', weight: 100, reps: 8, completed: true },
          { id: 's-003-3', weight: 105, reps: 6, completed: true },
          { id: 's-003-4', weight: 105, reps: 5, completed: true }
        ]
      },
      {
        exerciseId: 'ex-025',
        exerciseName: 'Жим ногами',
        sets: [
          { id: 's-003-5', weight: 180, reps: 12, completed: true },
          { id: 's-003-6', weight: 180, reps: 12, completed: true },
          { id: 's-003-7', weight: 200, reps: 10, completed: true }
        ]
      },
      {
        exerciseId: 'ex-027',
        exerciseName: 'Румынская тяга',
        sets: [
          { id: 's-003-8', weight: 80, reps: 10, completed: true },
          { id: 's-003-9', weight: 80, reps: 10, completed: true },
          { id: 's-003-10', weight: 85, reps: 8, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-004',
    date: '2026-02-21',
    type: 'Кардио',
    title: 'Кардио',
    durationMinutes: 35,
    notes: 'Лёгкое кардио между силовыми',
    createdAt: new Date('2026-02-21').getTime(),
    exercises: [
      {
        exerciseId: 'ex-035',
        exerciseName: 'Бег',
        sets: [
          { id: 's-004-1', weight: 0, reps: 1, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-005',
    date: '2026-02-19',
    type: 'Силовая',
    title: 'Грудь и трицепс',
    durationMinutes: 68,
    notes: '',
    createdAt: new Date('2026-02-19').getTime(),
    exercises: [
      {
        exerciseId: 'ex-001',
        exerciseName: 'Жим лёжа',
        sets: [
          { id: 's-005-1', weight: 80, reps: 8, completed: true },
          { id: 's-005-2', weight: 80, reps: 7, completed: true },
          { id: 's-005-3', weight: 82.5, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-004',
        exerciseName: 'Разводка гантелей',
        sets: [
          { id: 's-005-4', weight: 18, reps: 12, completed: true },
          { id: 's-005-5', weight: 18, reps: 12, completed: true },
          { id: 's-005-6', weight: 20, reps: 10, completed: true }
        ]
      },
      {
        exerciseId: 'ex-021',
        exerciseName: 'Французский жим',
        sets: [
          { id: 's-005-7', weight: 40, reps: 10, completed: true },
          { id: 's-005-8', weight: 40, reps: 10, completed: true },
          { id: 's-005-9', weight: 40, reps: 9, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-006',
    date: '2026-02-17',
    type: 'Силовая',
    title: 'Спина и бицепс',
    durationMinutes: 60,
    notes: '',
    createdAt: new Date('2026-02-17').getTime(),
    exercises: [
      {
        exerciseId: 'ex-008',
        exerciseName: 'Тяга штанги в наклоне',
        sets: [
          { id: 's-006-1', weight: 80, reps: 8, completed: true },
          { id: 's-006-2', weight: 80, reps: 8, completed: true },
          { id: 's-006-3', weight: 85, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-010',
        exerciseName: 'Тяга верхнего блока',
        sets: [
          { id: 's-006-4', weight: 65, reps: 12, completed: true },
          { id: 's-006-5', weight: 65, reps: 11, completed: true },
          { id: 's-006-6', weight: 70, reps: 10, completed: true }
        ]
      },
      {
        exerciseId: 'ex-017',
        exerciseName: 'Подъём гантелей на бицепс',
        sets: [
          { id: 's-006-7', weight: 18, reps: 12, completed: true },
          { id: 's-006-8', weight: 18, reps: 12, completed: true },
          { id: 's-006-9', weight: 20, reps: 10, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-007',
    date: '2026-02-14',
    type: 'Силовая',
    title: 'Плечи',
    durationMinutes: 55,
    notes: 'Фокус на средней дельте',
    createdAt: new Date('2026-02-14').getTime(),
    exercises: [
      {
        exerciseId: 'ex-012',
        exerciseName: 'Жим штанги стоя',
        sets: [
          { id: 's-007-1', weight: 60, reps: 8, completed: true },
          { id: 's-007-2', weight: 60, reps: 8, completed: true },
          { id: 's-007-3', weight: 65, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-014',
        exerciseName: 'Разводка гантелей в стороны',
        sets: [
          { id: 's-007-4', weight: 12, reps: 15, completed: true },
          { id: 's-007-5', weight: 12, reps: 15, completed: true },
          { id: 's-007-6', weight: 14, reps: 12, completed: true },
          { id: 's-007-7', weight: 14, reps: 12, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-008',
    date: '2026-02-10',
    type: 'Силовая',
    title: 'Ноги',
    durationMinutes: 75,
    notes: '',
    createdAt: new Date('2026-02-10').getTime(),
    exercises: [
      {
        exerciseId: 'ex-024',
        exerciseName: 'Приседания со штангой',
        sets: [
          { id: 's-008-1', weight: 95, reps: 8, completed: true },
          { id: 's-008-2', weight: 100, reps: 8, completed: true },
          { id: 's-008-3', weight: 100, reps: 7, completed: true },
          { id: 's-008-4', weight: 100, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-026',
        exerciseName: 'Разгибание ног',
        sets: [
          { id: 's-008-5', weight: 50, reps: 15, completed: true },
          { id: 's-008-6', weight: 50, reps: 15, completed: true },
          { id: 's-008-7', weight: 55, reps: 12, completed: true }
        ]
      },
      {
        exerciseId: 'ex-028',
        exerciseName: 'Сгибание ног',
        sets: [
          { id: 's-008-8', weight: 40, reps: 15, completed: true },
          { id: 's-008-9', weight: 40, reps: 14, completed: true },
          { id: 's-008-10', weight: 45, reps: 12, completed: true }
        ]
      },
      {
        exerciseId: 'ex-030',
        exerciseName: 'Подъём на носки',
        sets: [
          { id: 's-008-11', weight: 70, reps: 20, completed: true },
          { id: 's-008-12', weight: 70, reps: 20, completed: true },
          { id: 's-008-13', weight: 80, reps: 15, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-009',
    date: '2026-02-07',
    type: 'Силовая',
    title: 'Грудь и трицепс',
    durationMinutes: 65,
    notes: 'Новый личный рекорд в жиме!',
    createdAt: new Date('2026-02-07').getTime(),
    exercises: [
      {
        exerciseId: 'ex-001',
        exerciseName: 'Жим лёжа',
        sets: [
          { id: 's-009-1', weight: 82.5, reps: 8, completed: true },
          { id: 's-009-2', weight: 85, reps: 6, completed: true },
          { id: 's-009-3', weight: 87.5, reps: 5, completed: true },
          { id: 's-009-4', weight: 90, reps: 3, completed: true }
        ]
      },
      {
        exerciseId: 'ex-003',
        exerciseName: 'Жим под углом',
        sets: [
          { id: 's-009-5', weight: 70, reps: 10, completed: true },
          { id: 's-009-6', weight: 72.5, reps: 8, completed: true },
          { id: 's-009-7', weight: 72.5, reps: 7, completed: true }
        ]
      },
      {
        exerciseId: 'ex-023',
        exerciseName: 'Отжимания на брусьях',
        sets: [
          { id: 's-009-8', weight: 10, reps: 12, completed: true },
          { id: 's-009-9', weight: 10, reps: 11, completed: true },
          { id: 's-009-10', weight: 15, reps: 8, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-010',
    date: '2026-01-31',
    type: 'HIIT',
    title: 'HIIT тренировка',
    durationMinutes: 30,
    notes: 'Интенсивная круговая',
    createdAt: new Date('2026-01-31').getTime(),
    exercises: [
      {
        exerciseId: 'ex-034',
        exerciseName: 'Планка',
        sets: [
          { id: 's-010-1', weight: 0, reps: 60, completed: true },
          { id: 's-010-2', weight: 0, reps: 60, completed: true },
          { id: 's-010-3', weight: 0, reps: 45, completed: true }
        ]
      },
      {
        exerciseId: 'ex-037',
        exerciseName: 'Прыжки на скакалке',
        sets: [
          { id: 's-010-4', weight: 0, reps: 100, completed: true },
          { id: 's-010-5', weight: 0, reps: 100, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-011',
    date: '2026-01-28',
    type: 'Силовая',
    title: 'Спина и бицепс',
    durationMinutes: 60,
    notes: '',
    createdAt: new Date('2026-01-28').getTime(),
    exercises: [
      {
        exerciseId: 'ex-006',
        exerciseName: 'Становая тяга',
        sets: [
          { id: 's-011-1', weight: 115, reps: 5, completed: true },
          { id: 's-011-2', weight: 120, reps: 5, completed: true },
          { id: 's-011-3', weight: 120, reps: 4, completed: true }
        ]
      },
      {
        exerciseId: 'ex-007',
        exerciseName: 'Подтягивания',
        sets: [
          { id: 's-011-4', weight: 0, reps: 10, completed: true },
          { id: 's-011-5', weight: 0, reps: 9, completed: true },
          { id: 's-011-6', weight: 0, reps: 8, completed: true }
        ]
      },
      {
        exerciseId: 'ex-018',
        exerciseName: 'Молоток',
        sets: [
          { id: 's-011-7', weight: 20, reps: 12, completed: true },
          { id: 's-011-8', weight: 20, reps: 12, completed: true },
          { id: 's-011-9', weight: 22, reps: 10, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-012',
    date: '2026-01-24',
    type: 'Силовая',
    title: 'Ноги',
    durationMinutes: 72,
    notes: '',
    createdAt: new Date('2026-01-24').getTime(),
    exercises: [
      {
        exerciseId: 'ex-024',
        exerciseName: 'Приседания со штангой',
        sets: [
          { id: 's-012-1', weight: 95, reps: 8, completed: true },
          { id: 's-012-2', weight: 95, reps: 8, completed: true },
          { id: 's-012-3', weight: 100, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-029',
        exerciseName: 'Выпады с гантелями',
        sets: [
          { id: 's-012-4', weight: 20, reps: 12, completed: true },
          { id: 's-012-5', weight: 20, reps: 12, completed: true },
          { id: 's-012-6', weight: 22, reps: 10, completed: true }
        ]
      },
      {
        exerciseId: 'ex-031',
        exerciseName: 'Ягодичный мостик',
        sets: [
          { id: 's-012-7', weight: 80, reps: 12, completed: true },
          { id: 's-012-8', weight: 80, reps: 12, completed: true },
          { id: 's-012-9', weight: 90, reps: 10, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-013',
    date: '2026-01-20',
    type: 'Растяжка',
    title: 'Растяжка и восстановление',
    durationMinutes: 40,
    notes: 'Мышцы болят после тяжёлой недели',
    createdAt: new Date('2026-01-20').getTime(),
    exercises: []
  },
  {
    id: 'w-014',
    date: '2026-01-17',
    type: 'Силовая',
    title: 'Грудь и трицепс',
    durationMinutes: 60,
    notes: '',
    createdAt: new Date('2026-01-17').getTime(),
    exercises: [
      {
        exerciseId: 'ex-001',
        exerciseName: 'Жим лёжа',
        sets: [
          { id: 's-014-1', weight: 77.5, reps: 8, completed: true },
          { id: 's-014-2', weight: 80, reps: 7, completed: true },
          { id: 's-014-3', weight: 80, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-005',
        exerciseName: 'Отжимания',
        sets: [
          { id: 's-014-4', weight: 0, reps: 20, completed: true },
          { id: 's-014-5', weight: 0, reps: 18, completed: true },
          { id: 's-014-6', weight: 0, reps: 15, completed: true }
        ]
      },
      {
        exerciseId: 'ex-020',
        exerciseName: 'Жим узким хватом',
        sets: [
          { id: 's-014-7', weight: 60, reps: 10, completed: true },
          { id: 's-014-8', weight: 60, reps: 10, completed: true },
          { id: 's-014-9', weight: 65, reps: 8, completed: true }
        ]
      }
    ]
  },
  {
    id: 'w-015',
    date: '2025-12-29',
    type: 'Силовая',
    title: 'Последняя тренировка года',
    durationMinutes: 55,
    notes: 'Итоги года — чувствую прогресс!',
    createdAt: new Date('2025-12-29').getTime(),
    exercises: [
      {
        exerciseId: 'ex-001',
        exerciseName: 'Жим лёжа',
        sets: [
          { id: 's-015-1', weight: 75, reps: 8, completed: true },
          { id: 's-015-2', weight: 77.5, reps: 7, completed: true },
          { id: 's-015-3', weight: 77.5, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-024',
        exerciseName: 'Приседания со штангой',
        sets: [
          { id: 's-015-4', weight: 90, reps: 8, completed: true },
          { id: 's-015-5', weight: 90, reps: 7, completed: true },
          { id: 's-015-6', weight: 90, reps: 6, completed: true }
        ]
      },
      {
        exerciseId: 'ex-006',
        exerciseName: 'Становая тяга',
        sets: [
          { id: 's-015-7', weight: 110, reps: 5, completed: true },
          { id: 's-015-8', weight: 110, reps: 5, completed: true },
          { id: 's-015-9', weight: 115, reps: 4, completed: true }
        ]
      }
    ]
  }
]

/** @type {import('@/models/types').User} */
export const mockUser = {
  name: 'Александр',
  age: 28,
  avatarUrl: null,
  weightLog: [
    { date: '2025-11-01', kg: 84.0 },
    { date: '2025-12-01', kg: 82.5 },
    { date: '2026-01-05', kg: 81.0 },
    { date: '2026-01-20', kg: 80.5 },
    { date: '2026-02-01', kg: 80.0 },
    { date: '2026-02-15', kg: 79.5 },
    { date: '2026-03-01', kg: 79.0 }
  ],
  goals: [
    { id: 'g-1', text: 'Жим лёжа 100 кг', targetDate: '2026-06-01', done: false },
    { id: 'g-2', text: 'Похудеть до 77 кг', targetDate: '2026-07-01', done: false },
    { id: 'g-3', text: 'Становая тяга 150 кг', targetDate: '2026-09-01', done: false },
    { id: 'g-4', text: 'Тренироваться 3 раза в неделю', targetDate: '2026-04-01', done: false }
  ]
}
