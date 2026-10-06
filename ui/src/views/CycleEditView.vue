<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors" @click="$router.back()">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ isEdit ? 'Редактировать цикл' : 'Новый цикл' }}</h2>
    </div>

    <!-- Unsaved edits from an earlier visit -->
    <div v-if="draftOffer" class="card p-4 mb-4 border-l-4 border-l-primary flex items-center gap-3 flex-wrap" role="status">
      <History class="w-5 h-5 text-primary flex-shrink-0" />
      <p class="flex-1 min-w-[12rem] text-sm text-ink dark:text-white">
        Есть несохранённые изменения {{ isEdit ? 'этого цикла' : 'нового цикла' }} от {{ formatDraftTime(draftOffer.savedAt) }}.
      </p>
      <div class="flex gap-2">
        <BaseButton size="sm" @click="restoreDraft">Продолжить редактирование</BaseButton>
        <BaseButton size="sm" variant="ghost" @click="discardDraft">Отбросить</BaseButton>
      </div>
    </div>

    <!-- Meta -->
    <div class="card p-5 mb-4 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <BaseInput v-model="form.title" label="Название цикла" placeholder="Жимовой цикл Суровецкого" />
        <BaseInput v-model="form.author_name" label="Автор программы" placeholder="Аскольд Суровецкий" />
      </div>
      <div>
        <label class="label">Описание</label>
        <textarea v-model="form.description" class="input resize-none" rows="2" placeholder="Краткое описание программы..." />
      </div>
      <label class="flex items-center gap-3 cursor-pointer">
        <input type="checkbox" v-model="form.is_public" class="w-4 h-4 rounded text-primary" />
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Сделать цикл публичным (доступен всем пользователям)</span>
      </label>
    </div>

    <!-- Exercise columns definition -->
    <div class="card p-5 mb-4">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Упражнения в цикле</h3>
          <p class="text-xs text-gray-400 mt-0.5">Определите список упражнений — они станут столбцами таблицы. Отметьте основные: по ним строятся графики цикла.</p>
        </div>
        <BaseButton variant="outline" size="sm" @click="addExerciseCol">Добавить</BaseButton>
      </div>
      <div class="space-y-2">
        <div v-for="(col, ci) in exerciseCols" :key="ci" class="flex items-center gap-2">
          <button
            class="flex-1 input text-left truncate"
            @click="openPicker(ci)"
          >
            <span v-if="col.name" class="text-gray-800 dark:text-gray-100">{{ col.name }}</span>
            <span v-else class="text-gray-400 text-sm">Выбрать упражнение...</span>
          </button>
          <button
            type="button"
            :class="['h-10 px-3 rounded-xl border text-xs font-medium inline-flex items-center gap-1.5 flex-shrink-0 transition-colors',
              col.main ? 'bg-primary/10 border-primary/30 text-primary' : 'border-steel-100 dark:border-steel-700 text-steel-700 dark:text-steel-300 hover:border-steel-300']"
            :aria-pressed="!!col.main"
            title="Основное упражнение цикла — по нему строятся графики"
            @click="col.main = !col.main"
          >
            <Star :class="['w-3.5 h-3.5', col.main ? 'fill-current' : '']" />
            <span class="hidden sm:inline">Основное</span>
          </button>
          <button
            class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 disabled:opacity-30"
            :disabled="exerciseCols.length <= 1"
            @click="removeExerciseCol(ci)"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Live load of the table below; can be pinned while editing it -->
    <CyclePlanCharts class="mb-4" pinnable :workouts="livePayload.workouts" :main-exercises="livePayload.main_exercises" />

    <!-- Workouts table; on a computer it can take over the whole screen -->
    <div
      :class="expanded
        ? 'fixed inset-0 z-50 flex flex-col bg-card dark:bg-steel-900 pt-safe-top'
        : 'card mb-4'"
      role="region"
      aria-label="Тренировки цикла"
    >
      <div class="flex items-center justify-between gap-3 p-4 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Тренировки</h3>
          <p class="text-xs text-gray-400 mt-0.5">
            Цикл хранится в % от 1ПМ, поэтому подходит любому атлету —
            килограммы считаются при раскладке. В режиме «кг» проценты пересчитываются от указанного 1ПМ.
          </p>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5" role="group" aria-label="Единицы веса">
            <button
              v-for="u in unitOptions" :key="u.value" type="button"
              :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                unit === u.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white']"
              :aria-pressed="unit === u.value"
              @click="setUnit(u.value)"
            >{{ u.label }}</button>
          </div>
          <BaseButton variant="outline" size="sm" @click="addWorkout">Добавить тренировку</BaseButton>
          <button
            type="button"
            class="hidden lg:inline-flex btn btn-ghost px-3 py-1.5 min-h-0 text-sm"
            :title="expanded ? 'Свернуть (Esc)' : 'Развернуть таблицу на весь экран'"
            @click="toggleExpanded"
          >
            <component :is="expanded ? Minimize2 : Maximize2" class="w-4 h-4" />
            {{ expanded ? 'Свернуть' : 'Развернуть' }}
          </button>
        </div>
      </div>

      <div :class="expanded ? 'flex-1 overflow-auto' : 'overflow-x-auto'">
        <table class="w-full text-sm">
          <thead>
            <tr :class="['bg-gray-50 dark:bg-gray-800 border-b border-gray-100 dark:border-gray-800', expanded ? 'sticky top-0 z-10' : '']">
              <th
                v-for="col in exerciseCols"
                :key="col.name || col.id"
                class="text-left px-3 py-2 text-xs font-semibold text-gray-700 dark:text-gray-200 min-w-[320px]"
              >
                {{ col.name || '—' }}
                <span v-if="!inKg(col)" class="block font-normal text-steel-700 dark:text-steel-300">% от 1ПМ × повторы</span>
                <span v-else class="block font-normal text-steel-700 dark:text-steel-300">кг × повторы</span>
                <!-- 1RM the kg ↔ % conversion uses for this lift -->
                <label v-if="unit === 'kg'" class="mt-1.5 flex items-center gap-1.5 font-normal text-steel-700 dark:text-steel-300">
                  1ПМ
                  <input
                    type="number" min="0" step="2.5" inputmode="decimal"
                    :value="refMax[col.name] ?? ''"
                    placeholder="—"
                    class="input w-20 min-h-0 py-1 px-2 text-xs text-right tabular-nums"
                    @input="setRefMax(col.name, $event.target.value)"
                  />
                  кг
                  <span v-if="!inKg(col)" class="text-danger">— введите, чтобы считать в кг</span>
                </label>
              </th>
            </tr>
          </thead>
          <!-- One group per workout: a title bar spanning the lifts, then its sets -->
          <tbody v-for="(workout, wi) in form.workouts" :key="wi" class="border-t border-steel-100 dark:border-steel-700">
            <tr>
              <td :colspan="exerciseCols.length" class="p-0 bg-steel-50/80 dark:bg-steel-950/40">
                <!-- Sticks to the left edge while the lifts scroll sideways, so the
                     copy actions stay in view however many lifts the cycle has. -->
                <div class="sticky left-0 w-fit max-w-[calc(100vw-2.5rem)] lg:max-w-[52rem] flex items-center gap-x-2 gap-y-1.5 flex-wrap px-3 py-2">
                  <span class="h-7 min-w-[2.25rem] px-2 rounded-lg bg-primary/10 text-primary text-sm font-display font-semibold flex items-center justify-center tabular-nums flex-shrink-0">
                    Т{{ wi + 1 }}
                  </span>
                  <input
                    v-model="workout.title"
                    maxlength="200"
                    class="w-56 sm:w-72 max-w-full bg-transparent rounded-lg px-2 py-1 font-semibold text-ink dark:text-white placeholder:font-normal placeholder:text-steel-300 border border-transparent hover:border-steel-100 dark:hover:border-steel-700 focus:border-primary focus:bg-card dark:focus:bg-steel-900 focus:outline-none transition-colors"
                    placeholder="Название, например «Тяжёлый жим»"
                    :aria-label="`Название тренировки ${wi + 1}`"
                  />

                  <div class="flex items-center gap-1 flex-shrink-0 text-xs">
                    <template v-if="lastCopy?.wi === wi">
                      <span class="text-steel-700 dark:text-steel-300">Подходы из Т{{ lastCopy.from + 1 }}</span>
                      <button type="button" class="px-2 py-1 rounded-lg font-medium text-primary hover:bg-primary/10" @click="undoCopy">Отменить</button>
                    </template>
                    <template v-else>
                      <button
                        v-if="wi > 0"
                        type="button"
                        class="px-2 py-1 rounded-lg font-medium text-primary hover:bg-primary/10 inline-flex items-center gap-1"
                        :title="`Скопировать все подходы из Т${wi}`"
                        @click="copyWorkout(wi - 1, wi)"
                      ><Copy class="w-3.5 h-3.5" />Как в Т{{ wi }}</button>
                      <select
                        v-if="form.workouts.length > 2"
                        class="h-7 rounded-lg border border-steel-100 dark:border-steel-700 bg-card dark:bg-steel-900 text-steel-700 dark:text-steel-300 px-1.5 text-xs"
                        :aria-label="`Скопировать подходы в Т${wi + 1} из другой тренировки`"
                        @change="copyWorkout(Number($event.target.value), wi); $event.target.value = ''"
                      >
                        <option value="">Скопировать из…</option>
                        <option v-for="src in otherWorkouts(wi)" :key="src.i" :value="src.i">
                          Т{{ src.i + 1 }}{{ src.title ? ` · ${src.title}` : '' }}
                        </option>
                      </select>
                    </template>
                    <button
                      type="button"
                      class="w-7 h-7 flex items-center justify-center rounded-lg text-steel-700 dark:text-steel-300 hover:text-ink hover:bg-steel-100 dark:hover:bg-steel-700"
                      :title="`Дублировать Т${wi + 1} — копия встанет следующей`"
                      :aria-label="`Дублировать тренировку ${wi + 1}`"
                      @click="duplicateWorkout(wi)"
                    ><CopyPlus class="w-3.5 h-3.5" /></button>
                    <button
                      type="button"
                      class="w-7 h-7 flex items-center justify-center rounded-lg text-steel-300 hover:text-primary hover:bg-primary/10 disabled:opacity-30 disabled:pointer-events-none"
                      :disabled="form.workouts.length <= 1"
                      :aria-label="`Удалить тренировку ${wi + 1}`"
                      title="Удалить тренировку"
                      @click="removeWorkout(wi)"
                    ><Trash2 class="w-3.5 h-3.5" /></button>
                  </div>
                </div>
              </td>
            </tr>
            <tr class="align-top">
              <td v-for="(col, ci) in exerciseCols" :key="ci" class="px-2 py-2">
                <!-- Which lift this is, repeated per workout — the column header is long gone by T8 -->
                <p class="text-xs font-medium text-steel-700 dark:text-steel-300 mb-1.5 px-0.5 flex items-center gap-1 min-w-0">
                  <Star v-if="col.main" class="w-3 h-3 text-primary fill-current flex-shrink-0" aria-label="основное" />
                  <span class="truncate">{{ col.name || `Упражнение ${ci + 1}` }}</span>
                </p>
                <div class="space-y-1">
                  <div
                    v-for="(set, si) in getWorkoutSets(wi, ci)"
                    :key="si"
                    class="flex items-center gap-1"
                  >
                    <StepperInput
                      class="flex-1"
                      :model-value="inKg(col) ? toKg(col, set.percent_1rm) : set.percent_1rm"
                      :step="2.5"
                      :min="0"
                      :decimals="1"
                      :placeholder="inKg(col) ? 'кг' : '%'"
                      :suffix="inKg(col) ? 'кг' : '%'"
                      @update:model-value="updateSet(wi, ci, si, 'percent_1rm', inKg(col) ? toPercent(col, $event) : $event)"
                    />
                    <span class="text-gray-400 text-xs flex-shrink-0">×</span>
                    <StepperInput
                      class="flex-1"
                      :model-value="set.reps"
                      :step="1"
                      :min="1"
                      placeholder="повт"
                      @update:model-value="updateSet(wi, ci, si, 'reps', $event)"
                    />
                    <button
                      class="w-7 h-9 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
                      :aria-label="`Удалить подход ${si + 1}`"
                      @click="removeSet(wi, ci, si)"
                    >
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div class="flex items-center gap-3 mt-2">
                    <button class="text-xs text-primary hover:text-primary/80 font-medium py-1" @click="addSet(wi, ci)">+ подход</button>
                    <button
                      v-if="previousWith(wi, ci) !== -1"
                      class="text-xs text-steel-700 dark:text-steel-300 hover:text-primary font-medium py-1 inline-flex items-center gap-1"
                      :title="`Скопировать подходы «${col.name || 'упражнения'}» из Т${previousWith(wi, ci) + 1}`"
                      @click="copyExercise(previousWith(wi, ci), wi, ci)"
                    ><Copy class="w-3 h-3" />как в Т{{ previousWith(wi, ci) + 1 }}</button>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Bulk add workouts -->
      <div class="p-4 border-t border-gray-100 dark:border-gray-800 flex flex-wrap items-center gap-3">
        <span class="text-sm text-gray-600 dark:text-gray-400">Добавить сразу</span>
        <input v-model.number="bulkCount" type="number" min="1" max="50" class="input w-20 text-center text-sm" inputmode="numeric" />
        <span class="text-sm text-gray-600 dark:text-gray-400">тренировок</span>
        <BaseButton variant="outline" @click="bulkAdd">Добавить</BaseButton>
      </div>
    </div>

    <!-- Save -->
    <div class="flex gap-3">
      <BaseButton variant="outline" @click="$router.back()">Отмена</BaseButton>
      <BaseButton class="flex-1" :loading="saving" :disabled="!form.title.trim()" @click="save">
        {{ isEdit ? 'Сохранить изменения' : 'Создать цикл' }}
      </BaseButton>
    </div>
  </div>

  <!-- Exercise picker modal -->
  <BaseModal v-model="showExercisePicker" title="Выбрать упражнение" :fullscreen="true">
    <div class="space-y-3">
      <input
        v-model="exerciseSearch"
        class="input"
        placeholder="Поиск по названию или группе мышц..."
        autofocus
      />
      <div class="space-y-1 max-h-[60vh] overflow-y-auto">
        <button
          v-for="ex in filteredPickerExercises"
          :key="ex.id"
          class="w-full text-left px-3 py-2.5 rounded-xl hover:bg-primary/5 transition-colors border border-transparent hover:border-primary/20"
          @click="selectExercise(ex)"
        >
          <div class="font-medium text-gray-800 dark:text-gray-100 text-sm">{{ ex.name }}</div>
          <div class="text-xs text-gray-400 mt-0.5">{{ ex.muscleGroup }} · {{ ex.equipment }}</div>
        </button>
        <p v-if="!filteredPickerExercises.length" class="text-center text-sm text-gray-400 py-6">Ничего не найдено</p>
      </div>
    </div>
    <template #footer>
      <button class="btn btn-danger w-full sm:w-auto" @click="showExercisePicker = false">Отмена</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, X, Star, Copy, CopyPlus, Trash2, History, Maximize2, Minimize2 } from 'lucide-vue-next'
import CyclePlanCharts from '@/components/exercises/CyclePlanCharts.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import StepperInput from '@/components/ui/StepperInput.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const bulkCount = ref(1)

// Form state
const form = reactive({
  title: '',
  description: '',
  author_name: '',
  is_public: false,
  workouts: [],
})

// Exercise columns — each is { id: string|null, name: string }
const exerciseCols = ref([{ id: null, name: '' }])

// Exercise picker state
const showExercisePicker = ref(false)
const pickerColIndex = ref(null)
const exerciseSearch = ref('')

const allExercises = computed(() => store.state.exercises.library)
const filteredPickerExercises = computed(() => {
  const q = exerciseSearch.value.toLowerCase().trim()
  if (!q) return allExercises.value
  return allExercises.value.filter(e =>
    e.name.toLowerCase().includes(q) || e.muscleGroup.toLowerCase().includes(q)
  )
})

function openPicker(ci) {
  pickerColIndex.value = ci
  exerciseSearch.value = ''
  showExercisePicker.value = true
}

function selectExercise(ex) {
  const prev = exerciseCols.value[pickerColIndex.value]
  exerciseCols.value[pickerColIndex.value] = { id: ex.id, name: ex.name, main: !!prev?.main }
  prefillRefMaxes()
  showExercisePicker.value = false
}

// Initialize a workout row with empty sets for each exercise column
function newWorkoutRow() {
  return { title: '', notes: '', exercises: exerciseCols.value.map(() => ({ sets: [] })) }
}

function addWorkout() {
  form.workouts.push(newWorkoutRow())
}

// ── Copying sets between workouts ────────────────────────────────────────
// Copying replaces the target's sets, so the last copy can be undone.
const lastCopy = ref(null)   // { wi, from, prev: exercises snapshot }
const cloneSets = sets => sets.map(s => ({ ...s }))
const cloneExercises = w => w.exercises.map(e => ({ sets: cloneSets(e.sets) }))

function copyWorkout(from, to) {
  if (Number.isNaN(from) || from === to) return
  lastCopy.value = { wi: to, from, prev: cloneExercises(form.workouts[to]) }
  form.workouts[to].exercises = cloneExercises(form.workouts[from])
}

// The nearest earlier workout that trains this lift (-1 if none): squats
// skipped on a bench day still copy from the last squat day.
function previousWith(wi, ci) {
  for (let i = wi - 1; i >= 0; i--) if (getWorkoutSets(i, ci).length) return i
  return -1
}

function copyExercise(from, to, ci) {
  lastCopy.value = { wi: to, from, prev: cloneExercises(form.workouts[to]) }
  form.workouts[to].exercises[ci].sets = cloneSets(form.workouts[from].exercises[ci].sets)
}

function otherWorkouts(wi) {
  return form.workouts.map((w, i) => ({ i, title: w.title })).filter(w => w.i !== wi)
}

function undoCopy() {
  const { wi, prev } = lastCopy.value
  form.workouts[wi].exercises = prev
  lastCopy.value = null
}

function duplicateWorkout(wi) {
  const src = form.workouts[wi]
  form.workouts.splice(wi + 1, 0, { title: src.title, notes: src.notes, exercises: cloneExercises(src) })
  lastCopy.value = null
}

function removeWorkout(wi) {
  lastCopy.value = null
  if (form.workouts.length > 1) form.workouts.splice(wi, 1)
}

function bulkAdd() {
  for (let i = 0; i < bulkCount.value; i++) form.workouts.push(newWorkoutRow())
}

function addExerciseCol() {
  exerciseCols.value.push({ id: null, name: '' })
  form.workouts.forEach(w => w.exercises.push({ sets: [] }))
}

function removeExerciseCol(ci) {
  if (exerciseCols.value.length <= 1) return
  exerciseCols.value.splice(ci, 1)
  form.workouts.forEach(w => w.exercises.splice(ci, 1))
}

function getWorkoutSets(wi, ci) {
  return form.workouts[wi]?.exercises[ci]?.sets ?? []
}

function addSet(wi, ci) {
  lastCopy.value = null  // a manual edit makes the copy's undo stale
  const sets = form.workouts[wi].exercises[ci].sets
  const last = sets[sets.length - 1]
  sets.push({ percent_1rm: last?.percent_1rm ?? 75, reps: last?.reps ?? 5 })
}

function removeSet(wi, ci, si) {
  lastCopy.value = null  // a manual edit makes the copy's undo stale
  form.workouts[wi].exercises[ci].sets.splice(si, 1)
}

function updateSet(wi, ci, si, field, value) {
  lastCopy.value = null  // a manual edit makes the copy's undo stale
  form.workouts[wi].exercises[ci].sets[si][field] = value
}

// ── % / kg entry ─────────────────────────────────────────────────────────
// The cycle is always stored in % of 1RM (so it fits any athlete); "кг" is
// only an entry mode that converts through a reference 1RM per lift —
// the user's own max by default, editable in the column header.
const UNIT_KEY = 'gym_cycle_edit_unit'
const unitOptions = [{ value: 'percent', label: '%' }, { value: 'kg', label: 'кг' }]
const unit = ref((() => { try { return localStorage.getItem(UNIT_KEY) || 'percent' } catch { return 'percent' } })())
function setUnit(u) {
  unit.value = u
  try { localStorage.setItem(UNIT_KEY, u) } catch { /* storage unavailable */ }
}

const refMax = reactive({})
function setRefMax(name, value) {
  const n = Number(value)
  refMax[name] = n > 0 ? n : null
}
// Profile maxes may arrive after the editor opens.
watch(() => store.state.user.maxes, () => prefillRefMaxes())

function prefillRefMaxes() {
  exerciseCols.value.forEach(col => {
    if (col.name && refMax[col.name] == null) {
      const own = store.state.user.maxes.find(m => m.exercise_name === col.name)
      if (own) refMax[col.name] = own.weight_kg
    }
  })
}
// A lift without a known 1RM stays in % even in kg mode — nothing to convert with.
function inKg(col) {
  return unit.value === 'kg' && refMax[col.name] > 0
}
function toKg(col, percent) {
  if (percent == null || percent === '') return null
  return Math.round(refMax[col.name] * percent / 100 / 2.5) * 2.5
}
function toPercent(col, kg) {
  if (kg == null) return null
  return Math.round(kg / refMax[col.name] * 1000) / 10
}

// Charts read the same shape the API gets, so they follow every edit.
const livePayload = computed(() => buildPayload())

// Build API payload
function buildPayload(f = form, cols = exerciseCols.value) {
  return {
    title: f.title.trim(),
    description: f.description.trim(),
    author_name: f.author_name.trim(),
    is_public: f.is_public,
    main_exercises: cols
      .filter(col => col.main && col.name.trim())
      .map(col => ({ exerciseId: col.id ?? null, exerciseName: col.name.trim() })),
    workouts: f.workouts.map((w, wi) => ({
      workout_number: wi + 1,
      title: (w.title || '').trim(),
      notes: w.notes || '',
      exercises: cols
        .map((col, ci) => ({
          exercise_id: col.id ?? null,
          exercise_name: col.name.trim() || `Упражнение ${ci + 1}`,
          sets: w.exercises[ci]?.sets.map(s => ({
            percent_1rm: Number(s.percent_1rm) || 0,
            reps: Number(s.reps) || 1,
          })) ?? [],
        }))
        .filter(e => e.sets.length > 0),
    })),
  }
}

// Populate form from existing cycle (edit mode)
function loadCycle(cycle) {
  form.title = cycle.title
  form.description = cycle.description
  form.author_name = cycle.author_name
  form.is_public = cycle.is_public

  // Collect unique exercise cols in order
  const seenCols = []
  const seenSet = new Set()
  for (const w of cycle.workouts) {
    for (const e of w.exercises) {
      if (!seenSet.has(e.exercise_name)) {
        seenSet.add(e.exercise_name)
        seenCols.push({ id: e.exercise_id ?? null, name: e.exercise_name })
      }
    }
  }
  const mainNames = new Set((cycle.main_exercises || []).map(m => m.exerciseName))
  seenCols.forEach(col => { col.main = mainNames.has(col.name) })
  exerciseCols.value = seenCols.length ? seenCols : [{ id: null, name: '' }]

  form.workouts = cycle.workouts.map(w => ({
    title: w.title || '',
    notes: w.notes || '',
    exercises: seenCols.map(col => {
      const ex = w.exercises.find(e => e.exercise_name === col.name)
      return { sets: ex?.sets.map(s => ({ percent_1rm: s.percent_1rm, reps: s.reps })) ?? [] }
    }),
  }))
}

// ── Full-screen table (desktop) ─────────────────────────────────────────
// Wide cycles with many lifts get the whole window; Esc brings the page back.
const expanded = ref(false)
function toggleExpanded() {
  expanded.value = !expanded.value
  document.body.style.overflow = expanded.value ? 'hidden' : ''
}
function onKeydown(e) {
  if (e.key === 'Escape' && expanded.value) toggleExpanded()
}
window.addEventListener('keydown', onKeydown)
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})

// ── Draft autosave ───────────────────────────────────────────────────────
// Edits are kept in this browser until saved, so leaving the page by
// accident (another tab, a misclick, a reload) loses nothing: coming back
// offers to pick up where you left off.
const draftKey = computed(() => `gym_cycle_draft_${route.params.id || 'new'}`)
const draftOffer = ref(null)
const baseline = ref(null)          // payload as loaded — what "unsaved" is measured against
const snapshot = () => JSON.stringify(buildPayload())
const isDirty = computed(() => baseline.value !== null && snapshot() !== baseline.value)

function readDraft() {
  try { return JSON.parse(localStorage.getItem(draftKey.value) || 'null') } catch { return null }
}
function clearDraft() {
  try { localStorage.removeItem(draftKey.value) } catch { /* storage unavailable */ }
}

let draftTimer = null
watch([() => form, exerciseCols], () => {
  if (baseline.value === null || draftOffer.value) return   // still loading, or an offer is pending
  clearTimeout(draftTimer)
  draftTimer = setTimeout(() => {
    if (draftOffer.value) return
    if (!isDirty.value) return clearDraft()
    try {
      localStorage.setItem(draftKey.value, JSON.stringify({
        savedAt: Date.now(),
        form: { title: form.title, description: form.description, author_name: form.author_name, is_public: form.is_public, workouts: form.workouts },
        cols: exerciseCols.value,
      }))
    } catch { /* storage full or unavailable — the page still works */ }
  }, 500)
}, { deep: true })

function restoreDraft() {
  const d = draftOffer.value
  Object.assign(form, d.form)
  exerciseCols.value = d.cols
  prefillRefMaxes()
  draftOffer.value = null
}
function discardDraft() {
  clearDraft()
  draftOffer.value = null
}
function formatDraftTime(ts) {
  return new Date(ts).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

// Closing the tab or reloading with unsaved edits gets the browser's own prompt.
function onBeforeUnload(e) {
  if (!isDirty.value) return
  e.preventDefault()
  e.returnValue = ''
}
window.addEventListener('beforeunload', onBeforeUnload)
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', onBeforeUnload)
  clearTimeout(draftTimer)
})

onMounted(async () => {
  // Ensure exercises library is loaded
  if (!store.state.exercises.library.length) {
    await store.dispatch('exercises/initExercises')
  }
  if (isEdit.value) {
    const cycle = await store.dispatch('cycles/fetchCycle', route.params.id)
    loadCycle(cycle)
    prefillRefMaxes()
  } else {
    form.workouts.push(newWorkoutRow())
  }
  baseline.value = snapshot()
  const draft = readDraft()
  if (draft) {
    // Only offer a draft that actually differs from what's saved now.
    const differs = JSON.stringify(buildPayload(draft.form, draft.cols)) !== baseline.value
    if (differs) draftOffer.value = draft
    else clearDraft()
  }
})

async function save() {
  saving.value = true
  try {
    const payload = buildPayload()
    let saved
    if (isEdit.value) {
      saved = await store.dispatch('cycles/updateCycle', { id: route.params.id, data: payload })
    } else {
      saved = await store.dispatch('cycles/createCycle', payload)
    }
    clearDraft()
    baseline.value = snapshot()
    store.dispatch('ui/showToast', { message: isEdit.value ? 'Цикл обновлён' : 'Цикл создан!', type: 'success' })
    router.push(`/cycles/${saved.id}`)
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка сохранения', type: 'error' })
  } finally {
    saving.value = false
  }
}
</script>
