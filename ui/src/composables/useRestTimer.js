import { ref, computed } from 'vue'

// Module-level singleton — one timer shared across all components
const active = ref(false)
const remaining = ref(0)
const total = ref(90)
let _interval = null
let _startedAt = 0      // Date.now() when current countdown segment began
let _startRemaining = 0 // remaining.value at that moment

function _tick() {
  const elapsed = Math.floor((Date.now() - _startedAt) / 1000)
  const next = _startRemaining - elapsed
  if (next <= 0) {
    remaining.value = 0
    clearInterval(_interval)
    active.value = false
    if (navigator.vibrate) navigator.vibrate([150, 80, 150])
  } else {
    remaining.value = next
  }
}

function _onVisibilityChange() {
  if (!document.hidden && active.value) _tick()
}

function start(seconds) {
  const secs = seconds ?? total.value
  clearInterval(_interval)
  total.value = secs
  remaining.value = secs
  _startedAt = Date.now()
  _startRemaining = secs
  active.value = true
  _interval = setInterval(_tick, 500)
}

function stop() {
  clearInterval(_interval)
  active.value = false
  remaining.value = 0
}

function adjust(delta) {
  const next = Math.max(5, Math.min(remaining.value + delta, 600))
  remaining.value = next
  if (next > total.value) total.value = next
  // Reset anchor so diff is calculated from the new value
  _startedAt = Date.now()
  _startRemaining = next
}

const progress = computed(() => (total.value > 0 ? remaining.value / total.value : 0))

const formatted = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

document.addEventListener('visibilitychange', _onVisibilityChange)

export function useRestTimer() {
  return { active, remaining, total, progress, formatted, start, stop, adjust }
}
