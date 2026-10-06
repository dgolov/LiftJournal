<template>
  <div>
    <!-- Scrolls sideways on phones, stretches to the card's full width from lg up -->
    <div class="heatmap-scroll overflow-x-auto lg:overflow-visible pb-1 -mx-1 px-1">
      <div class="min-w-max lg:min-w-0 lg:w-full">

        <!-- Month labels -->
        <div class="flex gap-0.5 mb-1 ml-7">
          <div
            v-for="(week, wi) in weeks"
            :key="wi"
            class="w-3 lg:flex-1 text-steel-700 dark:text-steel-300 overflow-visible whitespace-nowrap"
            style="font-size: 9px; line-height: 1.2"
          >{{ week.monthLabel }}</div>
        </div>

        <!-- Day labels + week columns -->
        <div class="flex gap-0.5">
          <div class="flex flex-col gap-0.5 mr-1 w-6 flex-shrink-0">
            <div
              v-for="(label, i) in dayLabels"
              :key="i"
              class="h-3 lg:h-auto lg:flex-1 flex items-center justify-end text-steel-700 dark:text-steel-300"
              style="font-size: 9px"
            >{{ label }}</div>
          </div>

          <div
            v-for="(week, wi) in weeks"
            :key="wi"
            class="flex flex-col gap-0.5 lg:flex-1"
          >
            <div
              v-for="(day, di) in week.days"
              :key="di"
              :class="['w-3 h-3 lg:w-full lg:h-auto lg:aspect-square rounded-[3px]', day ? cellColor(day.count) : 'invisible']"
              :title="day ? dayTitle(day) : ''"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-1 mt-2 justify-end text-steel-700 dark:text-steel-300" style="font-size: 10px">
      <span class="mr-0.5">Меньше</span>
      <div v-for="n in [0, 1, 2, 3, 4]" :key="n" :class="['w-3 h-3 rounded-[3px]', cellColor(n)]" />
      <span class="ml-0.5">Больше</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { toDateStr } from '@/components/calendar/calendarStyles.js'

const props = defineProps({
  activity: { type: Array, default: () => [] }, // [{ date: 'YYYY-MM-DD', count }]
})

const countByDate = computed(() => {
  const map = {}
  props.activity.forEach(a => { map[a.date] = (map[a.date] || 0) + a.count })
  return map
})

// 53 Monday-first weeks ending with the current one. Dates are built from
// local calendar days — toISOString() would shift them a day east of UTC.
const weeks = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const start = new Date(today)
  start.setDate(start.getDate() - ((start.getDay() + 6) % 7) - 52 * 7)

  const result = []
  let prevMonth = -1
  for (let w = 0; w < 53; w++) {
    const days = []
    for (let d = 0; d < 7; d++) {
      const date = new Date(start)
      date.setDate(start.getDate() + w * 7 + d)
      if (date > today) { days.push(null); continue }
      const dateStr = toDateStr(date)
      days.push({ dateStr, date, count: countByDate.value[dateStr] || 0 })
    }
    const weekStart = new Date(start)
    weekStart.setDate(start.getDate() + w * 7)
    let monthLabel = ''
    if (weekStart.getMonth() !== prevMonth) {
      monthLabel = weekStart.toLocaleDateString('ru-RU', { month: 'short' }).replace('.', '')
      prevMonth = weekStart.getMonth()
    }
    if (days.some(Boolean)) result.push({ days, monthLabel })
  }
  // A month that only gets a week or two at the edge (the grid starts
  // mid-month) would print its name on top of the next one — drop it.
  result.forEach((week, i) => {
    if (week.monthLabel && result.slice(i + 1, i + 3).some(w => w.monthLabel)) week.monthLabel = ''
  })
  return result
})

const dayLabels = ['Пн', '', 'Ср', '', 'Пт', '', 'Вс']

// The app's red, in four strengths; empty days sit back in the card's grey.
function cellColor(count) {
  if (count === 0) return 'bg-steel-100 dark:bg-steel-700/60'
  if (count === 1) return 'bg-primary/30'
  if (count === 2) return 'bg-primary/55'
  if (count === 3) return 'bg-primary/80'
  return 'bg-primary'
}

function dayTitle(day) {
  const label = day.date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
  if (day.count === 0) return `${label}: нет тренировок`
  const n = day.count, m10 = n % 10, m100 = n % 100
  const word = m10 === 1 && m100 !== 11 ? 'тренировка' : m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20) ? 'тренировки' : 'тренировок'
  return `${label}: ${n} ${word}`
}
</script>

<style scoped>
.heatmap-scroll::-webkit-scrollbar { height: 3px; }
.heatmap-scroll::-webkit-scrollbar-track { background: transparent; }
.heatmap-scroll::-webkit-scrollbar-thumb { background: rgba(174, 180, 192, 0.35); border-radius: 2px; }
.heatmap-scroll::-webkit-scrollbar-thumb:hover { background: rgba(174, 180, 192, 0.6); }
</style>
