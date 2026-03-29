<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">История</h2>
      <span class="text-sm text-gray-500">{{ filtered.length }} тренировок</span>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-6 space-y-3">
      <div class="flex flex-wrap gap-2">
        <button
          :class="['text-sm px-3 py-1.5 rounded-full font-medium border transition-colors',
            !activeType ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary']"
          @click="setFilter('type', null)"
        >Все</button>
        <button
          v-for="type in workoutTypes"
          :key="type"
          :class="['text-sm px-3 py-1.5 rounded-full font-medium border transition-colors',
            activeType === type ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary']"
          @click="setFilter('type', type)"
        >{{ type }}</button>
      </div>

      <div class="flex flex-col gap-3">
        <input
          :value="filters.search"
          placeholder="Поиск по названию или упражнению..."
          class="input"
          @input="setFilter('search', $event.target.value)"
        />
        <div class="flex gap-3">
          <input type="date" :value="filters.dateFrom || ''" class="input flex-1" @input="setFilter('dateFrom', $event.target.value || null)" />
          <input type="date" :value="filters.dateTo || ''" class="input flex-1" @input="setFilter('dateTo', $event.target.value || null)" />
        </div>
        <button v-if="hasActiveFilters" class="btn-ghost btn text-sm self-start" @click="resetFilters">Сбросить фильтры</button>
      </div>
    </div>

    <!-- List -->
    <div v-if="filtered.length" class="space-y-3">
      <WorkoutCard v-for="workout in filtered" :key="workout.id" :workout="workout" />
    </div>

    <BaseEmptyState
      v-else
      title="Тренировок не найдено"
      :description="hasActiveFilters ? 'Попробуйте изменить фильтры' : 'Начни первую тренировку!'"
    >
      <template #icon><Activity class="w-12 h-12" /></template>
      <RouterLink to="/workouts/new" class="mt-4 btn-primary btn">
        Добавить тренировку
      </RouterLink>
    </BaseEmptyState>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Activity } from 'lucide-vue-next'
import WorkoutCard from '@/components/workout/WorkoutCard.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const workoutTypes = WORKOUT_TYPES

onMounted(() => {
  if (!store.state.workouts.workouts.length) {
    store.dispatch('workouts/initWorkouts')
  }
})
const filtered = computed(() => store.getters['workouts/filteredWorkouts'])
const filters = computed(() => store.state.workouts.filters)
const activeType = computed(() => filters.value.type)
const hasActiveFilters = computed(() =>
  filters.value.type || filters.value.dateFrom || filters.value.dateTo || filters.value.search
)

function setFilter(key, value) {
  store.commit('workouts/SET_FILTER', { key, value })
}
function resetFilters() {
  store.commit('workouts/RESET_FILTERS')
}
</script>
