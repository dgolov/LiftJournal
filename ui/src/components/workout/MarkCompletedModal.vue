<template>
  <BaseModal :model-value="modelValue" title="Всё-таки выполнили?" max-width="sm" @update:model-value="$emit('update:modelValue', $event)">
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">«{{ plan?.title }}»</p>
    <p class="text-xs text-gray-400 mb-4">Была запланирована на {{ plan ? formatShortDate(plan.scheduledDate) : '' }}</p>

    <div class="mb-4">
      <label class="label text-xs">Дата, когда фактически выполнили</label>
      <input type="date" v-model="date" :max="today" class="input" />
      <p class="text-xs text-gray-400 mt-1">Используется, если создавать запись тренировки</p>
    </div>

    <p class="text-sm text-gray-600 dark:text-gray-400">
      Можно создать запись тренировки на эту дату, либо просто отметить план выполненным — если вы уже записали эту тренировку отдельно.
    </p>
    <template #footer>
      <BaseButton variant="ghost" @click="close">Отмена</BaseButton>
      <BaseButton variant="outline" :loading="markingOnly" @click="markOnly">Просто отметить</BaseButton>
      <BaseButton @click="createWorkout">Создать тренировку</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  plan: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])

const store = useStore()
const router = useRouter()
const markingOnly = ref(false)
const today = new Date().toISOString().split('T')[0]
const date = ref(today)

// Default to the day it was planned for — the most likely actual date —
// re-derived whenever a new plan is handed in (modal opens).
watch(() => props.plan, (plan) => {
  if (!plan) return
  date.value = plan.scheduledDate > today ? today : plan.scheduledDate
}, { immediate: true })

function formatShortDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

function close() {
  emit('update:modelValue', false)
}

async function markOnly() {
  if (!props.plan) return
  markingOnly.value = true
  try {
    await store.dispatch('planned/updatePlannedWorkout', { id: props.plan.id, status: 'completed' })
    store.dispatch('ui/showToast', { message: 'Отмечено как выполненное', type: 'success' })
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    markingOnly.value = false
    close()
  }
}

async function createWorkout() {
  if (!props.plan) return
  await store.dispatch('workouts/startWorkoutFromPlan', { plan: props.plan, date: date.value })
  close()
  router.push('/workouts/new')
}
</script>
