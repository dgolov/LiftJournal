<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <button
        class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
        @click="$router.back()"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Редактировать шаблон</h2>
    </div>

    <div v-if="!form" class="text-center py-16 text-gray-400">Шаблон не найден</div>

    <template v-else>
      <!-- Basic info -->
      <div class="card p-5 mb-4 space-y-4">
        <h3 class="font-semibold text-gray-900 dark:text-white">Основная информация</h3>

        <BaseInput v-model="form.title" label="Название шаблона" placeholder="Например: Push day" />

        <div>
          <label class="label">Тип тренировки</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="type in workoutTypes"
              :key="type"
              :class="['px-3 py-1.5 rounded-full text-sm font-medium border transition-colors',
                form.type === type
                  ? 'bg-primary text-white border-primary'
                  : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary']"
              @click="form.type = type"
            >{{ type }}</button>
          </div>
        </div>
      </div>

      <!-- Exercises -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 dark:text-white">Упражнения</h3>
          <div class="flex items-center gap-2">
            <ExerciseViewModeToggle />
            <BaseButton variant="outline" size="sm" @click="showPicker = true">+ Добавить</BaseButton>
          </div>
        </div>

        <draggable
          v-if="form.exercises.length"
          :list="form.exercises"
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
      </div>

      <div class="flex gap-3">
        <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
        <BaseButton class="flex-1" :disabled="!canSave" :loading="saving" @click="save">Сохранить изменения</BaseButton>
      </div>

      <ExercisePicker v-model="showPicker" :added-ids="addedExerciseIds" @pick="addExercise" />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ChevronLeft, Dumbbell, Trash2, X, GripVertical } from 'lucide-vue-next'
import draggable from 'vuedraggable'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import StepperInput from '@/components/ui/StepperInput.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import ExerciseCompactCard from '@/components/workout/ExerciseCompactCard.vue'
import ExerciseViewModeToggle from '@/components/workout/ExerciseViewModeToggle.vue'
import { useExerciseViewMode } from '@/composables/useExerciseViewMode.js'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()
const route = useRoute()
const viewMode = useExerciseViewMode()

const workoutTypes = WORKOUT_TYPES
const showPicker = ref(false)
const saving = ref(false)
const form = ref(null)

function uid() {
  return `ts-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

const canSave = computed(() => !!form.value && form.value.title.trim().length > 0)
const addedExerciseIds = computed(() => new Set(form.value ? form.value.exercises.map(e => e.exerciseId) : []))

function addExercise(exercise) {
  showPicker.value = false
  form.value.exercises.push({
    exerciseId: exercise.id,
    exerciseName: exercise.name,
    sets: [{ id: uid(), weight: 0, reps: 0 }],
  })
}

function removeExercise(exIdx) {
  form.value.exercises.splice(exIdx, 1)
}

function addSet(exIdx) {
  const ex = form.value.exercises[exIdx]
  const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
  ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps })
}

function removeSet(exIdx, setIdx) {
  form.value.exercises[exIdx].sets.splice(setIdx, 1)
}

async function save() {
  saving.value = true
  try {
    await store.dispatch('templates/updateTemplate', {
      id: route.params.id,
      title: form.value.title.trim(),
      type: form.value.type,
      exercises: form.value.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({ weight: s.weight, reps: s.reps })),
      })),
    })
    store.dispatch('ui/showToast', { message: 'Шаблон обновлён', type: 'success' })
    router.push('/templates')
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    saving.value = false
  }
}

function loadForm(template) {
  form.value = {
    title: template.title,
    type: template.type,
    exercises: template.exercises.map(ex => ({
      exerciseId: ex.exerciseId,
      exerciseName: ex.exerciseName,
      sets: ex.sets.map(s => ({ id: s.id || uid(), weight: s.weight, reps: s.reps })),
    })),
  }
}

onMounted(async () => {
  await store.dispatch('exercises/initExercises')
  let template = store.getters['templates/byId'](route.params.id)
  if (!template) {
    await store.dispatch('templates/fetchTemplates')
    template = store.getters['templates/byId'](route.params.id)
  }
  if (template) loadForm(template)
})
</script>
