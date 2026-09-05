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
    </div>

    <div class="mb-4">
      <TemplateExerciseEditor :exercises="form.exercises" />
    </div>

    <div class="flex gap-3">
      <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
      <BaseButton class="flex-1" :disabled="!canSave" :loading="saving" @click="save">Создать шаблон</BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import TemplateExerciseEditor from '@/components/workout/TemplateExerciseEditor.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()

const workoutTypes = WORKOUT_TYPES
const saving = ref(false)
const form = ref({
  title: '',
  type: 'Силовая',
  exercises: [],
})

const canSave = computed(() => form.value.title.trim().length > 0)

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
})
</script>
