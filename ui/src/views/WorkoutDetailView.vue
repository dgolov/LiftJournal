<template>
  <div v-if="workout">
    <!-- Header -->
    <div class="flex items-start gap-4 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="onBack">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
          <span class="text-sm text-gray-400">{{ formattedDate }}</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">{{ workout.title }}</h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ formatDuration(workout.durationMinutes) }} · {{ workout.exercises.length }} упр.<template v-if="totalVolume > 0"> · тоннаж {{ formatVolume(totalVolume) }} кг</template>
        </p>
        <p v-if="workout.notes" class="text-sm text-gray-600 mt-2 italic">{{ workout.notes }}</p>
      </div>
      <button
        v-if="!isEditing"
        class="p-2 rounded-xl hover:bg-gray-100 text-gray-500"
        title="Редактировать"
        @click="startEdit"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a2 2 0 01-1.414.586H9v-1.414a2 2 0 01.586-1.414z"/>
        </svg>
      </button>
    </div>

    <!-- Edit form -->
    <div v-if="isEditing" class="card p-4 mb-4 space-y-4">
      <h3 class="font-semibold text-gray-900">Редактирование тренировки</h3>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="label">Название</label>
          <input v-model="draft.title" class="input w-full" />
        </div>
        <div>
          <label class="label">Дата</label>
          <input v-model="draft.date" type="date" class="input w-full" />
        </div>
        <div>
          <label class="label">Длительность (мин)</label>
          <input v-model.number="draft.durationMinutes" type="number" min="0" class="input w-full" />
        </div>
        <div>
          <label class="label">Тип</label>
          <select v-model="draft.type" class="input w-full">
            <option v-for="t in WORKOUT_TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="label">Заметки</label>
        <textarea v-model="draft.notes" class="input w-full" rows="2" />
      </div>

      <div class="flex gap-2 justify-end">
        <button class="btn" @click="cancelEdit">Отмена</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveEdit">
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>

    <!-- Exercises -->
    <div class="space-y-4">
      <div v-for="ex in displayExercises" :key="ex.exerciseId" class="card p-4">
        <h3 class="font-semibold text-gray-900 mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <div v-for="(set, i) in ex.sets" :key="set.id"
            class="flex items-center gap-1 text-sm">
            <span class="text-gray-400 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>

            <!-- View mode -->
            <template v-if="!isEditing">
              <template v-if="isCardio(ex.exerciseId)">
                <span class="font-medium">{{ set.reps }} мин.</span>
              </template>
              <template v-else>
                <span class="font-medium">{{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}</span>
                <span class="text-gray-400">×</span>
                <span class="font-medium">{{ set.reps }} повт.</span>
              </template>
              <span :class="['ml-auto text-xs font-medium', set.completed ? 'text-green-500' : 'text-gray-300']">
                {{ set.completed ? '✓' : '○' }}
              </span>
            </template>

            <!-- Edit mode -->
            <template v-else>
              <template v-if="isCardio(ex.exerciseId)">
                <StepperInput
                  class="flex-1"
                  :model-value="set.reps"
                  :step="1"
                  placeholder="мин"
                  @update:model-value="updateDraftSet(ex.exerciseId, set.id, 'reps', $event)"
                />
              </template>
              <template v-else>
                <StepperInput
                  class="flex-1"
                  :model-value="set.weight"
                  :step="2.5"
                  :decimals="1"
                  placeholder="кг"
                  @update:model-value="updateDraftSet(ex.exerciseId, set.id, 'weight', $event)"
                />
                <span class="text-gray-300 text-sm flex-shrink-0">×</span>
                <StepperInput
                  class="flex-1"
                  :model-value="set.reps"
                  :step="1"
                  placeholder="повт"
                  @update:model-value="updateDraftSet(ex.exerciseId, set.id, 'reps', $event)"
                />
              </template>
              <button
                :class="['w-9 h-9 rounded-full border-2 flex items-center justify-center transition-colors flex-shrink-0 text-sm font-bold',
                  set.completed ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 text-transparent hover:border-green-400']"
                @click="updateDraftSet(ex.exerciseId, set.id, 'completed', !set.completed)"
              >✓</button>
              <button
                class="w-7 h-9 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
                @click="removeDraftSet(ex.exerciseId, set.id)"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </template>
          </div>

          <!-- Add set button in edit mode -->
          <button
            v-if="isEditing"
            class="text-xs text-primary hover:underline mt-1"
            @click="addDraftSet(ex.exerciseId)"
          >+ добавить подход</button>
        </div>

        <p class="mt-2 text-xs text-gray-400 flex gap-3">
          <template v-if="isCardio(ex.exerciseId)">
            <span>Итого: {{ ex.sets.reduce((s, set) => s + (set.reps || 0), 0) }} мин.</span>
          </template>
          <template v-else>
            <span>Тоннаж: {{ ex.sets.reduce((s, set) => s + set.weight * set.reps, 0) }} кг</span>
            <span>· Расч. 1ПМ: {{ Math.max(...ex.sets.map(s => s.reps === 1 ? s.weight : Math.round(s.weight * (1 + s.reps / 30)))) }} кг</span>
          </template>
        </p>
      </div>
    </div>

    <div v-if="!workout.exercises.length" class="text-center py-8 text-gray-400">
      Упражнения не записаны
    </div>

    <!-- Add exercise button in edit mode -->
    <button
      v-if="isEditing"
      class="mt-2 w-full card p-3 flex items-center justify-center gap-2 text-sm text-primary hover:bg-gray-50 transition-colors"
      @click="showPicker = true"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
      </svg>
      Добавить упражнение
    </button>

    <ExercisePicker
      v-model="showPicker"
      :added-ids="draftAddedIds"
      @pick="addDraftExercise"
    />
  </div>

  <div v-else class="text-center py-16 text-gray-400">
    Тренировка не найдена
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import StepperInput from '@/components/ui/StepperInput.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const route = useRoute()
const store = useStore()

const workout = computed(() => store.getters['workouts/workoutById'](route.params.id))

const exerciseLibrary = computed(() => store.state.exercises.library)
function isCardio(exerciseId) {
  return exerciseLibrary.value.find(e => e.id === exerciseId)?.muscleGroup === 'Кардио'
}

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[workout.value?.type] || 'gray')

const formattedDate = computed(() => {
  if (!workout.value) return ''
  const d = new Date(workout.value.date + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})

const totalVolume = computed(() =>
  workout.value?.exercises.reduce((total, ex) =>
    isCardio(ex.exerciseId) ? total : total + ex.sets.reduce((s, set) => s + set.weight * set.reps, 0), 0) ?? 0
)

function formatVolume(v) {
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v
}

function formatDuration(minutes) {
  if (!minutes) return '—'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0) return `${h} ч ${m > 0 ? m + ' мин' : ''}`
  return `${m} мин`
}

// ── Edit mode ──────────────────────────────────────────────────────────────
const isEditing = ref(false)
const saving = ref(false)
const draft = ref(null)
const showPicker = ref(false)

const draftAddedIds = computed(() =>
  draft.value ? new Set(draft.value.exercises.map(e => e.exerciseId)) : new Set()
)

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

function uid() {
  return `s-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function startEdit() {
  draft.value = deepClone(workout.value)
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  draft.value = null
}

function onBack() {
  if (isEditing.value) { cancelEdit() } else { history.back() }
}

// Show draft exercises in edit mode, real workout exercises otherwise
const displayExercises = computed(() =>
  isEditing.value ? draft.value.exercises : workout.value.exercises
)

function updateDraftSet(exerciseId, setId, field, value) {
  const ex = draft.value.exercises.find(e => e.exerciseId === exerciseId)
  if (!ex) return
  const set = ex.sets.find(s => s.id === setId)
  if (set) set[field] = value
}

function removeDraftSet(exerciseId, setId) {
  const ex = draft.value.exercises.find(e => e.exerciseId === exerciseId)
  if (!ex) return
  ex.sets = ex.sets.filter(s => s.id !== setId)
}

function addDraftExercise(exercise) {
  showPicker.value = false
  draft.value.exercises.push({
    exerciseId: exercise.id,
    exerciseName: exercise.name,
    sets: [{ id: uid(), weight: 0, reps: 0, completed: false }]
  })
}

function addDraftSet(exerciseId) {
  const ex = draft.value.exercises.find(e => e.exerciseId === exerciseId)
  if (!ex) return
  const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
  ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps, completed: false })
}

async function saveEdit() {
  saving.value = true
  try {
    await store.dispatch('workouts/updateWorkout', draft.value)
    store.dispatch('ui/showToast', { message: 'Тренировка обновлена', type: 'success' }, { root: true })
    isEditing.value = false
    draft.value = null
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка при сохранении', type: 'error' }, { root: true })
  } finally {
    saving.value = false
  }
}
</script>
