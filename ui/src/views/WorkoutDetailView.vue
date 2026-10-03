<template>
  <div v-if="workout">
    <!-- Header -->
    <div class="mb-6">
      <!-- Back + actions row -->
      <div class="flex items-center gap-2 mb-3">
        <button class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors" @click="onBack">
          <ChevronLeft class="w-5 h-5" />
        </button>
        <template v-if="!isEditing && isOwner">
          <div class="ml-auto flex items-center flex-wrap justify-end gap-1">
            <button
              class="flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
              @click="repeatWorkout"
            >
              <RefreshCw class="w-3.5 h-3.5" /> Повторить
            </button>
            <button
              class="flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              @click="templateName = workout.title; showSaveTemplate = true"
            >
              <LayoutTemplate class="w-3.5 h-3.5" /> Шаблон
            </button>
            <button
              class="flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              @click="exportModalOpen = true"
            >
              <Download class="w-3.5 h-3.5" /> Экспорт
            </button>
            <button
              class="flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              @click="startEdit"
            >
              <Pencil class="w-3.5 h-3.5" /> Изменить
            </button>
          </div>
        </template>
      </div>
      <!-- Title block -->
      <div>
        <div class="flex items-center gap-2 mb-1">
          <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
          <span class="text-sm text-gray-400">{{ formattedDate }}</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ workout.title }}</h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ formatDuration(workout.durationMinutes) }} · {{ workout.exercises.length }} упр.<template v-if="totalVolume > 0"> · тоннаж {{ formatVolume(totalVolume) }} кг</template>
        </p>
        <p v-if="workout.notes" class="text-sm text-gray-600 dark:text-gray-400 mt-2 italic">{{ workout.notes }}</p>
      </div>
    </div>

    <!-- Edit form -->
    <div v-if="isEditing" class="card p-4 mb-4 space-y-4">
      <h3 class="font-semibold text-gray-900 dark:text-white">Редактирование тренировки</h3>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="label">Название</label>
          <input v-model="draft.title" class="input" />
        </div>
        <div>
          <label class="label">Дата</label>
          <input v-model="draft.date" type="date" class="input" />
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
        <button class="btn btn-ghost" @click="cancelEdit">Отмена</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveEdit">
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>

    <!-- Exercises: edit mode -->
    <div v-if="isEditing" class="flex items-center justify-between mb-3">
      <h3 class="font-semibold text-gray-900 dark:text-white">Упражнения</h3>
      <ExerciseViewModeToggle />
    </div>
    <draggable
      v-if="isEditing"
      :list="draft.exercises"
      item-key="instanceId"
      handle=".drag-handle"
      animation="200"
      class="space-y-4"
    >
      <template #item="{ element: ex }">
        <ExerciseCompactCard
          v-if="viewMode === 'cards'"
          :exercise-name="ex.exerciseName"
          :sets-count="ex.sets.length"
          @remove="removeDraftExercise(ex.instanceId)"
        />
        <SwipeDeleteWrapper
          v-else
          delete-label="Удалить упражнение"
          @delete="removeDraftExercise(ex.instanceId)"
        >
          <div class="card p-4">
            <div class="flex items-center gap-2 mb-3">
              <span class="drag-handle flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 cursor-grab active:cursor-grabbing touch-none p-1 -ml-1">
                <GripVertical class="w-4 h-4" />
              </span>
              <h3 class="font-semibold text-gray-900 dark:text-white flex-1">{{ ex.exerciseName }}</h3>
              <button
                class="w-7 h-7 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
                @click="removeDraftExercise(ex.instanceId)"
              ><Trash2 class="w-4 h-4" /></button>
            </div>
            <div class="space-y-2">
              <SwipeDeleteWrapper
                v-for="(set, i) in ex.sets"
                :key="set.id"
                :bordered="false"
                delete-label="Удалить подход"
                @delete="removeDraftSet(ex.instanceId, set.id)"
              >
              <div class="flex items-center gap-1 text-sm bg-card dark:bg-steel-900 py-0.5">
                <span class="text-gray-400 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>
                <template v-if="isCardio(ex.exerciseId)">
                  <StepperInput
                    class="flex-1"
                    :model-value="set.reps"
                    :step="1"
                    placeholder="мин"
                    @update:model-value="updateDraftSet(ex.instanceId, set.id, 'reps', $event)"
                  />
                </template>
                <template v-else>
                  <StepperInput
                    :class="['flex-1', set.failed ? 'opacity-50' : '']"
                    :model-value="set.weight"
                    :step="2.5"
                    :decimals="1"
                    placeholder="кг"
                    @update:model-value="updateDraftSet(ex.instanceId, set.id, 'weight', $event)"
                  />
                  <span class="text-gray-300 text-sm flex-shrink-0">×</span>
                  <StepperInput
                    :class="['flex-1', set.failed ? 'opacity-50' : '']"
                    :model-value="set.reps"
                    :step="1"
                    placeholder="повт"
                    @update:model-value="updateDraftSet(ex.instanceId, set.id, 'reps', $event)"
                  />
                  <input
                    type="text"
                    inputmode="decimal"
                    :value="set.rpe ?? ''"
                    placeholder="РПЕ"
                    title="RPE — субъективная тяжесть подхода, 1–10 (необязательно)"
                    class="w-10 flex-shrink-0 rounded-lg border border-steel-100 dark:border-steel-700 bg-white dark:bg-steel-900 text-ink dark:text-white font-mono px-0.5 py-2 text-xs text-center placeholder-gray-300 focus:border-primary focus:outline-none"
                    @change="onDraftRpeChange(ex.instanceId, set.id, $event)"
                  />
                </template>
                <button
                  :class="['w-9 h-9 rounded-full border flex items-center justify-center transition-colors flex-shrink-0 text-sm font-bold',
                    set.completed ? 'bg-green-500 border-green-500 text-white' :
                    set.failed    ? 'bg-red-500 border-red-500 text-white' :
                                    'bg-card dark:bg-steel-900 border-gray-300 text-gray-300 hover:border-green-400']"
                  :title="set.completed ? 'Выполнено → провал' : set.failed ? 'Провал → сбросить' : 'Отметить выполненным'"
                  @click="cycleDraftSetState(ex.instanceId, set.id, set)"
                >{{ set.completed ? '✓' : set.failed ? '✗' : '○' }}</button>
                <button
                  class="hidden lg:flex w-7 h-9 items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
                  @click="removeDraftSet(ex.instanceId, set.id)"
                ><X class="w-5 h-5" /></button>
              </div>
              </SwipeDeleteWrapper>
              <button class="text-xs text-primary hover:underline mt-1" @click="addDraftSet(ex.instanceId)">
                добавить подход
              </button>
            </div>
            <p class="mt-2 text-xs text-gray-400 flex flex-wrap gap-x-3 gap-y-1">
              <template v-if="isCardio(ex.exerciseId)">
                <span>Итого: {{ ex.sets.filter(s => !s.failed).reduce((s, set) => s + (set.reps || 0), 0) }} мин.</span>
              </template>
              <template v-else>
                <template v-for="st in [strengthSummary(ex)]" :key="'st'">
                  <span>Тоннаж: {{ st.tonnage }} кг</span>
                  <span v-if="st.lifts" title="Подъёмы в рабочих подходах (от 50% 1ПМ)">КПШ: {{ st.lifts }}</span>
                  <span v-if="st.avgWeight" title="Абсолютная интенсивность — средний вес подъёма в рабочих подходах (от 50% 1ПМ)">Абс. инт.: {{ st.avgWeight }} кг</span>
                  <span v-if="st.relIntensity != null" :title="`Относительная интенсивность — от 1ПМ ${st.baseline1RM} кг`">Отн. инт.: {{ st.relIntensity }}%</span>
                  <span v-if="st.e1RM">Расч. 1ПМ: {{ st.e1RM }} кг</span>
                </template>
              </template>
            </p>
          </div>
        </SwipeDeleteWrapper>
      </template>
    </draggable>

    <!-- Exercises: view mode -->
    <div v-else class="space-y-4">
      <div v-for="(ex, idx) in workout.exercises" :key="ex.instanceId || ex.exerciseId + idx" class="card p-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <div v-for="(set, i) in ex.sets" :key="set.id" class="flex items-center gap-1 text-sm">
            <span class="text-gray-400 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>
            <template v-if="isCardio(ex.exerciseId)">
              <span :class="['font-medium', set.failed ? 'line-through text-gray-400' : '']">{{ set.reps }} мин.</span>
            </template>
            <template v-else>
              <span :class="['font-medium', set.failed ? 'line-through text-gray-400' : '']">{{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}</span>
              <span class="text-gray-400">×</span>
              <span :class="['font-medium', set.failed ? 'line-through text-gray-400' : '']">{{ set.reps }} повт.</span>
              <span v-if="set.rpe" class="text-xs text-gray-400">РПЕ {{ set.rpe }}</span>
            </template>
            <span :class="['ml-auto text-xs font-medium', set.completed ? 'text-green-500' : set.failed ? 'text-red-400' : 'text-gray-300']">
              {{ set.completed ? '✓' : set.failed ? '✗' : '○' }}
            </span>
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-400 flex flex-wrap gap-x-3 gap-y-1">
          <template v-if="isCardio(ex.exerciseId)">
            <span>Итого: {{ ex.sets.filter(s => !s.failed).reduce((s, set) => s + (set.reps || 0), 0) }} мин.</span>
          </template>
          <template v-else>
            <template v-for="st in [strengthSummary(ex)]" :key="'st'">
              <span>Тоннаж: {{ st.tonnage }} кг</span>
              <span v-if="st.lifts" title="Подъёмы в рабочих подходах (от 50% 1ПМ)">КПШ: {{ st.lifts }}</span>
              <span v-if="st.avgWeight" title="Абсолютная интенсивность — средний вес подъёма в рабочих подходах (от 50% 1ПМ)">Абс. инт.: {{ st.avgWeight }} кг</span>
              <span v-if="st.relIntensity != null" :title="`Относительная интенсивность — от 1ПМ ${st.baseline1RM} кг`">Отн. инт.: {{ st.relIntensity }}%</span>
              <span v-if="st.e1RM">Расч. 1ПМ: {{ st.e1RM }} кг</span>
            </template>
          </template>
        </p>
      </div>
      <div v-if="!workout.exercises.length" class="text-center py-8 text-gray-400">Упражнения не записаны</div>
    </div>

    <!-- Add exercise button in edit mode -->
    <button
      v-if="isEditing"
      class="mt-2 w-full card p-3 flex items-center justify-center gap-2 text-sm text-primary hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      @click="showPicker = true"
    >
      <Plus class="w-4 h-4" />
      Добавить упражнение
    </button>

    <ExercisePicker
      v-model="showPicker"
      :added-ids="draftAddedIds"
      @pick="addDraftExercise"
    />

    <!-- Likes & Comments section -->
    <WorkoutSocialPanel
      v-if="!isEditing"
      class="mt-6"
      :workout-id="workout.id"
      :coach-ids="myCoachIds"
    />
  </div>

  <div v-else class="text-center py-16 text-gray-400">
    Тренировка не найдена
  </div>

  <ExportModal v-model="exportModalOpen" :workouts="workout ? [workout] : []" lock-period />

  <BaseModal v-model="showSaveTemplate" title="Сохранить как шаблон" max-width="sm">
    <BaseInput v-model="templateName" label="Название шаблона" placeholder="Например: Push day" />
    <template #footer>
      <BaseButton variant="ghost" @click="showSaveTemplate = false">Отмена</BaseButton>
      <BaseButton :disabled="!templateName.trim()" :loading="savingTemplate" @click="saveAsTemplate">Сохранить</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, Pencil, X, Plus, RefreshCw, Trash2, Download, GripVertical, LayoutTemplate } from 'lucide-vue-next'
import WorkoutSocialPanel from '@/components/social/WorkoutSocialPanel.vue'
import draggable from 'vuedraggable'
import ExportModal from '@/components/ui/ExportModal.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import StepperInput from '@/components/ui/StepperInput.vue'
import ExercisePicker from '@/components/workout/ExercisePicker.vue'
import ExerciseCompactCard from '@/components/workout/ExerciseCompactCard.vue'
import ExerciseViewModeToggle from '@/components/workout/ExerciseViewModeToggle.vue'
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'
import { useExerciseViewMode } from '@/composables/useExerciseViewMode.js'
import { WORKOUT_TYPES } from '@/services/mockData.js'
import workoutService from '@/services/workoutService.js'
import { sessionE1RM, sessionLoad, round1 } from '@/utils/strength.js'

const route = useRoute()
const router = useRouter()
const store = useStore()
const viewMode = useExerciseViewMode()

const fetchedWorkout = ref(null)

const workout = computed(() =>
  store.getters['workouts/workoutById'](route.params.id) ??
  store.state.social.feed.find(w => w.id === route.params.id) ??
  fetchedWorkout.value ??
  null
)

onMounted(async () => {
  const id = route.params.id
  // Someone else's workout that isn't in the feed cache — fetch it.
  // Likes and comments load in WorkoutSocialPanel.
  if (!store.getters['workouts/workoutById'](id) && !store.state.social.feed.find(w => w.id === id)) {
    try {
      fetchedWorkout.value = await workoutService.fetchSocialWorkout(id)
    } catch { /* no access or not found */ }
  }
})

// Comments from my coach(es) get a "тренер" mark.
const myCoachIds = computed(() => store.getters['coach/myCoaches'].map(l => l.coachId))

const currentUserId = computed(() => store.state.auth.userId)
const isOwner = computed(() => {
  const w = workout.value
  if (!w) return false
  return !('userId' in w) || w.userId === currentUserId.value
})
const isSocialWorkout = computed(() => workout.value && 'userId' in workout.value)

const exerciseLibrary = computed(() => store.state.exercises.library)
// Per-exercise load for this workout. Relative intensity uses the same
// 1RM baseline as the exercise progress chart (profile max or best estimate
// up to this date), topped up by the live sets so it stays sane while editing.
function strengthSummary(ex) {
  const sets = ex.sets.filter(s => !s.failed)
  const e1RM = sessionE1RM(sets)
  const session = store.getters['exercises/progressForExercise'](ex.exerciseId)
    .find(s => s.workoutId === workout.value?.id)
  const baseline1RM = Math.max(session?.baseline1RM || 0, e1RM)
  const { lifts, tonnage, avgWeight } = sessionLoad(sets, baseline1RM)
  return {
    tonnage,
    lifts,
    avgWeight: round1(avgWeight),
    e1RM: Math.round(e1RM),
    baseline1RM: Math.round(baseline1RM),
    relIntensity: baseline1RM && avgWeight ? Math.round(avgWeight / baseline1RM * 100) : null,
  }
}

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
    isCardio(ex.exerciseId) ? total : total + ex.sets.filter(s => !s.failed).reduce((s, set) => s + set.weight * set.reps, 0), 0) ?? 0
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
const exportModalOpen = ref(false)
const showPicker = ref(false)
const showSaveTemplate = ref(false)
const templateName = ref('')
const savingTemplate = ref(false)

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
  draft.value.exercises.forEach(ex => {
    if (!ex.instanceId) ex.instanceId = uid()
  })
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  draft.value = null
}

function onBack() {
  if (isEditing.value) { cancelEdit() } else { history.back() }
}

async function repeatWorkout() {
  await store.dispatch('workouts/startWorkoutFromHistory', workout.value)
  router.push('/workouts/new')
}

async function saveAsTemplate() {
  savingTemplate.value = true
  try {
    await store.dispatch('templates/createTemplate', {
      title: templateName.value.trim(),
      type: workout.value.type,
      exercises: workout.value.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.filter(s => !s.failed).map(s => ({ weight: s.weight, reps: s.reps })),
      })),
    })
    store.dispatch('ui/showToast', { message: 'Шаблон сохранён', type: 'success' })
    showSaveTemplate.value = false
    templateName.value = ''
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    savingTemplate.value = false
  }
}


function updateDraftSet(instanceId, setId, field, value) {
  const ex = draft.value.exercises.find(e => e.instanceId === instanceId)
  if (!ex) return
  const set = ex.sets.find(s => s.id === setId)
  if (set) set[field] = value
}

function onDraftRpeChange(instanceId, setId, e) {
  const raw = e.target.value.trim()
  if (!raw) { e.target.value = ''; updateDraftSet(instanceId, setId, 'rpe', null); return }
  const num = parseFloat(raw.replace(',', '.'))
  if (isNaN(num)) { e.target.value = ''; return }
  // RPE is conventionally whole or half points (7, 7.5, 8...) — snap to it.
  const clamped = Math.min(10, Math.max(1, Math.round(num * 2) / 2))
  e.target.value = String(clamped)
  updateDraftSet(instanceId, setId, 'rpe', clamped)
}

function cycleDraftSetState(instanceId, setId, set) {
  if (!set.completed && !set.failed) {
    updateDraftSet(instanceId, setId, 'completed', true)
    updateDraftSet(instanceId, setId, 'failed', false)
  } else if (set.completed) {
    updateDraftSet(instanceId, setId, 'completed', false)
    updateDraftSet(instanceId, setId, 'failed', true)
  } else {
    updateDraftSet(instanceId, setId, 'failed', false)
  }
}

function removeDraftSet(instanceId, setId) {
  const ex = draft.value.exercises.find(e => e.instanceId === instanceId)
  if (!ex) return
  ex.sets = ex.sets.filter(s => s.id !== setId)
}

function removeDraftExercise(instanceId) {
  draft.value.exercises = draft.value.exercises.filter(e => e.instanceId !== instanceId)
}

function addDraftExercise(exercise) {
  showPicker.value = false
  draft.value.exercises.push({
    instanceId: uid(),
    exerciseId: exercise.id,
    exerciseName: exercise.name,
    sets: [{ id: uid(), weight: 0, reps: 0, completed: false, failed: false, rpe: null }]
  })
}

function addDraftSet(instanceId) {
  const ex = draft.value.exercises.find(e => e.instanceId === instanceId)
  if (!ex) return
  const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
  ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps, completed: false, failed: false, rpe: null })
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
