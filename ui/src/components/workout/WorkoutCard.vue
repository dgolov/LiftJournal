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
        <h3 class="font-semibold text-gray-900 dark:text-white truncate">{{ workout.title }}</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ workout.exercises.length }} упр. · {{ totalSets }} подх. · {{ formatDuration(workout.durationMinutes) }}
        </p>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
          Тоннаж: {{ formatVolume(totalVolume) }} кг
        </p>
      </div>
      <button
        class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
        @click.stop="confirmDelete"
        title="Удалить"
      >
        <Trash2 class="w-4 h-4" />
      </button>
    </div>
  </div>

  <BaseModal v-model="showConfirm" title="Удалить тренировку?" max-width="sm">
    <p class="text-sm text-gray-600 dark:text-gray-400">Это действие нельзя отменить.</p>
    <template #footer>
      <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
      <BaseButton variant="danger" @click="deleteWorkout">Удалить</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { Trash2 } from 'lucide-vue-next'
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
