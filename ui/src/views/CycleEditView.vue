<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="$router.back()">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <h2 class="text-xl font-bold text-gray-900">{{ isEdit ? 'Редактировать цикл' : 'Новый цикл' }}</h2>
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
        <span class="text-sm font-medium text-gray-700">Сделать цикл публичным (доступен всем пользователям)</span>
      </label>
    </div>

    <!-- Exercise columns definition -->
    <div class="card p-5 mb-4">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h3 class="font-semibold text-gray-900">Упражнения в цикле</h3>
          <p class="text-xs text-gray-400 mt-0.5">Определите список упражнений — они станут столбцами таблицы</p>
        </div>
        <BaseButton variant="outline" size="sm" @click="addExerciseCol">Добавить</BaseButton>
      </div>
      <div class="space-y-2">
        <div v-for="(col, ci) in exerciseCols" :key="ci" class="flex items-center gap-2">
          <button
            class="flex-1 input text-left truncate"
            @click="openPicker(ci)"
          >
            <span v-if="col.name" class="text-gray-800">{{ col.name }}</span>
            <span v-else class="text-gray-400 text-sm">Выбрать упражнение...</span>
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

    <!-- Workouts table -->
    <div class="card mb-4">
      <div class="flex items-center justify-between p-4 border-b border-gray-100">
        <div>
          <h3 class="font-semibold text-gray-900">Тренировки</h3>
          <p class="text-xs text-gray-400 mt-0.5">Каждая строка — одна тренировка в цикле</p>
        </div>
        <BaseButton variant="outline" size="sm" @click="addWorkout">Добавить строку</BaseButton>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="text-left px-3 py-2 text-xs font-semibold text-gray-500 w-12">#</th>
              <th
                v-for="col in exerciseCols"
                :key="col.name || col.id"
                class="text-left px-3 py-2 text-xs font-semibold text-gray-700 min-w-[220px]"
              >{{ col.name || '—' }}</th>
              <th class="w-8"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="(workout, wi) in form.workouts" :key="wi" class="align-top">
              <td class="px-3 py-2 text-gray-400 font-bold text-xs pt-3">{{ wi + 1 }}</td>
              <td v-for="(col, ci) in exerciseCols" :key="ci" class="px-2 py-2">
                <div class="space-y-1">
                  <div
                    v-for="(set, si) in getWorkoutSets(wi, ci)"
                    :key="si"
                    class="flex items-center gap-1"
                  >
                    <StepperInput
                      class="flex-1"
                      :model-value="set.percent_1rm"
                      :step="2.5"
                      :min="0"
                      placeholder="%"
                      @update:model-value="updateSet(wi, ci, si, 'percent_1rm', $event)"
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
                      @click="removeSet(wi, ci, si)"
                    >
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <button class="text-xs text-primary hover:text-primary/80 font-medium mt-3 py-1" @click="addSet(wi, ci)">+ подход</button>
                </div>
              </td>
              <td class="px-2 py-2 pt-3">
                <button
                  class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors disabled:opacity-30"
                  @click="removeWorkout(wi)"
                  :disabled="form.workouts.length <= 1"
                >
                  <X class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Bulk add workouts -->
      <div class="p-4 border-t border-gray-100 flex flex-wrap items-center gap-3">
        <span class="text-sm text-gray-600">Добавить сразу</span>
        <input v-model.number="bulkCount" type="number" min="1" max="50" class="input w-20 text-center text-sm" inputmode="numeric" />
        <span class="text-sm text-gray-600">тренировок</span>
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
          <div class="font-medium text-gray-800 text-sm">{{ ex.name }}</div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, X } from 'lucide-vue-next'
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
  exerciseCols.value[pickerColIndex.value] = { id: ex.id, name: ex.name }
  showExercisePicker.value = false
}

// Initialize a workout row with empty sets for each exercise column
function newWorkoutRow() {
  return { exercises: exerciseCols.value.map(() => ({ sets: [] })) }
}

function addWorkout() {
  form.workouts.push(newWorkoutRow())
}

function removeWorkout(wi) {
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
  const sets = form.workouts[wi].exercises[ci].sets
  const last = sets[sets.length - 1]
  sets.push({ percent_1rm: last?.percent_1rm ?? 75, reps: last?.reps ?? 5 })
}

function removeSet(wi, ci, si) {
  form.workouts[wi].exercises[ci].sets.splice(si, 1)
}

function updateSet(wi, ci, si, field, value) {
  form.workouts[wi].exercises[ci].sets[si][field] = value
}

// Build API payload
function buildPayload() {
  return {
    title: form.title.trim(),
    description: form.description.trim(),
    author_name: form.author_name.trim(),
    is_public: form.is_public,
    workouts: form.workouts.map((w, wi) => ({
      workout_number: wi + 1,
      title: '',
      notes: '',
      exercises: exerciseCols.value
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
  exerciseCols.value = seenCols.length ? seenCols : [{ id: null, name: '' }]

  form.workouts = cycle.workouts.map(w => ({
    exercises: seenCols.map(col => {
      const ex = w.exercises.find(e => e.exercise_name === col.name)
      return { sets: ex?.sets.map(s => ({ percent_1rm: s.percent_1rm, reps: s.reps })) ?? [] }
    }),
  }))
}

onMounted(async () => {
  // Ensure exercises library is loaded
  if (!store.state.exercises.library.length) {
    await store.dispatch('exercises/initExercises')
  }
  if (isEdit.value) {
    const cycle = await store.dispatch('cycles/fetchCycle', route.params.id)
    loadCycle(cycle)
  } else {
    form.workouts.push(newWorkoutRow())
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
    store.dispatch('ui/showToast', { message: isEdit.value ? 'Цикл обновлён' : 'Цикл создан!', type: 'success' })
    router.push(`/cycles/${saved.id}`)
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка сохранения', type: 'error' })
  } finally {
    saving.value = false
  }
}
</script>
