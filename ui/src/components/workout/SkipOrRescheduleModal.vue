<template>
  <BaseModal :model-value="modelValue" title="Перенести или пропустить?" max-width="sm" @update:model-value="$emit('update:modelValue', $event)">
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">«{{ plan?.title }}»</p>
    <p class="text-xs text-gray-400 mb-4">Запланировано на {{ plan ? formatShortDate(plan.scheduledDate) : '' }}</p>

    <div class="mb-4">
      <label class="label text-xs">Перенести на другой день</label>
      <input type="date" v-model="rescheduleDate" :min="today" class="input" />
      <p class="text-xs text-gray-400 mt-1">Тренировка останется в расписании на новую дату</p>
    </div>

    <template v-if="plan?.recurrenceGroupId">
      <p class="label text-xs mb-2">При пропуске без переноса:</p>
      <div class="space-y-2">
        <button
          :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
            skipScope === 'one' ? 'border-primary bg-primary/5' : 'border-gray-200 dark:border-gray-700']"
          @click="skipScope = 'one'"
        >
          <p class="font-medium text-gray-900 dark:text-white">Только эту тренировку</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ plan?.scheduledDate }}</p>
        </button>
        <button
          :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
            skipScope === 'all' ? 'border-orange-400 bg-orange-50 dark:bg-orange-900/10' : 'border-gray-200 dark:border-gray-700']"
          @click="skipScope = 'all'"
        >
          <p class="font-medium text-gray-900 dark:text-white">Эту и все следующие</p>
          <p class="text-xs text-gray-400 mt-0.5">Пропустит все запланированные повторения</p>
        </button>
      </div>
    </template>

    <template #footer>
      <BaseButton variant="ghost" @click="close">Отмена</BaseButton>
      <BaseButton variant="ghost" @click="doSkip">Пропустить без переноса</BaseButton>
      <BaseButton :disabled="!rescheduleDate" @click="doReschedule">Перенести</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useStore } from 'vuex'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  plan: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])

const store = useStore()
const today = new Date().toISOString().split('T')[0]

const skipScope = ref('one')
const rescheduleDate = ref('')

// Re-derive defaults whenever a new plan is handed in (modal opens)
watch(() => props.plan, (plan) => {
  if (!plan) return
  skipScope.value = 'one'
  // Default to a week later — a sensible "same day next week" nudge the
  // user can freely change, never earlier than today.
  const weekLater = new Date(plan.scheduledDate + 'T00:00:00')
  weekLater.setDate(weekLater.getDate() + 7)
  const weekLaterStr = weekLater.toISOString().slice(0, 10)
  rescheduleDate.value = weekLaterStr < today ? today : weekLaterStr
}, { immediate: true })

function formatShortDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

function close() {
  emit('update:modelValue', false)
}

async function doReschedule() {
  if (!rescheduleDate.value || !props.plan) return
  try {
    await store.dispatch('planned/reschedulePlannedWorkout', { id: props.plan.id, scheduledDate: rescheduleDate.value })
    store.dispatch('ui/showToast', { message: 'Тренировка перенесена', type: 'success' })
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    close()
  }
}

async function doSkip() {
  if (!props.plan) return
  try {
    if (skipScope.value === 'all' && props.plan.recurrenceGroupId) {
      await store.dispatch('planned/skipUpcomingRecurring', props.plan)
      store.dispatch('ui/showToast', { message: 'Все следующие пропущены', type: 'info' })
    } else {
      await store.dispatch('planned/skipPlannedWorkout', props.plan.id)
      store.dispatch('ui/showToast', { message: 'Тренировка пропущена', type: 'info' })
    }
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    close()
  }
}
</script>
