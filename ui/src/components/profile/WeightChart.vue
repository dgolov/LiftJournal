<template>
  <div v-if="data.length > 1">
    <Line :data="chartData" :options="chartOptions" />
  </div>
  <div v-else class="flex items-center justify-center h-24 text-sm text-gray-400">
    Нет данных о весе
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Filler
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const props = defineProps({
  data: { type: Array, default: () => [] } // [ { date, kg } ]
})

const chartData = computed(() => ({
  labels: props.data.map(d => {
    const date = new Date(d.date + 'T00:00:00')
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  }),
  datasets: [{
    label: 'Вес (кг)',
    data: props.data.map(d => d.kg),
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99,102,241,0.1)',
    fill: true,
    tension: 0.4,
    pointRadius: 4,
    pointBackgroundColor: '#6366f1'
  }]
}))

const chartOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
    y: {
      grid: { color: 'rgba(0,0,0,0.05)' },
      ticks: { font: { size: 11 } },
      min: ctx => {
        const values = ctx.chart.data.datasets[0].data
        if (!values.length) return 0
        return Math.floor(Math.min(...values) - 2)
      }
    }
  }
}
</script>
