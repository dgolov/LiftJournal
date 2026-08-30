<template>
  <div>
    <div class="flex flex-col gap-3 mb-4">
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Упражнения</h2>
        <div class="flex items-center gap-3 flex-wrap">
          <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 flex-wrap">
            <button
              v-for="opt in statusOptions"
              :key="opt.value"
              :class="['px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                status === opt.value ? 'bg-white dark:bg-gray-700 shadow-sm text-primary' : 'text-gray-500']"
              @click="setStatus(opt.value)"
            >{{ opt.label }}</button>
          </div>
          <button class="btn-primary text-sm px-3 py-1.5 flex-shrink-0" @click="openCreate">+ Добавить упражнение</button>
        </div>
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <input
          v-model="search"
          type="text"
          placeholder="Поиск по названию..."
          class="input max-w-xs"
          @input="onSearchInput"
        />
        <select v-model="muscleGroup" class="input max-w-[200px]" @change="load">
          <option value="">Все группы мышц</option>
          <option v-for="mg in muscleGroups" :key="mg" :value="mg">{{ mg }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else-if="!exercises.length" class="card p-12 text-center text-gray-400 text-sm">
      Ничего не найдено
    </div>

    <div v-else class="space-y-3">
      <div v-for="ex in exercises" :key="ex.id" class="card p-4 flex items-start gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <p class="font-semibold text-gray-900 dark:text-white">{{ ex.name }}</p>
            <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusBadge(ex).class]">
              {{ statusBadge(ex).label }}
            </span>
          </div>
          <p class="text-xs text-gray-400 mt-0.5">{{ ex.muscleGroup }} · {{ ex.equipment }}</p>
          <p v-if="ex.secondaryMuscles?.length" class="text-xs text-gray-400 mt-0.5">
            Доп. мышцы: {{ ex.secondaryMuscles.join(', ') }}
          </p>
          <p v-if="ex.description" class="text-sm text-gray-600 dark:text-gray-300 mt-2">{{ ex.description }}</p>
          <p v-if="ex.submittedByName" class="text-xs text-gray-400 mt-2">
            Добавил: {{ ex.submittedByName }}
            <span v-if="ex.submittedByEmail">({{ ex.submittedByEmail }})</span>
          </p>
        </div>
        <div class="flex flex-col gap-2 flex-shrink-0">
          <template v-if="ex.status === 'pending'">
            <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="approve(ex)">
              Одобрить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="reject(ex)">
              Отклонить
            </button>
          </template>
          <template v-else-if="ex.status === 'approved'">
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="revoke(ex)">
              Снять с доступа
            </button>
          </template>
          <template v-else-if="ex.status === 'rejected'">
            <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="approve(ex)">
              Одобрить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
          </template>
          <template v-else-if="ex.status === 'private'">
            <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="approve(ex)">
              Одобрить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="reject(ex)">
              Отклонить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
          </template>
          <template v-else>
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
          </template>
          <button
            class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40"
            :disabled="busyId === ex.id"
            title="Удалить безвозвратно"
            @click="deletePermanently(ex)"
          >
            Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="creating" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="creating = false">
      <div class="card p-5 w-full max-w-md space-y-3">
        <h3 class="font-semibold text-gray-900 dark:text-white">Добавить упражнение</h3>
        <p class="text-xs text-gray-400">Появится сразу у всех пользователей, без модерации.</p>
        <div>
          <label class="label text-xs">Название</label>
          <input v-model="newExercise.name" class="input" placeholder="Например: Болгарские сплит-приседания" />
        </div>
        <div class="flex gap-3">
          <div class="flex-1">
            <label class="label text-xs">Группа мышц</label>
            <select v-model="newExercise.muscleGroup" class="input">
              <option value="">Выберите...</option>
              <option v-for="mg in MUSCLE_GROUPS" :key="mg" :value="mg">{{ mg }}</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="label text-xs">Оборудование</label>
            <select v-model="newExercise.equipment" class="input">
              <option value="">Выберите...</option>
              <option v-for="eq in EQUIPMENT_TYPES" :key="eq" :value="eq">{{ eq }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="label text-xs">Доп. мышцы (через запятую, необязательно)</label>
          <input v-model="newExercise.secondaryMusclesText" class="input" placeholder="Трицепс, Плечи" />
        </div>
        <div>
          <label class="label text-xs">Описание</label>
          <textarea v-model="newExercise.description" rows="2" class="input resize-none" placeholder="Как выполнять упражнение..." />
        </div>
        <p v-if="createError" class="text-sm text-danger">{{ createError }}</p>
        <div class="flex justify-end gap-2 pt-1">
          <button class="btn-outline text-sm px-3 py-1.5" @click="creating = false">Отмена</button>
          <button
            class="btn-primary text-sm px-3 py-1.5"
            :disabled="!newExercise.name.trim() || !newExercise.muscleGroup || !newExercise.equipment || creatingBusy"
            @click="submitCreate"
          >Добавить</button>
        </div>
      </div>
    </div>

    <!-- Rename modal -->
    <div v-if="renaming" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="renaming = null">
      <div class="card p-5 w-full max-w-sm">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Переименовать упражнение</h3>
        <input v-model="renameValue" class="input" @keyup.enter="submitRename" />
        <div class="flex justify-end gap-2 mt-4">
          <button class="btn-outline text-sm px-3 py-1.5" @click="renaming = null">Отмена</button>
          <button class="btn-primary text-sm px-3 py-1.5" :disabled="!renameValue.trim()" @click="submitRename">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService from '@/services/adminService.js'

const statusOptions = [
  { value: 'pending', label: 'На модерации' },
  { value: 'approved', label: 'Одобренные' },
  { value: 'private', label: 'Личные' },
  { value: 'rejected', label: 'Отклонённые' },
  { value: 'all', label: 'Все' },
]

const MUSCLE_GROUPS = [
  'Грудь', 'Спина', 'Плечи', 'Бицепс', 'Трицепс',
  'Пресс', 'Квадрицепс', 'Бицепс бедра', 'Икры', 'Ягодицы', 'Кардио',
]
const EQUIPMENT_TYPES = [
  'Штанга', 'Гантели', 'Тренажёр', 'Собственный вес', 'Гиря', 'Блок', 'Беговая дорожка',
]

// "Личные" isn't a real backend status filter — it means "everything a user
// submitted themselves" (any status), as opposed to built-in exercises.
// Detected via submittedByName, which is only set for created_by != null rows.
const CUSTOM_TAB = 'private'

const exercises = ref([])
const loading = ref(true)
const error = ref('')
const busyId = ref(null)
const status = ref('pending')
const search = ref('')
const muscleGroup = ref('')
const muscleGroups = ref([])

const renaming = ref(null)
const renameValue = ref('')

const creating = ref(false)
const creatingBusy = ref(false)
const createError = ref('')
function blankExercise() {
  return { name: '', muscleGroup: '', equipment: '', secondaryMusclesText: '', description: '' }
}
const newExercise = ref(blankExercise())

let searchDebounce = null

function statusBadge(ex) {
  if (ex.status === 'private') return { label: 'Личное', class: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400' }
  if (ex.status === 'rejected') return { label: 'Отклонено', class: 'bg-danger/15 text-danger' }
  if (ex.status === 'pending') return { label: 'На модерации', class: 'bg-warning/15 text-warning' }
  return { label: 'Публичное', class: 'bg-success/15 text-success' }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const isCustomTab = status.value === CUSTOM_TAB
    const result = await adminService.fetchExercises({
      status: isCustomTab ? 'all' : status.value, search: search.value, muscleGroup: muscleGroup.value,
    })
    exercises.value = isCustomTab ? result.filter(e => e.submittedByName) : result
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadMuscleGroups() {
  try {
    const all = await adminService.fetchExercises({ status: 'all' })
    muscleGroups.value = [...new Set(all.map(e => e.muscleGroup))].sort((a, b) => a.localeCompare(b, 'ru'))
  } catch {
    // non-critical — filter dropdown just stays empty
  }
}

onMounted(() => {
  load()
  loadMuscleGroups()
})

function setStatus(s) {
  status.value = s
  load()
}

function onSearchInput() {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(load, 300)
}

function openCreate() {
  newExercise.value = blankExercise()
  createError.value = ''
  creating.value = true
}

async function submitCreate() {
  createError.value = ''
  creatingBusy.value = true
  try {
    const secondaryMuscles = newExercise.value.secondaryMusclesText
      .split(',').map(s => s.trim()).filter(Boolean)
    const created = await adminService.createExercise({
      name: newExercise.value.name.trim(),
      muscleGroup: newExercise.value.muscleGroup,
      equipment: newExercise.value.equipment,
      secondaryMuscles,
      description: newExercise.value.description.trim(),
    })
    creating.value = false
    if (status.value === 'all' || status.value === 'approved') {
      exercises.value = [...exercises.value, created].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    }
    if (!muscleGroups.value.includes(created.muscleGroup)) {
      muscleGroups.value = [...muscleGroups.value, created.muscleGroup].sort((a, b) => a.localeCompare(b, 'ru'))
    }
  } catch (e) {
    createError.value = e.message
  } finally {
    creatingBusy.value = false
  }
}

async function deletePermanently(ex) {
  if (!confirm(`Удалить упражнение «${ex.name}» безвозвратно? Это действие нельзя отменить.`)) return
  busyId.value = ex.id
  try {
    await adminService.deleteExercisePermanently(ex.id)
    exercises.value = exercises.value.filter(e => e.id !== ex.id)
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

// "Все" and "Личные" both list exercises across every status, so an action
// there updates the row in place; the other tabs are single-status queues
// where an item leaves the list once its status no longer matches.
function keepsVisibleAfterAction() {
  return status.value === 'all' || status.value === CUSTOM_TAB
}

async function approve(ex) {
  busyId.value = ex.id
  try {
    const updated = await adminService.approveExercise(ex.id)
    if (keepsVisibleAfterAction()) {
      const i = exercises.value.findIndex(e => e.id === ex.id)
      if (i !== -1) exercises.value[i] = updated
    } else {
      exercises.value = exercises.value.filter(e => e.id !== ex.id)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function revoke(ex) {
  if (!confirm(`Снять «${ex.name}» с общего доступа? Упражнение перейдёт в отклонённые, его можно будет одобрить заново.`)) return
  busyId.value = ex.id
  try {
    const updated = await adminService.revokeExercise(ex.id)
    if (keepsVisibleAfterAction()) {
      const i = exercises.value.findIndex(e => e.id === ex.id)
      if (i !== -1) exercises.value[i] = updated
    } else {
      exercises.value = exercises.value.filter(e => e.id !== ex.id)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function reject(ex) {
  if (!confirm(`Отклонить упражнение «${ex.name}»?`)) return
  busyId.value = ex.id
  try {
    await adminService.rejectExercise(ex.id)
    if (keepsVisibleAfterAction()) {
      const i = exercises.value.findIndex(e => e.id === ex.id)
      if (i !== -1) exercises.value[i] = { ...exercises.value[i], status: 'rejected' }
    } else {
      exercises.value = exercises.value.filter(e => e.id !== ex.id)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

function openRename(ex) {
  renaming.value = ex
  renameValue.value = ex.name
}

async function submitRename() {
  const ex = renaming.value
  const name = renameValue.value.trim()
  if (!name) return
  busyId.value = ex.id
  try {
    const updated = await adminService.renameExercise(ex.id, name)
    const i = exercises.value.findIndex(e => e.id === ex.id)
    if (i !== -1) exercises.value[i] = updated
    renaming.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}
</script>
