<template>
  <BaseModal :model-value="modelValue" title="Запланировать цикл" max-width="md" @update:model-value="$emit('update:modelValue', $event)">
    <div class="space-y-4">
      <div>
        <label class="label">Дата начала</label>
        <input type="date" v-model="startDate" :min="todayStr" class="input" />
      </div>

      <div>
        <label class="label">Дни недели для тренировок</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="d in weekDayOptions" :key="d.value" type="button"
            :class="['w-10 h-10 rounded-lg text-sm font-medium border transition-colors',
              selectedDays.includes(d.value) ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary']"
            @click="toggleDay(d.value)"
          >{{ d.label }}</button>
        </div>
        <p v-if="!selectedDays.length" class="text-xs text-danger mt-1.5">Выберите хотя бы один день</p>
      </div>

      <div v-if="preview.length">
        <label class="label">Расписание ({{ preview.length }} {{ workoutWord }})</label>
        <div class="max-h-52 overflow-y-auto space-y-0.5 border border-gray-100 dark:border-gray-800 rounded-xl p-2">
          <div v-for="p in preview" :key="p.workout.id" class="flex items-center justify-between text-sm px-2 py-1.5">
            <span class="text-gray-700 dark:text-gray-300">{{ p.label }}</span>
            <span class="text-gray-400 capitalize">{{ formatDate(p.date) }}</span>
          </div>
        </div>
      </div>

      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
    </div>
    <template #footer>
      <BaseButton variant="ghost" @click="close">Отмена</BaseButton>
      <BaseButton :disabled="!preview.length" :loading="saving" @click="submit">
        Запланировать {{ preview.length }} {{ workoutWord }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  cycle: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])

const store = useStore()
const router = useRouter()

function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
const todayStr = toDateStr(new Date())

const startDate = ref(todayStr)
const weekDayOptions = [
  { value: 1, label: 'Пн' }, { value: 2, label: 'Вт' }, { value: 3, label: 'Ср' },
  { value: 4, label: 'Чт' }, { value: 5, label: 'Пт' }, { value: 6, label: 'Сб' }, { value: 0, label: 'Вс' },
]
// Mon/Wed/Fri is a sensible default for a 3x/week strength cycle
const selectedDays = ref([1, 3, 5])
const saving = ref(false)
const error = ref('')

function toggleDay(v) {
  const i = selectedDays.value.indexOf(v)
  if (i === -1) selectedDays.value.push(v)
  else selectedDays.value.splice(i, 1)
}

const userMaxes = computed(() => store.state.user.maxes)
function getMax(exerciseName) {
  return userMaxes.value.find(m => m.exercise_name === exerciseName)?.weight_kg ?? null
}

// Same rounding convention as starting a cycle workout directly (workouts/startWorkoutFromCycle)
function calcWeight(maxKg, percent) {
  return Math.round(maxKg * percent / 100 / 2.5) * 2.5
}

// Walk forward day by day from the start date, assigning each selected
// weekday to the next unscheduled cycle workout in order.
const preview = computed(() => {
  if (!props.cycle || !selectedDays.value.length) return []
  const workouts = props.cycle.workouts
  const result = []
  const cur = new Date(startDate.value + 'T00:00:00')
  let guard = 0
  while (result.length < workouts.length && guard < 2000) {
    if (selectedDays.value.includes(cur.getDay())) {
      const workout = workouts[result.length]
      result.push({
        workout,
        date: toDateStr(cur),
        label: `Тренировка ${workout.workout_number}`,
      })
    }
    cur.setDate(cur.getDate() + 1)
    guard++
  }
  return result
})

const workoutWord = computed(() => {
  const n = preview.value.length % 10
  const n10 = preview.value.length % 100
  if (n10 >= 11 && n10 <= 14) return 'тренировок'
  if (n === 1) return 'тренировку'
  if (n >= 2 && n <= 4) return 'тренировки'
  return 'тренировок'
})

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', weekday: 'short' })
}

function close() {
  emit('update:modelValue', false)
}

async function submit() {
  if (!preview.value.length) return
  saving.value = true
  error.value = ''
  try {
    for (const item of preview.value) {
      const exercises = item.workout.exercises.map(ex => {
        const maxKg = getMax(ex.exercise_name)
        const exerciseId = ex.exercise_id
          ?? store.state.exercises.library.find(e => e.name === ex.exercise_name)?.id
          ?? `cycle-${ex.id}`
        return {
          exerciseId,
          exerciseName: ex.exercise_name,
          sets: ex.sets.map(s => ({
            weight: maxKg ? calcWeight(maxKg, s.percent_1rm) : 0,
            reps: s.reps,
          })),
        }
      })
      await store.dispatch('planned/createPlannedWorkout', {
        title: `${item.label} — ${props.cycle.title}`,
        type: 'Силовая',
        scheduledDate: item.date,
        notes: '',
        exercises,
      })
    }
    store.dispatch('ui/showToast', { message: `Запланировано ${preview.value.length} ${workoutWord.value}`, type: 'success' })
    close()
    router.push('/planning')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
