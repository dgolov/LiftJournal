<template>
  <div class="card p-4">
    <div class="flex items-center justify-between mb-3">
      <div>
        <h4 class="font-semibold text-gray-900">{{ exercise.exerciseName }}</h4>
        <p class="text-xs text-gray-400">{{ exercise.sets.length }} {{ isCardio ? 'сессий' : 'подход(ов)' }}</p>
      </div>
      <button
        class="p-1.5 text-gray-300 hover:text-red-400 transition-colors"
        @click="removeExercise"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
    </div>

    <!-- Header row -->
    <div v-if="isCardio" class="flex items-center gap-1 mb-2 text-xs text-gray-400 font-medium">
      <span class="w-5" />
      <span class="flex-1 text-center">Мин.</span>
      <span class="w-10" />
      <span class="w-8" />
    </div>
    <div v-else class="flex items-center gap-1 mb-2 text-xs text-gray-400 font-medium">
      <span class="w-5" />
      <span class="flex-1 text-center">Вес (кг)</span>
      <span class="w-3" />
      <span class="flex-1 text-center">Повт.</span>
      <span class="w-10" />
      <span class="w-8" />
    </div>

    <div class="space-y-2">
      <ExerciseSetRow
        v-for="(set, i) in exercise.sets"
        :key="set.id"
        :set="set"
        :exercise-id="exercise.exerciseId"
        :index="i"
        :is-cardio="isCardio"
        @remove="removeSet(set.id)"
      />
    </div>

    <button
      class="mt-3 w-full py-2 text-sm text-primary hover:text-primary-dark font-medium border border-dashed border-primary/30 hover:border-primary/60 rounded-lg transition-colors"
      @click="addSet"
    >
      {{ isCardio ? '+ Добавить сессию' : '+ Добавить подход' }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import ExerciseSetRow from './ExerciseSetRow.vue'

const props = defineProps({
  exercise: { type: Object, required: true }
})

const store = useStore()
const exerciseData = computed(() => store.getters['exercises/exerciseById'](props.exercise.exerciseId))
const isCardio = computed(() => exerciseData.value?.muscleGroup === 'Кардио')

function addSet() {
  store.commit('workouts/ADD_SET_TO_EXERCISE', props.exercise.exerciseId)
}

function removeSet(setId) {
  store.commit('workouts/REMOVE_SET', { exerciseId: props.exercise.exerciseId, setId })
}

function removeExercise() {
  store.commit('workouts/REMOVE_EXERCISE_FROM_ACTIVE', props.exercise.exerciseId)
}
</script>
