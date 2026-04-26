<template>
  <div>
    <!-- Month labels -->
    <div class="flex mb-1 ml-7">
      <template v-for="(m, i) in monthLabels" :key="i">
        <span
          class="text-xs text-gray-400 flex-shrink-0"
          :style="{ width: m.weeks * (cellSize + gap) + 'px' }"
        >{{ m.label }}</span>
      </template>
    </div>

    <div class="flex gap-0 items-start">
      <!-- Day-of-week labels -->
      <div class="flex flex-col mr-1.5" :style="{ gap: gap + 'px' }">
        <div
          v-for="(d, i) in dayLabels"
          :key="i"
          class="text-xs text-gray-400 leading-none flex items-center justify-end"
          :style="{ height: cellSize + 'px', width: '20px' }"
        >{{ d }}</div>
      </div>

      <!-- Grid -->
      <div class="flex overflow-x-auto pb-1" :style="{ gap: gap + 'px' }">
        <div
          v-for="(week, wi) in grid"
          :key="wi"
          class="flex flex-col flex-shrink-0"
          :style="{ gap: gap + 'px' }"
        >
          <div
            v-for="(day, di) in week"
            :key="di"
            :class="['rounded-sm transition-opacity', day.future ? 'opacity-0' : '', cellColor(day.count)]"
            :style="{ width: cellSize + 'px', height: cellSize + 'px' }"
            :title="day.date && !day.future ? tooltipText(day) : undefined"
          />
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-1 mt-2 justify-end text-xs text-gray-400">
      <span>меньше</span>
      <div v-for="n in [0,1,2,3,4]" :key="n" :class="['rounded-sm', cellColor(n)]" :style="{ width: '11px', height: '11px' }" />
      <span>больше</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  activity: { type: Array, default: () => [] }, // [{date:'YYYY-MM-DD', count:N}]
})

const cellSize = 12
const gap = 2

const activityMap = computed(() => {
  const m = {}
  props.activity.forEach(a => { m[a.date] = a.count })
  return m
})

// Build 53-week grid ending today
const grid = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // Go back to the Monday of the week 52 weeks ago
  const start = new Date(today)
  start.setDate(start.getDate() - 364)
  // Align to Monday (1)
  const dow = start.getDay() || 7  // Sun=0 → 7
  start.setDate(start.getDate() - (dow - 1))

  const weeks = []
  const cur = new Date(start)

  while (cur <= today || weeks.length < 53) {
    const week = []
    for (let d = 0; d < 7; d++) {
      const dateStr = cur.toISOString().slice(0, 10)
      week.push({
        date: dateStr,
        count: activityMap.value[dateStr] || 0,
        future: cur > today,
      })
      cur.setDate(cur.getDate() + 1)
    }
    weeks.push(week)
    if (cur > today && weeks.length >= 52) break
  }
  return weeks
})

const monthLabels = computed(() => {
  const labels = []
  let lastMonth = null
  let currentLabel = null

  grid.value.forEach(week => {
    const monthDay = week.find(d => !d.future)
    if (!monthDay) return
    const m = new Date(monthDay.date).getMonth()
    if (m !== lastMonth) {
      if (currentLabel) labels.push(currentLabel)
      currentLabel = { label: new Date(monthDay.date).toLocaleDateString('ru-RU', { month: 'short' }), weeks: 1 }
      lastMonth = m
    } else {
      if (currentLabel) currentLabel.weeks++
    }
  })
  if (currentLabel) labels.push(currentLabel)
  return labels
})

const dayLabels = ['Пн', '', 'Ср', '', 'Пт', '', '']

function cellColor(count) {
  if (count === 0) return 'bg-gray-100 dark:bg-gray-800'
  if (count === 1) return 'bg-primary/30'
  if (count === 2) return 'bg-primary/55'
  if (count === 3) return 'bg-primary/80'
  return 'bg-primary'
}

function tooltipText(day) {
  const d = new Date(day.date + 'T00:00:00')
  const label = d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
  if (day.count === 0) return label + ': нет тренировок'
  return `${label}: ${day.count} тренировка${day.count === 1 ? '' : day.count < 5 ? 'и' : ''}`
}
</script>
