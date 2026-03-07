<template>
  <div v-if="exercise">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500 mt-1" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ exercise.name }}</h2>
        <div class="flex flex-wrap gap-1.5 mt-2">
          <BaseBadge color="indigo">{{ exercise.muscleGroup }}</BaseBadge>
          <BaseBadge color="gray">{{ exercise.equipment }}</BaseBadge>
          <BaseBadge v-for="m in exercise.secondaryMuscles" :key="m" color="gray">{{ m }}</BaseBadge>
        </div>
        <p v-if="exercise.description" class="text-sm text-gray-600 mt-2">{{ exercise.description }}</p>
      </div>
    </div>

    <!-- PR Card -->
    <div v-if="pr" class="card p-4 mb-6 flex items-center gap-4 border-l-4 border-yellow-400">
      <span class="text-3xl">🏆</span>
      <div>
        <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Личный рекорд</p>
        <p class="text-xl font-bold text-gray-900">
          {{ pr.weight > 0 ? pr.weight + ' кг × ' + pr.reps + ' повт.' : pr.reps + ' повт.' }}
        </p>
        <p class="text-xs text-gray-400">{{ formatDate(pr.date) }}</p>
      </div>
    </div>

    <!-- Chart -->
    <div class="card p-4 mb-6">
      <h3 class="font-semibold text-gray-900 mb-4">Прогресс</h3>
      <ProgressChart :data="progress" />
    </div>

    <!-- Sessions table -->
    <div class="card p-4">
      <h3 class="font-semibold text-gray-900 mb-3">История сессий</h3>
      <div v-if="progress.length" class="divide-y divide-gray-50">
        <div v-for="session in [...progress].reverse()" :key="session.date + session.workoutId"
          class="flex items-center gap-3 py-2.5 text-sm cursor-pointer hover:bg-gray-50 rounded-lg px-2 -mx-2"
          @click="$router.push(`/workouts/${session.workoutId}`)">
          <span class="text-gray-400 text-xs w-24 flex-shrink-0">{{ formatDate(session.date) }}</span>
          <span class="flex-1 text-gray-600 truncate">{{ session.workoutTitle }}</span>
          <span class="text-gray-900 font-medium">{{ session.maxWeight > 0 ? session.maxWeight + ' кг' : 'Б/в' }}</span>
          <span class="text-gray-400">{{ session.maxReps }} повт.</span>
        </div>
      </div>
      <BaseEmptyState v-else icon="📊" title="Нет данных" description="Добавьте это упражнение в тренировку, чтобы отслеживать прогресс" />
    </div>
  </div>

  <div v-else class="text-center py-16 text-gray-400">Упражнение не найдено</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ProgressChart from '@/components/exercises/ProgressChart.vue'

const route = useRoute()
const store = useStore()

const exercise = computed(() => store.getters['exercises/exerciseById'](route.params.id))
const progress = computed(() => store.getters['exercises/progressForExercise'](route.params.id))
const pr = computed(() => store.getters['exercises/personalRecord'](route.params.id))

function formatDate(date) {
  return new Date(date + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
