<template>
  <div :class="['card p-4', pinned ? 'sticky z-20 shadow-lift top-[calc(4.5rem+env(safe-area-inset-top))]' : '']">
    <div class="flex items-start justify-between gap-3 flex-wrap mb-3">
      <div>
        <h3 class="font-semibold text-ink dark:text-white">Нагрузка по циклу</h3>
        <p v-if="!pinned" class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">
          По процентам от 1ПМ, подходы легче 50% не считаются.
          <template v-if="!mainExercises.length">Отметьте основные упражнения ★, чтобы видеть только их.</template>
        </p>
      </div>
      <div class="flex items-center gap-2">
      <button
        v-if="pinnable"
        type="button"
        :class="['p-2 rounded-lg border transition-colors', pinned ? 'bg-primary/10 border-primary/30 text-primary' : 'border-steel-100 dark:border-steel-700 text-steel-700 dark:text-steel-300 hover:border-steel-300']"
        :aria-pressed="pinned"
        :title="pinned ? 'Открепить график' : 'Закрепить график при прокрутке таблицы'"
        @click="pinned = !pinned"
      ><Pin class="w-4 h-4" /></button>
      <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5">
        <button
          v-for="m in metrics" :key="m.value" type="button"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors', segClass(metric === m.value)]"
          @click="metric = m.value"
        >{{ m.label }}</button>
      </div>
      </div>
    </div>

    <p v-if="!lifts.length" class="text-sm text-steel-700 dark:text-steel-300 py-6 text-center">
      Добавьте упражнению подходы с процентами или отметьте основные ★ — здесь появятся графики.
    </p>

    <template v-else>
      <!-- Which lift -->
      <div v-if="lifts.length > 1" class="flex flex-wrap gap-1.5 mb-3">
        <button
          v-for="l in lifts" :key="l" type="button"
          :class="['px-3 py-1 rounded-full text-sm border transition-colors',
            current === l ? 'bg-primary/10 border-primary/30 text-primary font-medium' : 'border-steel-100 dark:border-steel-700 text-steel-700 dark:text-steel-300 hover:border-steel-300']"
          @click="selected = l"
        >{{ l }}</button>
      </div>

      <!-- Cycle totals for the lift -->
      <div v-if="!pinned" class="flex flex-wrap items-baseline gap-x-5 gap-y-1 mb-3 text-sm tabular-nums">
        <span class="text-steel-700 dark:text-steel-300">КПШ за цикл <strong class="text-ink dark:text-white">{{ summary.lifts }}</strong></span>
        <span v-if="summary.avgPercent != null" class="text-steel-700 dark:text-steel-300">средняя интенсивность <strong class="text-ink dark:text-white">{{ summary.avgPercent }}%</strong></span>
        <span class="text-steel-700 dark:text-steel-300">тренировок <strong class="text-ink dark:text-white">{{ summary.sessions }}</strong></span>
      </div>
      <!-- Share of lifts per zone, the whole cycle at a glance -->
      <div v-if="summary.lifts && !pinned" class="mb-4">
        <div class="flex h-2 rounded-full overflow-hidden bg-steel-100 dark:bg-steel-700">
          <div
            v-for="(share, zi) in summary.zoneShare" :key="zi"
            :style="{ width: share + '%', background: ZONE_COLORS[zi] }"
            :title="`${ZONES[zi].label}: ${share}% подъёмов`"
          />
        </div>
        <div class="flex flex-wrap gap-x-3 gap-y-1 mt-1.5 text-xs text-steel-700 dark:text-steel-300 tabular-nums">
          <span v-for="(z, zi) in ZONES" :key="zi" class="inline-flex items-center gap-1">
            <span class="w-2 h-2 rounded-sm" :style="{ background: ZONE_COLORS[zi] }" />{{ z.label }} — {{ summary.zoneShare[zi] }}%
          </span>
        </div>
      </div>

      <div v-if="summary.lifts" :class="pinned ? 'h-36' : 'h-56 sm:h-64'">
        <Line :data="chartData" :options="chartOptions" />
      </div>
      <p v-else class="text-sm text-steel-700 dark:text-steel-300 py-6 text-center">
        У «{{ current }}» пока нет рабочих подходов — добавьте в таблице подходы от 50% 1ПМ, и график появится.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Pin } from 'lucide-vue-next'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, LineElement, PointElement, BarElement, BarController,
  LinearScale, CategoryScale, Tooltip, Legend,
} from 'chart.js'
import { ZONES, planLoadFor, planSummary } from '@/utils/cyclePlan.js'

ChartJS.register(LineElement, PointElement, BarElement, BarController, LinearScale, CategoryScale, Tooltip, Legend)

const props = defineProps({
  // Cycle workouts in API shape: [{ exercises: [{ exercise_name, sets: [{ percent_1rm, reps }] }] }]
  workouts: { type: Array, required: true },
  mainExercises: { type: Array, default: () => [] },   // [{ exerciseName }]
  // In the editor the chart can stick above the table while you scroll it.
  pinnable: { type: Boolean, default: false },
})

// Pinned: a compact chart that follows the viewport while sets are edited.
const pinned = ref(false)

// Light to full brand red, one step per 10% zone.
const ZONE_COLORS = ['#F6C9CC', '#EE9AA0', '#E56B73', '#D92D3A', '#8F1C26']
const PLAN = '#D92D3A'
const TOP = '#4B5260'

const metrics = [
  { value: 'intensity', label: 'Интенсивность' },
  { value: 'lifts', label: 'КПШ' },
  { value: 'zones', label: 'Зоны' },
]
const metric = ref('intensity')
function segClass(active) {
  return active
    ? 'bg-card text-primary shadow-soft dark:bg-steel-700'
    : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white'
}

// Every lift marked main — shown straight away, even before it has any sets,
// so marking one visibly does something. Without any marked: every lift with
// working (≥50%) sets.
const lifts = computed(() => {
  const main = [...new Set(props.mainExercises.map(m => m.exerciseName).filter(Boolean))]
  if (main.length) return main
  const withLoad = new Set()
  props.workouts.forEach(w => w.exercises.forEach(e => {
    if (e.sets.some(s => Number(s.percent_1rm) >= 50)) withLoad.add(e.exercise_name)
  }))
  return [...withLoad]
})
const selected = ref(null)
const current = computed(() => lifts.value.includes(selected.value) ? selected.value : lifts.value[0])

const points = computed(() => current.value ? planLoadFor(props.workouts, current.value) : [])
const summary = computed(() => planSummary(points.value))
// "Т3" alone, or "Т3" over a short name ("Тяжёлый жим") on a second line.
function shortName(title) {
  const t = (title || '').trim()
  return t.length > 14 ? `${t.slice(0, 13)}…` : t
}
const labels = computed(() => props.workouts.map((w, i) => (w.title?.trim() ? [`Т${i + 1}`, shortName(w.title)] : `Т${i + 1}`)))

const chartData = computed(() => {
  const val = f => points.value.map(p => (p ? f(p) : null))
  if (metric.value === 'lifts') {
    return {
      labels: labels.value,
      datasets: [{ type: 'bar', label: 'КПШ', data: val(p => p.lifts), backgroundColor: 'rgba(217,45,58,0.8)', borderRadius: 6, maxBarThickness: 26 }],
    }
  }
  if (metric.value === 'zones') {
    return {
      labels: labels.value,
      datasets: ZONES.map((z, zi) => ({
        type: 'bar', label: z.label, data: val(p => p.zones[zi] || null),
        backgroundColor: ZONE_COLORS[zi], stack: 'zones', maxBarThickness: 26,
      })),
    }
  }
  return {
    labels: labels.value,
    datasets: [
      { label: 'Средняя интенсивность', data: val(p => p.avgPercent), borderColor: PLAN, backgroundColor: PLAN, borderWidth: 2, pointRadius: 4, tension: 0.3, spanGaps: true },
      { label: 'Самый тяжёлый подход', data: val(p => p.topPercent), borderColor: TOP, backgroundColor: TOP, borderDash: [5, 4], borderWidth: 1.5, pointRadius: 2, tension: 0.3, spanGaps: true },
    ],
  }
})

const chartOptions = computed(() => {
  const isPercent = metric.value === 'intensity'
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 200 },   // redrawn on every edit — keep it snappy
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true, font: { size: 12 } } },
      tooltip: {
        filter: item => item.parsed.y != null,
        callbacks: {
          title: items => {
            const i = items[0]?.dataIndex
            const name = props.workouts[i]?.title?.trim()
            return name ? `Т${i + 1} · ${name}` : `Т${i + 1}`
          },
          label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}${isPercent ? '%' : metric.value === 'zones' ? ' подъёмов' : ''}`,
        },
      },
    },
    scales: {
      x: { stacked: metric.value === 'zones', grid: { display: false }, ticks: { font: { size: 11 } } },
      y: {
        stacked: metric.value === 'zones',
        beginAtZero: !isPercent,
        suggestedMin: isPercent ? 50 : undefined,
        suggestedMax: isPercent ? 100 : undefined,
        grid: { color: 'rgba(127,134,150,0.12)' },
        ticks: { font: { size: 11 }, callback: v => (isPercent ? `${v}%` : v) },
      },
    },
  }
})
</script>
