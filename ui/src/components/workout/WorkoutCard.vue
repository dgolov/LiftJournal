<template>
  <div
    class="card p-4 hover:shadow-md transition-shadow cursor-pointer"
    @click="$router.push(`/workouts/${workout.id}`)"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
          <span class="text-xs text-gray-400">{{ formattedDate }}</span>
        </div>
        <h3 class="font-semibold text-gray-900 truncate">{{ workout.title }}</h3>
        <p class="text-xs text-gray-500 mt-1">
          {{ workout.exercises.length }} упр. · {{ totalSets }} подх. · {{ formatDuration(workout.durationMinutes) }}
        </p>
        <p class="text-xs text-gray-400 mt-0.5">
          Тоннаж: {{ formatVolume(totalVolume) }} кг
        </p>
      </div>
      <button
        class="p-1.5 text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
        @click.stop="confirmDelete"
        title="Удалить"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
    </div>
  </div>

  <BaseModal v-model="showConfirm" title="Удалить тренировку?" max-width="sm">
    <p class="text-sm text-gray-600">Это действие нельзя отменить.</p>
    <template #footer>
      <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
      <BaseButton variant="danger" @click="deleteWorkout">Удалить</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  workout: { type: Object, required: true }
})

const store = useStore()
const showConfirm = ref(false)

const typeColorMap = {
  'Силовая': 'indigo',
  'Кардио': 'green',
  'Растяжка': 'purple',
  'HIIT': 'orange',
  'Другое': 'gray'
}
const typeColor = computed(() => typeColorMap[props.workout.type] || 'gray')

const formattedDate = computed(() => {
  const d = new Date(props.workout.date + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
})

const totalSets = computed(() =>
  props.workout.exercises.reduce((n, ex) => n + ex.sets.length, 0)
)

const totalVolume = computed(() =>
  props.workout.exercises.reduce((total, ex) =>
    total + ex.sets.reduce((s, set) => s + set.weight * set.reps, 0), 0)
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

function confirmDelete() { showConfirm.value = true }

async function deleteWorkout() {
  await store.dispatch('workouts/deleteWorkout', props.workout.id)
  store.dispatch('ui/showToast', { message: 'Тренировка удалена', type: 'success' })
  showConfirm.value = false
}
</script>
