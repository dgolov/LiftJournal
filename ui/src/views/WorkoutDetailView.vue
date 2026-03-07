<template>
  <div v-if="workout">
    <!-- Header -->
    <div class="flex items-start gap-4 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
          <span class="text-sm text-gray-400">{{ formattedDate }}</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">{{ workout.title }}</h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ formatDuration(workout.durationMinutes) }} · {{ workout.exercises.length }} упр. · тоннаж {{ formatVolume(totalVolume) }} кг
        </p>
        <p v-if="workout.notes" class="text-sm text-gray-600 mt-2 italic">{{ workout.notes }}</p>
      </div>
    </div>

    <!-- Exercises -->
    <div class="space-y-4">
      <div v-for="ex in workout.exercises" :key="ex.exerciseId" class="card p-4">
        <h3 class="font-semibold text-gray-900 mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <div v-for="(set, i) in ex.sets" :key="set.id"
            class="flex items-center gap-3 text-sm">
            <span class="text-gray-400 w-6">{{ i + 1 }}.</span>
            <span class="font-medium">{{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}</span>
            <span class="text-gray-400">×</span>
            <span class="font-medium">{{ set.reps }} повт.</span>
            <span :class="['ml-auto text-xs font-medium', set.completed ? 'text-green-500' : 'text-gray-300']">
              {{ set.completed ? '✓' : '○' }}
            </span>
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-400 flex gap-3">
          <span>Тоннаж: {{ ex.sets.reduce((s, set) => s + set.weight * set.reps, 0) }} кг</span>
          <span>· Расч. 1ПМ: {{ Math.max(...ex.sets.map(s => s.reps === 1 ? s.weight : Math.round(s.weight * (1 + s.reps / 30)))) }} кг</span>
        </p>
      </div>
    </div>

    <div v-if="!workout.exercises.length" class="text-center py-8 text-gray-400">
      Упражнения не записаны
    </div>
  </div>

  <div v-else class="text-center py-16 text-gray-400">
    Тренировка не найдена
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import BaseBadge from '@/components/ui/BaseBadge.vue'

const route = useRoute()
const store = useStore()

const workout = computed(() => store.getters['workouts/workoutById'](route.params.id))

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[workout.value?.type] || 'gray')

const formattedDate = computed(() => {
  if (!workout.value) return ''
  const d = new Date(workout.value.date + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})

const totalVolume = computed(() =>
  workout.value?.exercises.reduce((total, ex) =>
    total + ex.sets.reduce((s, set) => s + set.weight * set.reps, 0), 0) ?? 0
)

function formatVolume(v) {
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v
}

function formatDuration(minutes) {
  if (!minutes) return '—'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0) return `${h} ч ${m > 0 ? m + ' мин' : ''}`
  return `${m} мин`
}
</script>
