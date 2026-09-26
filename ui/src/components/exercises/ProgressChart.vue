<template>
  <div>
    <div v-if="!isCardio" class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5 mb-4">
      <button
        v-for="m in metrics" :key="m.value"
        :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
          metric === m.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white']"
        @click="metric = m.value"
      >{{ m.label }}</button>
    </div>

    <div v-if="data.length > 1">
      <Line :data="chartData" :options="chartOptions" />
      <p v-if="!isCardio" class="text-xs text-steel-300 dark:text-steel-700 mt-3">{{ metricHint }}</p>
    </div>
    <div v-else class="flex items-center justify-center h-32 text-sm text-steel-300">
      Недостаточно данных для графика (нужно минимум 2 сессии)
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  BarElement,
  BarController,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(LineElement, PointElement, BarElement, BarController, LinearScale, CategoryScale, Tooltip, Legend, Filler)

const props = defineProps({
  // strength: sessions from exercises/progressForExercise; cardio: [ { date, totalMinutes } ]
  data: { type: Array, default: () => [] },
  isCardio: { type: Boolean, default: false }
})

const COLORS = {
  primary: '#D92D3A',
  steel: '#4B5260',
  steelLight: '#AEB4C0',
  success: '#2F9E6B',
  hazard: '#F0B429',
}

const metrics = [
  { value: 'orm', label: '1ПМ' },
  { value: 'volume', label: 'Объём' },
  { value: 'intensity', label: 'Интенсивность' },
]
const metric = ref('orm')

const metricHint = computed(() => ({
  orm: 'Расчётный 1ПМ по формуле Эпли. Если у подхода указан RPE, к повторам добавляется запас до отказа (10 − RPE).',
  volume: 'Тоннаж — сумма вес × повторы, КПШ — количество подъёмов штанги. Проваленные подходы не учитываются.',
  intensity: 'Абсолютная — средний вес подъёма (тоннаж / КПШ). Относительная — он же в % от 1ПМ: из профиля или лучшего расчётного на дату тренировки.',
})[metric.value])

const labels = computed(() =>
  props.data.map(d => {
    const date = new Date(d.date + 'T00:00:00')
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  })
)

function line(label, key, color, extra = {}) {
  return {
    label,
    data: props.data.map(d => d[key]),
    borderColor: color,
    backgroundColor: color,
    tension: 0.35,
    pointRadius: 3,
    pointHoverRadius: 5,
    borderWidth: 2,
    spanGaps: true,
    ...extra
  }
}

const chartData = computed(() => {
  if (props.isCardio) {
    return {
      labels: labels.value,
      datasets: [line('Продолжительность (мин.)', 'totalMinutes', COLORS.primary, { fill: true, backgroundColor: 'rgba(217,45,58,0.08)' })]
    }
  }
  if (metric.value === 'volume') {
    return {
      labels: labels.value,
      datasets: [
        line('КПШ', 'lifts', COLORS.primary, { yAxisID: 'y1', order: 0 }),
        {
          type: 'bar',
          label: 'Тоннаж (кг)',
          data: props.data.map(d => d.totalVolume),
          backgroundColor: 'rgba(174,180,192,0.45)',
          hoverBackgroundColor: 'rgba(174,180,192,0.7)',
          borderRadius: 6,
          maxBarThickness: 28,
          order: 1
        }
      ]
    }
  }
  if (metric.value === 'intensity') {
    return {
      labels: labels.value,
      datasets: [
        line('Средний вес (кг)', 'avgWeight', COLORS.steel),
        line('Отн. интенсивность (%)', 'relIntensity', COLORS.primary, { yAxisID: 'y1' }),
        line('Топ-подход (% 1ПМ)', 'topSetIntensity', COLORS.primary, { yAxisID: 'y1', borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5 })
      ]
    }
  }
  return {
    labels: labels.value,
    datasets: [
      line('Расч. 1ПМ (кг)', 'best1RM', COLORS.primary, { fill: true, backgroundColor: 'rgba(217,45,58,0.08)' }),
      line('Макс. вес (кг)', 'maxWeight', COLORS.steel)
    ]
  }
})

const UNITS = {
  'КПШ': '', 'Тоннаж (кг)': ' кг', 'Средний вес (кг)': ' кг',
  'Отн. интенсивность (%)': '%', 'Топ-подход (% 1ПМ)': '%',
  'Расч. 1ПМ (кг)': ' кг', 'Макс. вес (кг)': ' кг', 'Продолжительность (мин.)': ' мин.'
}

const hasRightAxis = computed(() => !props.isCardio && metric.value !== 'orm')

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true, font: { size: 12 } } },
    tooltip: {
      callbacks: {
        label: ctx => ctx.parsed.y == null ? null : `${ctx.dataset.label.replace(/ \(.*\)$/, '')}: ${ctx.parsed.y}${UNITS[ctx.dataset.label] ?? ''}`
      }
    }
  },
  scales: {
    x: { grid: { display: false } },
    y: {
      position: 'left',
      beginAtZero: metric.value === 'volume',
      grid: { color: 'rgba(127,134,150,0.12)' },
      ticks: { font: { size: 11 } }
    },
    ...(hasRightAxis.value ? {
      y1: {
        position: 'right',
        beginAtZero: metric.value === 'volume',
        suggestedMax: metric.value === 'intensity' ? 100 : undefined,
        grid: { display: false },
        ticks: {
          font: { size: 11 },
          callback: v => metric.value === 'intensity' ? `${v}%` : v
        }
      }
    } : {})
  }
}))
</script>
