import { ref, computed } from 'vue'

// Module-level singleton — one timer shared across all components
const active = ref(false)
const remaining = ref(0)
const total = ref(90)
let _interval = null

function start(seconds) {
  const secs = seconds ?? total.value
  clearInterval(_interval)
  total.value = secs
  remaining.value = secs
  active.value = true
  _interval = setInterval(() => {
    remaining.value--
    if (remaining.value <= 0) {
      clearInterval(_interval)
      active.value = false
      if (navigator.vibrate) navigator.vibrate([150, 80, 150])
    }
  }, 1000)
}

function stop() {
  clearInterval(_interval)
  active.value = false
  remaining.value = 0
}

function adjust(delta) {
  remaining.value = Math.max(5, Math.min(remaining.value + delta, 600))
  if (remaining.value > total.value) total.value = remaining.value
}

const progress = computed(() => (total.value > 0 ? remaining.value / total.value : 0))

const formatted = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

export function useRestTimer() {
  return { active, remaining, total, progress, formatted, start, stop, adjust }
}
