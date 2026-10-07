<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, LineElement, PointElement, BarElement, BarController,
  LinearScale, CategoryScale, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, BarElement, BarController, LinearScale, CategoryScale, Tooltip, Legend)

// points: [{ label, plan: session|null, fact: session|null }] in cycle order
const props = defineProps({
  points: { type: Array, required: true },
  metric: { type: String, default: 'intensity' },   // intensity | lifts | tonnage
})

const PLAN = '#AEB4C0'
const FACT = '#D92D3A'

const METRICS = {
  intensity: { key: 'relIntensity', unit: '%', label: 'отн. интенсивность', kind: 'line' },
  lifts: { key: 'lifts', unit: '', label: 'КПШ', kind: 'bar' },
  tonnage: { key: 'totalVolume', unit: ' кг', label: 'тоннаж', kind: 'bar' },
}
const m = computed(() => METRICS[props.metric])

const chartData = computed(() => {
  const value = side => props.points.map(p => p[side]?.[m.value.key] ?? null)
  if (m.value.kind === 'bar') {
    return {
      labels: props.points.map(p => p.label),
      datasets: [
        { type: 'bar', label: 'План', data: value('plan'), backgroundColor: 'rgba(174,180,192,0.45)', borderRadius: 6, maxBarThickness: 22 },
        { type: 'bar', label: 'Факт', data: value('fact'), backgroundColor: 'rgba(217,45,58,0.8)', borderRadius: 6, maxBarThickness: 22 },
      ],
    }
  }
  return {
    labels: props.points.map(p => p.label),
    datasets: [
      { label: 'План', data: value('plan'), borderColor: PLAN, backgroundColor: PLAN, borderDash: [6, 4], borderWidth: 2, pointRadius: 3, tension: 0.3, spanGaps: true },
      { label: 'Факт', data: value('fact'), borderColor: FACT, backgroundColor: FACT, borderWidth: 2, pointRadius: 4, tension: 0.3, spanGaps: false },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2.4,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true, font: { size: 12 } } },
    tooltip: {
      callbacks: {
        title: items => props.points[items[0].dataIndex]?.title,
        label: ctx => ctx.parsed.y == null ? `${ctx.dataset.label}: —` : `${ctx.dataset.label}: ${ctx.parsed.y}${m.value.unit}`,
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
    y: {
      beginAtZero: m.value.kind === 'bar',
      grid: { color: 'rgba(127,134,150,0.12)' },
      ticks: { font: { size: 11 }, callback: v => `${v}${m.value.unit === '%' ? '%' : ''}` },
    },
  },
}))
</script>
