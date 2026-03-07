<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
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
        <BaseButton variant="outline" size="sm" @click="addExerciseCol">+ Добавить</BaseButton>
      </div>
      <div class="space-y-2">
        <div v-for="(col, ci) in exerciseCols" :key="ci" class="flex items-center gap-2">
          <input
            v-model="exerciseCols[ci]"
            class="input flex-1"
            :placeholder="`Упражнение ${ci + 1}`"
            @blur="syncExerciseName(ci)"
          />
          <button class="text-gray-300 hover:text-red-400 transition-colors p-1" @click="removeExerciseCol(ci)" :disabled="exerciseCols.length <= 1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
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
        <BaseButton variant="outline" size="sm" @click="addWorkout">+ Добавить строку</BaseButton>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="text-left px-3 py-2 text-xs font-semibold text-gray-500 w-12">#</th>
              <th
                v-for="col in exerciseCols"
                :key="col"
                class="text-left px-3 py-2 text-xs font-semibold text-gray-700 min-w-52"
              >{{ col || '—' }}</th>
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
                    <input
                      :value="set.percent_1rm"
                      @input="updateSet(wi, ci, si, 'percent_1rm', +$event.target.value)"
                      type="number"
                      min="0"
                      max="200"
                      step="2.5"
                      class="input text-xs px-2 py-1 w-16 text-center"
                      placeholder="%"
                    />
                    <span class="text-gray-400 text-xs">×</span>
                    <input
                      :value="set.reps"
                      @input="updateSet(wi, ci, si, 'reps', +$event.target.value)"
                      type="number"
                      min="1"
                      class="input text-xs px-2 py-1 w-12 text-center"
                      placeholder="повт"
                    />
                    <button class="text-gray-200 hover:text-red-400 transition-colors" @click="removeSet(wi, ci, si)">×</button>
                  </div>
                  <button class="text-xs text-primary hover:text-primary/80 font-medium mt-0.5" @click="addSet(wi, ci)">+ подход</button>
                </div>
              </td>
              <td class="px-2 py-2 pt-3">
                <button class="text-gray-200 hover:text-red-400 transition-colors" @click="removeWorkout(wi)" :disabled="form.workouts.length <= 1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Bulk add workouts -->
      <div class="p-4 border-t border-gray-100 flex items-center gap-3">
        <span class="text-sm text-gray-600">Добавить сразу</span>
        <input v-model.number="bulkCount" type="number" min="1" max="50" class="input w-20 text-center text-sm" />
        <span class="text-sm text-gray-600">тренировок</span>
        <BaseButton variant="ghost" size="sm" @click="bulkAdd">Добавить</BaseButton>
      </div>
    </div>

    <!-- Save -->
    <div class="flex gap-3">
      <BaseButton variant="ghost" @click="$router.back()">Отмена</BaseButton>
      <BaseButton class="flex-1" :loading="saving" :disabled="!form.title.trim()" @click="save">
        {{ isEdit ? 'Сохранить изменения' : 'Создать цикл' }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

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
  workouts: [],  // [{ exercises: [{ sets: [{ percent_1rm, reps }] }] }] — indexed by exerciseCols
})

// Exercise column names (define the "columns" of the table)
const exerciseCols = ref(['Основное упражнение'])

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
  exerciseCols.value.push('')
  // Add empty exercise slot to each existing workout row
  form.workouts.forEach(w => w.exercises.push({ sets: [] }))
}

function removeExerciseCol(ci) {
  if (exerciseCols.value.length <= 1) return
  exerciseCols.value.splice(ci, 1)
  form.workouts.forEach(w => w.exercises.splice(ci, 1))
}

function syncExerciseName(_ci) {
  // Nothing needed — exerciseCols is reactive and table headers re-render
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
        .map((name, ci) => ({
          exercise_name: name.trim() || `Упражнение ${ci + 1}`,
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

  // Collect unique exercise names in order
  const seenCols = []
  const seenSet = new Set()
  for (const w of cycle.workouts) {
    for (const e of w.exercises) {
      if (!seenSet.has(e.exercise_name)) {
        seenSet.add(e.exercise_name)
        seenCols.push(e.exercise_name)
      }
    }
  }
  exerciseCols.value = seenCols.length ? seenCols : ['Основное упражнение']

  form.workouts = cycle.workouts.map(w => ({
    exercises: seenCols.map(colName => {
      const ex = w.exercises.find(e => e.exercise_name === colName)
      return { sets: ex?.sets.map(s => ({ percent_1rm: s.percent_1rm, reps: s.reps })) ?? [] }
    }),
  }))
}

onMounted(async () => {
  if (isEdit.value) {
    const cycle = await store.dispatch('cycles/fetchCycle', route.params.id)
    loadCycle(cycle)
  } else {
    // Default: 1 exercise column, 1 empty workout row
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
