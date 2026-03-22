<template>
  <div v-if="exercise">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 mt-1 transition-colors" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ exercise.name }}</h2>
        <div class="flex flex-wrap gap-1.5 mt-2">
          <BaseBadge color="indigo">{{ exercise.muscleGroup }}</BaseBadge>
          <BaseBadge color="gray">{{ exercise.equipment }}</BaseBadge>
          <BaseBadge v-for="m in exercise.secondaryMuscles" :key="m" color="gray">{{ m }}</BaseBadge>
        </div>
        <p v-if="exercise.description" class="text-sm text-gray-600 dark:text-gray-400 mt-2">{{ exercise.description }}</p>
      </div>
    </div>

    <!-- PR Card (strength) -->
    <div v-if="pr && !isCardio" class="card p-4 mb-6 border-l-4 border-yellow-400">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">🏆</span>
        <p class="text-xs text-gray-500 uppercase tracking-wide font-semibold">Личные рекорды</p>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div class="text-center">
          <p class="text-xs text-gray-400 mb-0.5">Расч. 1ПМ</p>
          <p class="text-lg font-bold text-yellow-500">{{ pr.best1RM }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.best1RMDate) }}</p>
        </div>
        <div class="text-center border-x border-gray-100 dark:border-gray-700">
          <p class="text-xs text-gray-400 mb-0.5">Лучший вес</p>
          <p class="text-lg font-bold text-primary">{{ pr.bestWeight }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.bestWeightDate) }}</p>
        </div>
        <div class="text-center">
          <p class="text-xs text-gray-400 mb-0.5">Лучший тоннаж</p>
          <p class="text-lg font-bold text-green-500">{{ pr.bestVolume }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.bestVolumeDate) }}</p>
        </div>
      </div>
    </div>

    <!-- PR Card (cardio) -->
    <div v-if="pr && isCardio" class="card p-4 mb-6 border-l-4 border-yellow-400">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">🏆</span>
        <p class="text-xs text-gray-500 uppercase tracking-wide font-semibold">Личный рекорд</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-gray-400 mb-0.5">Лучшая сессия</p>
        <p class="text-lg font-bold text-yellow-500">{{ pr.bestDuration }} мин.</p>
        <p class="text-xs text-gray-400">{{ formatDate(pr.bestDurationDate) }}</p>
      </div>
    </div>

    <!-- Chart -->
    <div class="card p-4 mb-6">
      <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Прогресс</h3>
      <ProgressChart :data="progress" :is-cardio="isCardio" />
    </div>

    <!-- Sessions table -->
    <div class="card p-4">
      <h3 class="font-semibold text-gray-900 dark:text-white mb-3">История сессий</h3>
      <div v-if="progress.length" class="divide-y divide-gray-100 dark:divide-gray-800">
        <div v-for="session in [...progress].reverse()" :key="session.date + session.workoutId"
          class="flex items-center gap-3 py-2.5 text-sm cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg px-2 -mx-2 transition-colors"
          @click="$router.push(`/workouts/${session.workoutId}`)">
          <span class="text-gray-400 text-xs w-20 flex-shrink-0">{{ formatDate(session.date) }}</span>
          <span class="flex-1 text-gray-600 dark:text-gray-400 truncate">{{ session.workoutTitle }}</span>
          <template v-if="isCardio">
            <span class="text-primary font-semibold">{{ session.totalMinutes }} мин.</span>
          </template>
          <template v-else>
            <span class="text-yellow-500 font-semibold text-xs">1ПМ {{ session.best1RM }} кг</span>
            <span class="text-gray-900 dark:text-gray-100 font-medium">{{ session.maxWeight > 0 ? session.maxWeight + ' кг' : 'Б/в' }}</span>
            <span class="text-gray-400 text-xs">{{ session.totalVolume }} кг</span>
          </template>
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
const isCardio = computed(() => exercise.value?.muscleGroup === 'Кардио')
const progress = computed(() => store.getters['exercises/progressForExercise'](route.params.id))
const pr = computed(() => store.getters['exercises/personalRecord'](route.params.id))

function formatDate(date) {
  return new Date(date + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
