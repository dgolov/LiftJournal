<template>
  <div>
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-gray-900 dark:text-white">Упражнения</h3>
      <div class="flex items-center gap-2">
        <ExerciseViewModeToggle />
        <BaseButton variant="outline" size="sm" @click="showPicker = true">+ Добавить</BaseButton>
      </div>
    </div>

    <draggable
      v-if="exercises.length"
      :list="exercises"
      item-key="exerciseId"
      handle=".drag-handle"
      animation="200"
      class="space-y-3"
    >
      <template #item="{ element: ex, index: exIdx }">
        <ExerciseCompactCard
          v-if="viewMode === 'cards'"
          :exercise-name="ex.exerciseName"
          :sets-count="ex.sets.length"
          @remove="removeExercise(exIdx)"
        />
        <div v-else class="card p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2 min-w-0">
              <span class="drag-handle flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 cursor-grab active:cursor-grabbing touch-none p-1 -ml-1">
                <GripVertical class="w-4 h-4" />
              </span>
              <h4 class="font-semibold text-gray-900 dark:text-white min-w-0 truncate">{{ ex.exerciseName }}</h4>
            </div>
            <button
              class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
              @click="removeExercise(exIdx)"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>

          <!-- Column headers -->
          <div class="flex items-center gap-1 mb-2 text-xs text-gray-400 font-medium">
            <span class="w-5" />
            <span class="flex-1 text-center">Вес (кг)</span>
            <span class="w-3 text-center">×</span>
            <span class="flex-1 text-center">Повт.</span>
            <span class="w-7" />
          </div>

          <div class="space-y-2">
            <div v-for="(set, setIdx) in ex.sets" :key="set.id" class="flex items-center gap-1">
              <span class="text-xs text-gray-400 w-5 text-center flex-shrink-0">{{ setIdx + 1 }}</span>
              <StepperInput
                class="flex-1"
                :model-value="set.weight"
                :step="0.5"
                :decimals="1"
                placeholder="кг"
                @update:model-value="set.weight = $event"
              />
              <span class="text-gray-300 text-sm flex-shrink-0">×</span>
              <StepperInput
                class="flex-1"
                :model-value="set.reps"
                :step="1"
                placeholder="повт"
                @update:model-value="set.reps = $event"
              />
              <button
                class="w-7 h-9 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
                @click="removeSet(exIdx, setIdx)"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>

          <button
            class="mt-3 w-full py-2 text-sm text-primary hover:text-primary font-medium border border-dashed border-primary/30 hover:border-primary/60 rounded-lg transition-colors"
            @click="addSet(exIdx)"
          >+ Добавить подход</button>
        </div>
      </template>
    </draggable>

    <BaseEmptyState
      v-else
      title="Добавьте упражнения"
      description="Нажмите «+ Добавить», чтобы выбрать упражнения из библиотеки"
    >
      <template #icon><Dumbbell class="w-12 h-12" /></template>
    </BaseEmptyState>

    <ExercisePicker v-model="showPicker" :added-ids="addedExerciseIds" @pick="addExercise" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dumbbell, Trash2, X, GripVertical } from 'lucide-vue-next'
import draggable from 'vuedraggable'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import StepperInput from '@/components/ui/StepperInput.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import ExerciseCompactCard from '@/components/workout/ExerciseCompactCard.vue'
import ExerciseViewModeToggle from '@/components/workout/ExerciseViewModeToggle.vue'
import { useExerciseViewMode } from '@/composables/useExerciseViewMode.js'

// `exercises` is expected to be the parent's own reactive array (e.g. from a
// form ref) — mutated in place here, mirroring how vuedraggable's :list works.
const props = defineProps({
  exercises: { type: Array, required: true },
})

const viewMode = useExerciseViewMode()
const showPicker = ref(false)

const addedExerciseIds = computed(() => new Set(props.exercises.map(e => e.exerciseId)))

function uid() {
  return `ts-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function addExercise(exercise) {
  showPicker.value = false
  props.exercises.push({
    exerciseId: exercise.id,
    exerciseName: exercise.name,
    sets: [{ id: uid(), weight: 0, reps: 0 }],
  })
}

function removeExercise(exIdx) {
  props.exercises.splice(exIdx, 1)
}

function addSet(exIdx) {
  const ex = props.exercises[exIdx]
  const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
  ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps })
}

function removeSet(exIdx, setIdx) {
  props.exercises[exIdx].sets.splice(setIdx, 1)
}
</script>
