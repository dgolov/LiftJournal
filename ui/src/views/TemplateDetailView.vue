<template>
  <div v-if="template" class="max-w-2xl">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-3">
        <button class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors" @click="onBack">
          <ChevronLeft class="w-5 h-5" />
        </button>
        <template v-if="!isEditing">
          <button
            class="ml-auto flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            @click="startEdit"
          >
            <Pencil class="w-3.5 h-3.5" /> Изменить
          </button>
        </template>
      </div>
      <div v-if="!isEditing">
        <div class="flex items-center gap-2 mb-1">
          <BaseBadge :color="typeColor">{{ template.type }}</BaseBadge>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ template.title }}</h2>
        <p class="text-sm text-gray-500 mt-1">{{ template.exercises.length }} упр. · {{ totalSets(template) }} подходов</p>
      </div>
    </div>

    <!-- Edit form -->
    <template v-if="isEditing">
      <div class="card p-4 mb-4 space-y-4">
        <h3 class="font-semibold text-gray-900 dark:text-white">Редактирование шаблона</h3>

        <BaseInput v-model="draft.title" label="Название шаблона" />

        <div>
          <label class="label">Тип тренировки</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="type in workoutTypes"
              :key="type"
              :class="['px-3 py-1.5 rounded-full text-sm font-medium border transition-colors',
                draft.type === type
                  ? 'bg-primary text-white border-primary'
                  : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary']"
              @click="draft.type = type"
            >{{ type }}</button>
          </div>
        </div>

        <div class="flex gap-2 justify-end">
          <button class="btn btn-ghost" @click="cancelEdit">Отмена</button>
          <button class="btn btn-primary" :disabled="saving" @click="saveEdit">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </div>

      <TemplateExerciseEditor :exercises="draft.exercises" />
    </template>

    <!-- Exercises: view mode -->
    <div v-else class="space-y-4">
      <div v-for="ex in template.exercises" :key="ex.exerciseId" class="card p-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <div v-for="(set, i) in ex.sets" :key="set.id" class="flex items-center gap-1 text-sm">
            <span class="text-gray-400 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>
            <span class="font-medium">{{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}</span>
            <span class="text-gray-400">×</span>
            <span class="font-medium">{{ set.reps }} повт.</span>
          </div>
          <p v-if="!ex.sets.length" class="text-sm text-gray-400">Подходы не заданы</p>
        </div>
      </div>
      <div v-if="!template.exercises.length" class="text-center py-8 text-gray-400">Упражнения не добавлены</div>
    </div>
  </div>

  <div v-else class="text-center py-16 text-gray-400">
    Шаблон не найден
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, Pencil } from 'lucide-vue-next'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import TemplateExerciseEditor from '@/components/workout/TemplateExerciseEditor.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const route = useRoute()
const router = useRouter()
const store = useStore()

const workoutTypes = WORKOUT_TYPES
const isEditing = ref(false)
const saving = ref(false)
const draft = ref(null)

const template = computed(() => store.getters['templates/byId'](route.params.id))

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[template.value?.type] || 'gray')

function totalSets(t) {
  return t.exercises.reduce((n, ex) => n + ex.sets.length, 0)
}

function uid() {
  return `ts-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function startEdit() {
  draft.value = {
    title: template.value.title,
    type: template.value.type,
    exercises: template.value.exercises.map(ex => ({
      exerciseId: ex.exerciseId,
      exerciseName: ex.exerciseName,
      sets: ex.sets.map(s => ({ id: s.id || uid(), weight: s.weight, reps: s.reps })),
    })),
  }
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  draft.value = null
}

function onBack() {
  if (isEditing.value) cancelEdit()
  else router.back()
}

async function saveEdit() {
  saving.value = true
  try {
    await store.dispatch('templates/updateTemplate', {
      id: route.params.id,
      title: draft.value.title.trim(),
      type: draft.value.type,
      exercises: draft.value.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({ weight: s.weight, reps: s.reps })),
      })),
    })
    store.dispatch('ui/showToast', { message: 'Шаблон обновлён', type: 'success' })
    isEditing.value = false
    draft.value = null
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await store.dispatch('exercises/initExercises')
  if (!template.value) await store.dispatch('templates/fetchTemplates')
})
</script>
