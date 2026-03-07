<template>
  <div class="max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <h2 class="text-xl font-bold text-gray-900">Новая тренировка</h2>
    </div>

    <!-- Steps -->
    <div class="flex gap-1 mb-6">
      <div v-for="(s, i) in steps" :key="i"
        :class="['h-1 flex-1 rounded-full transition-colors', step > i ? 'bg-primary' : 'bg-gray-200']"
      />
    </div>

    <!-- Step 1: Info -->
    <div v-if="step === 0" class="space-y-4">
      <div class="card p-5">
        <h3 class="font-semibold text-gray-900 mb-4">Основная информация</h3>
        <div class="space-y-4">
          <BaseInput
            :model-value="activeWorkout.title"
            label="Название тренировки"
            placeholder="Например: Грудь и трицепс"
            @update:model-value="setField('title', $event)"
          />
          <div>
            <label class="label">Тип тренировки</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="type in workoutTypes"
                :key="type"
                :class="['px-3 py-1.5 rounded-full text-sm font-medium border transition-colors',
                  activeWorkout.type === type ? 'bg-primary text-white border-primary' : 'border-gray-200 text-gray-600 hover:border-primary']"
                @click="setField('type', type)"
              >{{ type }}</button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <BaseInput
              :model-value="activeWorkout.date"
              type="date"
              label="Дата"
              @update:model-value="setField('date', $event)"
            />
            <BaseInput
              :model-value="activeWorkout.durationMinutes"
              type="number"
              label="Длительность (мин)"
              min="1"
              @update:model-value="setField('durationMinutes', $event)"
            />
          </div>
          <div>
            <label class="label">Заметки</label>
            <textarea
              :value="activeWorkout.notes"
              placeholder="Как прошла тренировка?"
              rows="2"
              class="input resize-none"
              @input="setField('notes', $event.target.value)"
            />
          </div>
        </div>
      </div>
      <BaseButton class="w-full" :disabled="!canProceed" @click="step++">Далее →</BaseButton>
    </div>

    <!-- Step 2: Exercises -->
    <div v-else-if="step === 1">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-900">Упражнения</h3>
        <BaseButton variant="outline" size="sm" @click="showPicker = true">+ Добавить</BaseButton>
      </div>

      <div v-if="activeWorkout.exercises.length" class="space-y-3 mb-4">
        <ExerciseBlock v-for="ex in activeWorkout.exercises" :key="ex.exerciseId" :exercise="ex" />
      </div>

      <BaseEmptyState
        v-else
        icon="🏋️"
        title="Добавьте упражнения"
        description="Нажмите кнопку выше, чтобы выбрать упражнения из библиотеки"
        class="mb-4"
      />

      <div class="flex gap-3">
        <BaseButton variant="ghost" @click="step--">← Назад</BaseButton>
        <BaseButton class="flex-1" @click="step++">Далее →</BaseButton>
      </div>
    </div>

    <!-- Step 3: Review -->
    <div v-else>
      <h3 class="font-semibold text-gray-900 mb-4">Проверьте данные</h3>

      <div class="card p-4 mb-4">
        <div class="flex items-center gap-2 mb-2">
          <BaseBadge color="indigo">{{ activeWorkout.type }}</BaseBadge>
          <span class="text-sm text-gray-500">{{ formattedDate }}</span>
        </div>
        <h4 class="font-bold text-gray-900 text-lg">{{ activeWorkout.title || 'Без названия' }}</h4>
        <p class="text-sm text-gray-500 mt-1">
          {{ activeWorkout.durationMinutes }} мин ·
          {{ activeWorkout.exercises.length }} упр. ·
          {{ totalSets }} подходов
        </p>
        <p v-if="activeWorkout.notes" class="text-sm text-gray-600 mt-1 italic">{{ activeWorkout.notes }}</p>
        <div v-if="activeWorkout.exercises.length" class="mt-3 space-y-1">
          <p v-for="ex in activeWorkout.exercises" :key="ex.exerciseId" class="text-sm text-gray-700">
            · {{ ex.exerciseName }} — {{ ex.sets.length }} подх.
          </p>
        </div>
      </div>

      <div class="flex gap-3">
        <BaseButton variant="ghost" @click="step--">← Назад</BaseButton>
        <BaseButton class="flex-1" :loading="saving" @click="save">Сохранить тренировку ✓</BaseButton>
      </div>
    </div>

    <ExercisePicker v-model="showPicker" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ExerciseBlock from '@/components/workout/ExerciseBlock.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()

const step = ref(0)
const steps = [1, 2, 3]
const showPicker = ref(false)
const saving = ref(false)
const workoutTypes = WORKOUT_TYPES

const activeWorkout = computed(() => store.state.workouts.activeWorkout)

const canProceed = computed(() => activeWorkout.value.title.trim().length > 0)

const totalSets = computed(() =>
  activeWorkout.value.exercises.reduce((n, ex) => n + ex.sets.length, 0)
)

const formattedDate = computed(() => {
  const d = new Date(activeWorkout.value.date + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
})

function setField(field, value) {
  store.commit('workouts/SET_ACTIVE_WORKOUT_FIELD', { field, value })
}

async function save() {
  saving.value = true
  try {
    const saved = await store.dispatch('workouts/saveWorkout')
    store.dispatch('ui/showToast', { message: 'Тренировка сохранена!', type: 'success' })
    router.push(`/workouts/${saved.id}`)
  } finally {
    saving.value = false
  }
}
</script>
