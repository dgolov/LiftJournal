<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Упражнения</h2>
      <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
        <button
          :class="['px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            status === 'pending' ? 'bg-white dark:bg-gray-700 shadow-sm text-primary' : 'text-gray-500']"
          @click="setStatus('pending')"
        >На модерации</button>
        <button
          :class="['px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            status === 'all' ? 'bg-white dark:bg-gray-700 shadow-sm text-primary' : 'text-gray-500']"
          @click="setStatus('all')"
        >Все</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else-if="!exercises.length" class="card p-12 text-center text-gray-400 text-sm">
      {{ status === 'pending' ? 'Нет упражнений, ожидающих одобрения' : 'Нет упражнений' }}
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
          <template v-if="!ex.isApproved && !ex.isPrivate">
            <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="approve(ex)">
              Одобрить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="reject(ex)">
              Отклонить
            </button>
          </template>
          <template v-else-if="ex.isApproved && !ex.isPrivate">
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="revoke(ex)">
              Снять с доступа
            </button>
          </template>
          <template v-else>
            <button class="btn-outline text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="openRename(ex)">
              Переименовать
            </button>
          </template>
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

const exercises = ref([])
const loading = ref(true)
const error = ref('')
const busyId = ref(null)
const status = ref('pending')

const renaming = ref(null)
const renameValue = ref('')

function statusBadge(ex) {
  if (ex.isPrivate) return { label: 'Личное', class: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400' }
  if (!ex.isApproved) return { label: 'На модерации', class: 'bg-warning/15 text-warning' }
  return { label: 'Публичное', class: 'bg-success/15 text-success' }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    exercises.value = await adminService.fetchExercises(status.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

function setStatus(s) {
  status.value = s
  load()
}

async function approve(ex) {
  busyId.value = ex.id
  try {
    await adminService.approveExercise(ex.id)
    exercises.value = exercises.value.filter(e => e.id !== ex.id)
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function revoke(ex) {
  if (!confirm(`Снять «${ex.name}» с общего доступа? Упражнение останется видно только автору.`)) return
  busyId.value = ex.id
  try {
    const updated = await adminService.revokeExercise(ex.id)
    if (status.value === 'pending') {
      exercises.value = exercises.value.filter(e => e.id !== ex.id)
    } else {
      const i = exercises.value.findIndex(e => e.id === ex.id)
      if (i !== -1) exercises.value[i] = updated
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function reject(ex) {
  if (!confirm(`Отклонить и удалить упражнение «${ex.name}»?`)) return
  busyId.value = ex.id
  try {
    await adminService.rejectExercise(ex.id)
    exercises.value = exercises.value.filter(e => e.id !== ex.id)
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
