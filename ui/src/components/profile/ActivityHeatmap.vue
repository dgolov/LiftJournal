<template>
  <div>
    <div class="heatmap-scroll overflow-x-auto lg:overflow-visible pb-1 -mx-1 px-1">
      <div class="min-w-max lg:min-w-0 lg:w-full">

        <!-- Month labels -->
        <div class="flex gap-0.5 mb-1 ml-7">
          <div
            v-for="(week, wi) in weeks"
            :key="wi"
            class="w-3 lg:flex-1 text-gray-400 dark:text-gray-500 overflow-hidden"
            style="font-size: 9px; line-height: 1.2"
          >{{ week.monthLabel }}</div>
        </div>

        <!-- Day labels + week columns -->
        <div class="flex gap-0.5">

          <!-- Day labels -->
          <div class="flex flex-col gap-0.5 mr-1 w-6 flex-shrink-0">
            <div
              v-for="(label, i) in dayLabels"
              :key="i"
              class="h-3 text-gray-400 dark:text-gray-500 text-right leading-3"
              style="font-size: 9px"
            >{{ label }}</div>
          </div>

          <!-- Week columns -->
          <div
            v-for="(week, wi) in weeks"
            :key="wi"
            class="flex flex-col gap-0.5 lg:flex-1"
          >
            <div
              v-for="(day, di) in week.days"
              :key="di"
              :class="['w-3 h-3 lg:w-full lg:h-auto lg:aspect-square rounded-sm transition-colors',
                day ? cellColor(day.count) : 'invisible']"
              :title="day ? dayTitle(day) : ''"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-1 mt-2 justify-end">
      <span class="text-gray-400 mr-0.5" style="font-size: 10px">Меньше</span>
      <div v-for="c in legendColors" :key="c" :class="['w-3 h-3 rounded-sm', c]" />
      <span class="text-gray-400 ml-0.5" style="font-size: 10px">Больше</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const allWorkouts = computed(() => store.getters['workouts/allWorkouts'])

function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const workoutCountByDate = computed(() => {
  const map = {}
  for (const w of allWorkouts.value) {
    map[w.date] = (map[w.date] || 0) + 1
  }
  return map
})

const weeks = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const startDay = new Date(today)
  const dow = (startDay.getDay() + 6) % 7
  startDay.setDate(startDay.getDate() - dow - 52 * 7)

  const result = []
  let prevMonth = -1

  for (let w = 0; w < 53; w++) {
    const days = []
    let monthLabel = ''

    for (let d = 0; d < 7; d++) {
      const date = new Date(startDay)
      date.setDate(startDay.getDate() + w * 7 + d)
      if (date > today) { days.push(null); continue }
      const dateStr = toDateStr(date)
      days.push({ dateStr, count: workoutCountByDate.value[dateStr] || 0, date })
    }

    const weekStart = new Date(startDay)
    weekStart.setDate(startDay.getDate() + w * 7)
    if (weekStart.getMonth() !== prevMonth) {
      monthLabel = weekStart.toLocaleDateString('ru-RU', { month: 'short' }).replace('.', '')
      prevMonth = weekStart.getMonth()
    }

    if (days.some(d => d !== null)) result.push({ days, monthLabel })
  }

  return result
})

const dayLabels = ['Пн', '', 'Ср', '', 'Пт', '', 'Вс']

function cellColor(count) {
  if (count === 0) return 'bg-gray-100 dark:bg-gray-800'
  if (count === 1) return 'bg-indigo-200 dark:bg-indigo-900'
  if (count === 2) return 'bg-indigo-400 dark:bg-indigo-600'
  return 'bg-indigo-600 dark:bg-indigo-400'
}

const legendColors = [
  'bg-gray-100 dark:bg-gray-800',
  'bg-indigo-200 dark:bg-indigo-900',
  'bg-indigo-400 dark:bg-indigo-600',
  'bg-indigo-600 dark:bg-indigo-400',
]

function dayTitle(day) {
  const label = day.date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
  return day.count === 0 ? label + ' — нет тренировок' : label + ` — ${day.count} тр.`
}
</script>

<style scoped>
.heatmap-scroll::-webkit-scrollbar {
  height: 3px;
}
.heatmap-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.heatmap-scroll::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.35);
  border-radius: 2px;
}
.heatmap-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.6);
}
</style>
