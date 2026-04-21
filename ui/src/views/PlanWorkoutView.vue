<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <button
        class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
        @click="$router.back()"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">
        {{ isEdit ? 'Редактировать план' : 'Новый план тренировки' }}
      </h2>
    </div>

    <!-- Basic info -->
    <div class="card p-5 mb-4 space-y-4">
      <h3 class="font-semibold text-gray-900 dark:text-white">Основная информация</h3>

      <BaseInput
        v-model="form.title"
        label="Название тренировки"
        placeholder="Например: Приседания / Жим / Тяга"
      />

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

      <BaseInput
        v-model="form.scheduledDate"
        type="date"
        label="Дата тренировки"
      />

      <!-- Recurrence (only for new plans) -->
      <div v-if="!isEdit">
        <label class="label">Повторение</label>
        <div class="flex gap-2">
          <button
            :class="['flex-1 py-2 rounded-lg text-sm font-medium border transition-colors',
              !form.recurring ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400']"
            @click="form.recurring = false"
          >Не повторять</button>
          <button
            :class="['flex-1 py-2 rounded-lg text-sm font-medium border transition-colors',
              form.recurring ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400']"
            @click="form.recurring = true"
          >Каждую неделю</button>
        </div>
        <div v-if="form.recurring" class="mt-3 flex items-center gap-3">
          <span class="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">Повторять</span>
          <select v-model="form.recurrenceWeeks" class="input flex-1">
            <option :value="4">4 недели</option>
            <option :value="8">8 недель</option>
            <option :value="12">12 недель</option>
            <option :value="24">24 недели</option>
          </select>
          <span class="text-xs text-gray-400 whitespace-nowrap">по {{ scheduledDayLabel }}</span>
        </div>
      </div>

      <div>
        <label class="label">Заметки / план</label>
        <textarea
          v-model="form.notes"
          placeholder="Цели на тренировку, особые условия..."
          rows="2"
          class="input resize-none"
        />
      </div>
    </div>

    <!-- Exercises -->
    <div class="mb-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-900 dark:text-white">Упражнения</h3>
        <BaseButton variant="outline" size="sm" @click="showPicker = true">+ Добавить</BaseButton>
      </div>

      <div v-if="form.exercises.length" class="space-y-3">
        <div
          v-for="(ex, exIdx) in form.exercises"
          :key="ex.exerciseId"
          class="card p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-white">{{ ex.exerciseName }}</h4>
              <p class="text-xs text-gray-400">{{ ex.sets.length }} подходов (план)</p>
            </div>
            <button
              class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
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
            <div
              v-for="(set, setIdx) in ex.sets"
              :key="set.id"
              class="flex items-center gap-1"
            >
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
      </div>

      <BaseEmptyState
        v-else
        title="Добавьте упражнения"
        description="Добавьте упражнения и запланируйте подходы с целевыми весами"
        class="mb-4"
      >
        <template #icon><Dumbbell class="w-12 h-12" /></template>
      </BaseEmptyState>
    </div>

    <!-- Save -->
    <div class="flex gap-3">
      <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
      <BaseButton class="flex-1" :disabled="!canSave" :loading="saving" @click="save">
        {{ isEdit ? 'Сохранить изменения' : 'Сохранить план' }}
      </BaseButton>
    </div>

    <ExercisePicker
      v-model="showPicker"
      :added-ids="addedExerciseIds"
      @pick="addExercise"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ChevronLeft, Dumbbell, Trash2, X } from 'lucide-vue-next'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import StepperInput from '@/components/ui/StepperInput.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const showPicker = ref(false)
const saving = ref(false)
const workoutTypes = WORKOUT_TYPES

function tomorrow() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

function uid() {
  return `ps-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

const form = ref({
  title: '',
  type: 'Силовая',
  scheduledDate: route.query.date || tomorrow(),
  notes: '',
  exercises: [],
  recurring: false,
  recurrenceWeeks: 12,
})

const weekDayNames = ['воскресенье', 'понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']
const scheduledDayLabel = computed(() => {
  const d = new Date(form.value.scheduledDate + 'T00:00:00')
  return weekDayNames[d.getDay()]
})

const canSave = computed(() => form.value.title.trim().length > 0)

const addedExerciseIds = computed(() => new Set(form.value.exercises.map(e => e.exerciseId)))

function addExercise(exercise) {
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
    const payload = {
      title: form.value.title,
      type: form.value.type,
      scheduledDate: form.value.scheduledDate,
      notes: form.value.notes,
      exercises: form.value.exercises,
      status: 'planned',
    }
    if (isEdit.value) {
      await store.dispatch('planned/updatePlannedWorkout', { id: route.params.id, ...payload })
      store.dispatch('ui/showToast', { message: 'План обновлён', type: 'success' })
    } else if (form.value.recurring) {
      await store.dispatch('planned/createRecurringPlan', { payload, weeks: form.value.recurrenceWeeks })
      store.dispatch('ui/showToast', { message: `Создано ${form.value.recurrenceWeeks} тренировок`, type: 'success' })
    } else {
      await store.dispatch('planned/createPlannedWorkout', payload)
      store.dispatch('ui/showToast', { message: 'Тренировка запланирована!', type: 'success' })
    }
    router.push('/planning')
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await store.dispatch('exercises/initExercises')
  if (isEdit.value) {
    let plan = store.getters['planned/byId'](route.params.id)
    if (!plan) {
      await store.dispatch('planned/fetchPlannedWorkouts')
      plan = store.getters['planned/byId'](route.params.id)
    }
    if (plan) {
      form.value = {
        title: plan.title,
        type: plan.type,
        scheduledDate: plan.scheduledDate,
        notes: plan.notes || '',
        exercises: plan.exercises.map(ex => ({
          ...ex,
          sets: ex.sets.map(s => ({ ...s, id: s.id || uid() })),
        })),
      }
    }
  }
})
</script>
