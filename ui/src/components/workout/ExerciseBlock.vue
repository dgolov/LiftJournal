<template>
  <div class="card p-4">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2 min-w-0">
        <span class="drag-handle flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 cursor-grab active:cursor-grabbing touch-none p-1 -ml-1">
          <GripVertical class="w-4 h-4" />
        </span>
        <div class="min-w-0">
          <h4 class="font-semibold text-gray-900 dark:text-white">{{ exercise.exerciseName }}</h4>
          <p class="text-xs text-gray-400">{{ exercise.sets.length }} {{ isCardio ? 'сессий' : 'подход(ов)' }}</p>
        </div>
      </div>
      <button
        class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
        @click="removeExercise"
      >
        <Trash2 class="w-5 h-5" />
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
import { Trash2, GripVertical } from 'lucide-vue-next'
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
