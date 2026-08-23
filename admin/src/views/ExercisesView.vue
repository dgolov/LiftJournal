<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Упражнения на модерации</h2>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else-if="!exercises.length" class="card p-12 text-center text-gray-400 text-sm">
      Нет упражнений, ожидающих одобрения
    </div>

    <div v-else class="space-y-3">
      <div v-for="ex in exercises" :key="ex.id" class="card p-4 flex items-start gap-4">
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-gray-900 dark:text-white">{{ ex.name }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ ex.muscleGroup }} · {{ ex.equipment }}</p>
          <p v-if="ex.secondaryMuscles?.length" class="text-xs text-gray-400 mt-0.5">
            Доп. мышцы: {{ ex.secondaryMuscles.join(', ') }}
          </p>
          <p v-if="ex.description" class="text-sm text-gray-600 dark:text-gray-300 mt-2">{{ ex.description }}</p>
          <p class="text-xs text-gray-400 mt-2">
            Добавил: {{ ex.submittedByName || 'неизвестно' }}
            <span v-if="ex.submittedByEmail">({{ ex.submittedByEmail }})</span>
          </p>
        </div>
        <div class="flex flex-col gap-2 flex-shrink-0">
          <button class="btn-primary text-xs px-3 py-1.5" :disabled="busyId === ex.id" @click="approve(ex)">
            Одобрить
          </button>
          <button class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40" :disabled="busyId === ex.id" @click="reject(ex)">
            Отклонить
          </button>
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

async function load() {
  loading.value = true
  try {
    exercises.value = await adminService.fetchPendingExercises()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

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
</script>
