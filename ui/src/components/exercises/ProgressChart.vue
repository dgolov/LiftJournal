<template>
  <div v-if="data.length > 1">
    <Line :data="chartData" :options="chartOptions" />
  </div>
  <div v-else class="flex items-center justify-center h-32 text-sm text-gray-400">
    Недостаточно данных для графика (нужно минимум 2 сессии)
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
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler)

const props = defineProps({
  data: { type: Array, default: () => [] } // [ { date, maxWeight, totalVolume } ]
})

const labels = computed(() =>
  props.data.map(d => {
    const date = new Date(d.date + 'T00:00:00')
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  })
)

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Макс. вес (кг)',
      data: props.data.map(d => d.maxWeight),
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99, 102, 241, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: '#6366f1'
    },
    {
      label: 'Объём (кг)',
      data: props.data.map(d => d.totalVolume),
      borderColor: '#22c55e',
      backgroundColor: 'transparent',
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: '#22c55e',
      yAxisID: 'y1'
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 12 } } }
  },
  scales: {
    x: { grid: { display: false } },
    y: {
      position: 'left',
      grid: { color: 'rgba(0,0,0,0.05)' },
      ticks: { font: { size: 11 } }
    },
    y1: {
      position: 'right',
      grid: { display: false },
      ticks: { font: { size: 11 } }
    }
  }
}
</script>
