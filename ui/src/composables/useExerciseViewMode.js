import { ref, watch } from 'vue'

const STORAGE_KEY = 'gym:exerciseViewMode'

function readInitial() {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'cards' ? 'cards' : 'standard'
  } catch {
    return 'standard'
  }
}

// Module-level singleton — one shared preference across the workout/template/plan editors
const mode = ref(readInitial())

watch(mode, (val) => {
  try { localStorage.setItem(STORAGE_KEY, val) } catch { /* ignore */ }
})

export function useExerciseViewMode() {
  return mode
}
