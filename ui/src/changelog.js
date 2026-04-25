// Add a new entry here whenever you bump the version in package.json.
// Types: 'feature' | 'fix' | 'improvement'

export const CHANGELOG = [
  {
    version: '1.0.0',
    date: '2026-04-22',
    label: 'Первый релиз',
    entries: [
      { type: 'feature', text: 'Дашборд: стрик, тоннаж за месяц, личные рекорды' },
      { type: 'feature', text: 'Сравнение месяц-к-месяцу: тоннаж, тренировки, среднее время' },
      { type: 'feature', text: 'Свайп влево для удаления тренировок, упражнений и планов' },
      { type: 'feature', text: 'Неуспешные подходы — зачёркнуты, не учитываются в 1ПМ и тоннаже' },
      { type: 'feature', text: 'Автозаполнение весов из последней тренировки с этим упражнением' },
      { type: 'feature', text: 'История упражнения: таблица, фильтры, сортировка, пагинация' },
      { type: 'feature', text: 'Планирование тренировок с поддержкой повторяющихся событий' },
      { type: 'feature', text: 'Тренировочные циклы с процентами от 1ПМ' },
      { type: 'feature', text: 'Тёмная тема' },
    ],
  },
]
