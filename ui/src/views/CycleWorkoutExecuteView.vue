<template>
  <div class="max-w-2xl">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1">
        <p class="text-xs text-gray-400 font-medium">{{ cycleName }}</p>
        <h2 class="text-xl font-bold text-gray-900">{{ workout?.title }}</h2>
      </div>
      <div class="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full">
        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0"></span>
        <span class="font-mono font-bold text-primary text-sm">{{ elapsedFormatted }}</span>
      </div>
    </div>

    <div v-if="workout" class="space-y-4">
      <!-- Exercises -->
      <div v-for="ex in workout.exercises" :key="ex.exerciseId" class="card p-4">
        <h3 class="font-semibold text-gray-900 mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <button
            v-for="(set, i) in ex.sets"
            :key="set.id"
            :class="['w-full flex items-center gap-3 p-2.5 rounded-xl border-2 transition-all text-left',
              localCompleted.has(set.id)
                ? 'border-green-400 bg-green-50'
                : 'border-gray-100 hover:border-primary/40']"
            @click="toggleSet(set.id)"
          >
            <span :class="['w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors',
              localCompleted.has(set.id) ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 text-gray-300']">
              {{ localCompleted.has(set.id) ? '✓' : i + 1 }}
            </span>
            <span class="font-semibold text-gray-800">
              {{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}
            </span>
            <span class="text-gray-400">×</span>
            <span class="text-gray-700">{{ set.reps }} повт.</span>
            <span v-if="localCompleted.has(set.id)" class="ml-auto text-xs text-green-600 font-medium">выполнен</span>
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-2">
          {{ localCompleted.size }} / {{ totalSets }} подходов выполнено
        </p>
      </div>

      <!-- Notes -->
      <div class="card p-4">
        <label class="label">Заметки к тренировке</label>
        <textarea v-model="notes" rows="2" class="input resize-none" placeholder="Самочувствие, комментарии..."/>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
        <BaseButton class="flex-1" :loading="saving" @click="finish">
          Завершить тренировку ✓
        </BaseButton>
      </div>
    </div>

    <div v-else class="text-center py-16 text-gray-400">Загрузка...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import BaseButton from '@/components/ui/BaseButton.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const { runId, logId } = route.params
const workoutId = route.query.workoutId
const cycleName = route.query.cycleName || ''

const workout = computed(() => store.getters['workouts/workoutById'](workoutId))
const notes = ref('')
const saving = ref(false)
const localCompleted = ref(new Set())

const totalSets = computed(() =>
  workout.value?.exercises.reduce((n, ex) => n + ex.sets.length, 0) ?? 0
)

onMounted(async () => {
  if (!workout.value) {
    await store.dispatch('workouts/initWorkouts')
  }
  if (workout.value) {
    notes.value = workout.value.notes || ''
    for (const ex of workout.value.exercises) {
      for (const s of ex.sets) {
        if (s.completed) localCompleted.value.add(s.id)
      }
    }
  }
})

// ── Timer ──────────────────────────────────────────────────────────────────
const startedAt = Date.now()
const elapsedSeconds = ref(0)
const timer = setInterval(() => { elapsedSeconds.value = Math.floor((Date.now() - startedAt) / 1000) }, 1000)
onUnmounted(() => clearInterval(timer))

const elapsedFormatted = computed(() => {
  const s = elapsedSeconds.value
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
})
// ──────────────────────────────────────────────────────────────────────────

function toggleSet(setId) {
  const next = new Set(localCompleted.value)
  next.has(setId) ? next.delete(setId) : next.add(setId)
  localCompleted.value = next
}

async function finish() {
  if (!workout.value) return
  saving.value = true
  try {
    const durationMinutes = Math.max(1, Math.round(elapsedSeconds.value / 60))

    await store.dispatch('workouts/updateWorkout', {
      id: workout.value.id,
      date: workout.value.date,
      type: workout.value.type,
      title: workout.value.title,
      notes: notes.value,
      durationMinutes,
      exercises: workout.value.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({
          weight: s.weight,
          reps: s.reps,
          completed: localCompleted.value.has(s.id),
        })),
      })),
    })

    await store.dispatch('cycles/completeCycleWorkout', {
      runId,
      cycleWorkoutId: route.params.cycleWorkoutId,
    })

    store.dispatch('ui/showToast', { message: 'Тренировка завершена!', type: 'success' })
    router.push(`/cycles/${route.query.cycleId}`)
  } catch (e) {
    store.dispatch('ui/showToast', { message: e.message || 'Ошибка сохранения', type: 'error' })
  } finally {
    saving.value = false
  }
}
</script>
