// Shared look of the training calendars (history, coach's athlete view):
// done workouts are tinted by workout type, plans by status — a skipped plan
// must not read the same as an upcoming one.

export const workoutChipClasses = {
  'Силовая': 'bg-primary/15 text-primary dark:bg-primary/25',
  'Кардио': 'bg-success/15 text-success dark:bg-success/25',
  'Растяжка': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  'HIIT': 'bg-hazard/20 text-hazard dark:bg-hazard/25',
  'Другое': 'bg-steel-100 text-steel-700 dark:bg-steel-700 dark:text-steel-300',
}

export const planChipClasses = {
  planned: 'bg-hazard/20 text-hazard dark:bg-hazard/25',
  completed: 'bg-success/15 text-success dark:bg-success/25',
  skipped: 'bg-steel-100 text-steel-300 dark:bg-steel-700',
}

// item: { kind: 'workout', type } | { kind: 'plan', status }
export function chipClass(item) {
  if (item.kind === 'workout') return workoutChipClasses[item.type] || workoutChipClasses['Другое']
  return planChipClasses[item.status] || planChipClasses.planned
}

export function cellClass(day, selectedDate) {
  if (day.dateStr === selectedDate) return 'bg-primary/10 dark:bg-primary/15'
  if (!day.isCurrentMonth) return 'bg-steel-50 dark:bg-steel-950/60'
  return 'bg-card dark:bg-steel-900 hover:bg-steel-50 dark:hover:bg-steel-700/60 transition-colors'
}

export function dayNumberClass(day, todayStr) {
  const base = 'w-5 h-5 flex items-center justify-center rounded-full text-xs font-mono flex-shrink-0'
  if (day.dateStr === todayStr) return `${base} bg-primary text-white font-bold`
  if (!day.isCurrentMonth) return `${base} text-steel-300 dark:text-steel-700`
  return `${base} text-steel-700 dark:text-steel-300`
}

export function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// Monday-first month grid padded with the neighbouring months' days.
export function monthDays(year, month) {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startOffset = (firstDay.getDay() + 6) % 7
  const days = []
  for (let i = 0; i < startOffset; i++) {
    const d = new Date(year, month, 1 - startOffset + i)
    days.push({ date: d, isCurrentMonth: false, dateStr: toDateStr(d) })
  }
  for (let n = 1; n <= lastDay.getDate(); n++) {
    const d = new Date(year, month, n)
    days.push({ date: d, isCurrentMonth: true, dateStr: toDateStr(d) })
  }
  const tail = (7 - days.length % 7) % 7
  for (let i = 1; i <= tail; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ date: d, isCurrentMonth: false, dateStr: toDateStr(d) })
  }
  return days
}

export const WEEK_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
