<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Циклы</h2>
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

    <div v-else-if="!cycles.length" class="card p-12 text-center text-gray-400 text-sm">
      {{ status === 'pending' ? 'Нет циклов, ожидающих одобрения' : 'Нет циклов' }}
    </div>

    <div v-else class="space-y-3">
      <div v-for="c in cycles" :key="c.id" class="card p-4 flex items-start gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <p class="font-semibold text-gray-900 dark:text-white">{{ c.title }}</p>
            <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusBadge(c).class]">
              {{ statusBadge(c).label }}
            </span>
          </div>
          <p class="text-xs text-gray-400 mt-0.5">{{ c.authorName || 'Без автора' }} · {{ c.workoutCount }} тренировок</p>
          <p v-if="c.description" class="text-sm text-gray-600 dark:text-gray-300 mt-2">{{ c.description }}</p>
          <p v-if="c.submittedByName" class="text-xs text-gray-400 mt-2">
            Добавил: {{ c.submittedByName }}
            <span v-if="c.submittedByEmail">({{ c.submittedByEmail }})</span>
          </p>
        </div>
        <div class="flex flex-col gap-2 flex-shrink-0">
          <template v-if="c.isPublic && !c.isApproved">
            <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === c.id" @click="approve(c)">
              Одобрить
            </button>
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === c.id" @click="reject(c)">
              Отклонить
            </button>
          </template>
          <template v-else-if="c.isPublic && c.isApproved">
            <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === c.id" @click="revoke(c)">
              Отозвать доступ
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService from '@/services/adminService.js'

const cycles = ref([])
const loading = ref(true)
const error = ref('')
const busyId = ref(null)
const status = ref('pending')

function statusBadge(c) {
  if (!c.isPublic) return { label: 'Личный', class: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400' }
  if (!c.isApproved) return { label: 'На модерации', class: 'bg-warning/15 text-warning' }
  return { label: 'Публичный', class: 'bg-success/15 text-success' }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    cycles.value = await adminService.fetchCycles(status.value)
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

async function approve(c) {
  busyId.value = c.id
  try {
    await adminService.approveCycle(c.id)
    if (status.value === 'pending') {
      cycles.value = cycles.value.filter(x => x.id !== c.id)
    } else {
      const i = cycles.value.findIndex(x => x.id === c.id)
      if (i !== -1) cycles.value[i] = { ...cycles.value[i], isApproved: true }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function revoke(c) {
  if (!confirm(`Отозвать публичный доступ к циклу «${c.title}»? Он останется виден только автору.`)) return
  busyId.value = c.id
  try {
    await adminService.revokeCycle(c.id)
    if (status.value === 'pending') {
      cycles.value = cycles.value.filter(x => x.id !== c.id)
    } else {
      const i = cycles.value.findIndex(x => x.id === c.id)
      if (i !== -1) cycles.value[i] = { ...cycles.value[i], isPublic: false, isApproved: false }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}

async function reject(c) {
  if (!confirm(`Отклонить и удалить цикл «${c.title}»?`)) return
  busyId.value = c.id
  try {
    await adminService.rejectCycle(c.id)
    cycles.value = cycles.value.filter(x => x.id !== c.id)
  } catch (e) {
    error.value = e.message
  } finally {
    busyId.value = null
  }
}
</script>
