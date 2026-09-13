<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <button
        class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
        @click="$router.back()"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Новый шаблон</h2>
    </div>

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

      <BaseButton
        v-if="recentWorkouts.length"
        variant="outline"
        class="w-full flex items-center justify-center gap-2"
        @click="showRepeatPicker = true"
      >
        <RefreshCw class="w-4 h-4" /> Повторить тренировку
      </BaseButton>
    </div>

    <div class="mb-4">
      <TemplateExerciseEditor :exercises="form.exercises" />
    </div>

    <div class="flex gap-3">
      <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
      <BaseButton class="flex-1" :disabled="!canSave" :loading="saving" @click="save">Создать шаблон</BaseButton>
    </div>

    <BaseModal v-model="showRepeatPicker" title="Повторить тренировку" max-width="md" :fullscreen="true">
      <div class="space-y-1 -mx-2 px-2">
        <button
          v-for="w in recentWorkouts"
          :key="w.id"
          class="w-full text-left px-3 py-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-3"
          @click="repeatWorkout(w)"
        >
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ w.title || 'Без названия' }}</p>
            <p class="text-xs text-gray-400">{{ formatShortDate(w.date) }} · {{ w.type }} · {{ w.exercises.length }} упр.</p>
          </div>
        </button>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showRepeatPicker = false">Закрыть</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ChevronLeft, RefreshCw } from 'lucide-vue-next'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import TemplateExerciseEditor from '@/components/workout/TemplateExerciseEditor.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()

const workoutTypes = WORKOUT_TYPES
const saving = ref(false)
const showRepeatPicker = ref(false)
const form = ref({
  title: '',
  type: 'Силовая',
  exercises: [],
})

const canSave = computed(() => form.value.title.trim().length > 0)
const recentWorkouts = computed(() => store.getters['workouts/allWorkouts'].slice(0, 10))

function uid() {
  return `ts-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function formatShortDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function repeatWorkout(w) {
  form.value.title = w.title
  form.value.type = w.type
  form.value.exercises = w.exercises.map(ex => ({
    exerciseId: ex.exerciseId,
    exerciseName: ex.exerciseName,
    sets: ex.sets.map(s => ({ id: uid(), weight: s.weight, reps: s.reps })),
  }))
  showRepeatPicker.value = false
}

async function save() {
  saving.value = true
  try {
    const created = await store.dispatch('templates/createTemplate', {
      title: form.value.title.trim(),
      type: form.value.type,
      exercises: form.value.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({ weight: s.weight, reps: s.reps })),
      })),
    })
    store.dispatch('ui/showToast', { message: 'Шаблон создан', type: 'success' })
    router.push(`/templates/${created.id}`)
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.dispatch('exercises/initExercises')
  if (!store.state.workouts.workouts.length) store.dispatch('workouts/initWorkouts')
})
</script>
