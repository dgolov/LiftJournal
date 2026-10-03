<template>
  <BaseModal
    :model-value="modelValue"
    :title="targetId ? 'Назначить цикл' : 'Запланировать цикл'"
    max-width="md"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="space-y-5">
      <!-- Whose plan: a coach can lay a cycle out for any athlete they may plan for -->
      <div v-if="allowAthletes && !athleteId && plannableAthletes.length">
        <label class="label">Для кого</label>
        <select v-model="targetId" class="input">
          <option :value="null">Себе</option>
          <option v-for="a in plannableAthletes" :key="a.id" :value="a.id">{{ a.name }} — подопечный</option>
        </select>
      </div>
      <p v-else-if="targetId" class="text-sm text-steel-700 dark:text-steel-300 -mt-1">
        Тренировки появятся в плане: <strong class="text-ink dark:text-white">{{ athleteName }}</strong>
      </p>
      <!-- Which cycle (coach flow starts without one) -->
      <div v-if="!cycle">
        <label class="label">Цикл</label>
        <select v-model="pickedCycleId" class="input">
          <option :value="null" disabled>Выберите цикл</option>
          <option v-for="c in cycleOptions" :key="c.id" :value="c.id">
            {{ c.title }} · {{ c.workout_count }} {{ plural(c.workout_count, 'тренировка', 'тренировки', 'тренировок') }}
          </option>
        </select>
        <p class="text-xs text-steel-700 dark:text-steel-300 mt-1.5">
          Ваши циклы и публичные. Новый цикл можно собрать в разделе
          <RouterLink to="/cycles/new" class="text-primary hover:underline">«Циклы»</RouterLink>.
        </p>
      </div>

      <template v-if="activeCycle">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="label">Дата начала</label>
            <input v-model="startDate" type="date" :min="todayStr" class="input" />
          </div>
          <div>
            <label class="label">Дни тренировок</label>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="d in weekDayOptions" :key="d.value" type="button"
                :class="['w-9 h-9 rounded-lg text-sm font-medium border transition-colors',
                  selectedDays.includes(d.value) ? 'bg-primary text-white border-primary' : 'border-steel-100 dark:border-steel-700 text-steel-700 dark:text-steel-300 hover:border-primary']"
                :aria-pressed="selectedDays.includes(d.value)"
                @click="toggleDay(d.value)"
              >{{ d.label }}</button>
            </div>
            <p v-if="!selectedDays.length" class="text-xs text-danger mt-1.5">Выберите хотя бы один день</p>
          </div>
        </div>

        <!-- 1RM each percentage is taken from -->
        <div>
          <label class="label">1ПМ для расчёта весов</label>
          <div class="rounded-xl border border-steel-100 dark:border-steel-700 divide-y divide-steel-100 dark:divide-steel-700">
            <div v-for="ex in loadedExercises" :key="ex.name" class="flex items-center gap-3 px-3 py-2">
              <div class="flex-1 min-w-0">
                <p class="text-sm text-ink dark:text-white truncate">
                  {{ ex.name }}
                  <Star v-if="ex.main" class="inline w-3 h-3 text-primary fill-current -mt-0.5" aria-label="основное" />
                </p>
                <p class="text-xs" :class="maxSource[ex.name] === 'none' ? 'text-danger' : 'text-steel-700 dark:text-steel-300'">
                  {{ sourceLabel(ex.name) }}
                </p>
              </div>
              <div class="flex items-center gap-1.5 flex-shrink-0">
                <input
                  v-model.number="maxes[ex.name]"
                  type="number" min="0" step="2.5" inputmode="decimal"
                  class="input w-24 text-right tabular-nums"
                  :aria-label="`1ПМ, ${ex.name}`"
                  @input="maxSource[ex.name] = 'manual'"
                />
                <span class="text-sm text-steel-700 dark:text-steel-300">кг</span>
              </div>
            </div>
          </div>
          <p v-if="targetId && athleteData?.maxesHidden" class="text-xs text-steel-700 dark:text-steel-300 mt-1.5">
            Подопечный скрыл свои 1ПМ — подставлены расчётные по тренировкам, поправьте при необходимости.
          </p>
        </div>

        <div v-if="preview.length">
          <label class="label">Расписание — {{ preview.length }} {{ workoutWord }}</label>
          <p class="text-xs text-steel-700 dark:text-steel-300 -mt-0.5 mb-1.5">Дату любой тренировки можно перенести.</p>
          <div class="max-h-64 overflow-y-auto rounded-xl border border-steel-100 dark:border-steel-700 divide-y divide-steel-100 dark:divide-steel-700">
            <div
              v-for="(p, i) in preview" :key="p.workout.id"
              :class="['flex items-center gap-2 text-sm px-2.5 py-1.5', p.outOfOrder ? 'bg-hazard/10' : '']"
            >
              <span class="text-xs text-steel-300 w-6 flex-shrink-0 tabular-nums">Т{{ i + 1 }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-ink dark:text-white truncate">{{ p.label }}</p>
                <p v-if="p.moved" class="text-xs text-primary">перенесено</p>
              </div>
              <span class="text-xs text-steel-700 dark:text-steel-300 w-6 capitalize flex-shrink-0">{{ weekday(p.date) }}</span>
              <input
                type="date"
                :value="p.date"
                class="input w-36 min-h-0 py-1 px-2 text-sm flex-shrink-0"
                :aria-label="`Дата: ${p.label}`"
                @change="moveWorkout(p.workout.id, $event.target.value)"
              />
              <button
                type="button"
                :class="['w-7 h-7 flex items-center justify-center rounded-lg flex-shrink-0 transition-colors',
                  p.moved ? 'text-steel-700 hover:text-primary hover:bg-primary/10 dark:text-steel-300' : 'invisible']"
                title="Вернуть дату по расписанию"
                aria-label="Вернуть дату по расписанию"
                @click="moveWorkout(p.workout.id, null)"
              ><RotateCcw class="w-3.5 h-3.5" /></button>
            </div>
          </div>
          <p v-if="preview.some(p => p.outOfOrder)" class="text-xs text-hazard mt-1.5">
            Подсвеченная тренировка стоит не позже предыдущей — проверьте, что порядок цикла не нарушен.
          </p>
        </div>
      </template>

      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
    </div>
    <template #footer>
      <BaseButton variant="ghost" @click="close">Отмена</BaseButton>
      <BaseButton :disabled="!preview.length || missingMaxes" :loading="saving" @click="submit">
        Запланировать {{ preview.length || '' }} {{ preview.length ? workoutWord : '' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Star, RotateCcw } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { apiErrorMessage } from '@/services/workoutService.js'
import { toDateStr } from '@/components/calendar/calendarStyles.js'
import { sessionE1RM } from '@/utils/strength.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  cycle: { type: Object, default: null },
  // Coach mode: lay the cycle out in this athlete's plan, from their 1RMs.
  athleteId: { type: Number, default: null },
  // Opened from a cycle page by a coach: offer "Себе" or any of their athletes.
  allowAthletes: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'scheduled'])

const store = useStore()
const router = useRouter()

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

// ── Cycle choice (coach flow) ─────────────────────────────────────────────
// Whose plan the cycle goes into: null = the current user.
const targetId = ref(props.athleteId)
watch(() => props.athleteId, id => { targetId.value = id })
const plannableAthletes = computed(() => store.state.coach.athletes.filter(a => a.canEditPlan))
const athleteData = computed(() => targetId.value ? store.getters['coach/athleteById'](targetId.value) : null)
watch(targetId, id => {
  if (id) store.dispatch('coach/loadAthlete', { id }).catch(e => { error.value = apiErrorMessage(e) })
}, { immediate: true })
const athleteName = computed(() => athleteData.value?.summary?.name || 'подопечного')
const cycleOptions = computed(() => store.state.cycles.cycles)
const pickedCycleId = ref(null)
const pickedCycle = ref(null)
const activeCycle = computed(() => props.cycle || pickedCycle.value)

watch(() => props.modelValue, open => {
  if (open && !props.cycle && !cycleOptions.value.length) store.dispatch('cycles/fetchCycles').catch(() => {})
  if (open && props.allowAthletes && !store.state.coach.athletes.length) store.dispatch('coach/fetchAthletes').catch(() => {})
}, { immediate: true })

watch(pickedCycleId, async id => {
  pickedCycle.value = null
  if (!id) return
  try {
    pickedCycle.value = await store.dispatch('cycles/fetchCycle', id)
  } catch (e) {
    error.value = apiErrorMessage(e)
  }
})

// ── 1RMs the percentages are taken from ───────────────────────────────────
const mainNames = computed(() => new Set((activeCycle.value?.main_exercises || []).map(m => m.exerciseName)))
const cycleExercises = computed(() => {
  const seen = new Map()
  activeCycle.value?.workouts.forEach(w => w.exercises.forEach(e => {
    if (!seen.has(e.exercise_name)) seen.set(e.exercise_name, { name: e.exercise_name, id: e.exercise_id, main: mainNames.value.has(e.exercise_name), loaded: false })
    // Sets at 0% are reps-only (pull-ups, core work) — no 1RM needed for those.
    if (e.sets.some(st => st.percent_1rm > 0)) seen.get(e.exercise_name).loaded = true
  }))
  return [...seen.values()].sort((a, b) => Number(b.main) - Number(a.main))
})

const sourceMaxes = computed(() => (targetId.value ? athleteData.value?.maxes : store.state.user.maxes) || [])
const sourceWorkouts = computed(() => (targetId.value ? athleteData.value?.workouts : store.state.workouts.workouts) || [])

function estimatedMax(ex) {
  const sets = []
  sourceWorkouts.value.forEach(w => w.exercises.forEach(e => {
    if ((ex.id && e.exerciseId === ex.id) || e.exerciseName === ex.name) sets.push(...e.sets.filter(s => !s.failed))
  }))
  const e1rm = sessionE1RM(sets)
  return e1rm ? Math.round(e1rm / 2.5) * 2.5 : null
}

const maxes = reactive({})
const maxSource = reactive({})   // profile | estimated | manual | none
// Re-derived when the cycle, the target, or the target's 1RMs arrive — not on
// every plan created during submit (that replaces athleteData but keeps its
// maxes), which would wipe 1RMs typed in by hand mid-way.
watch([cycleExercises, targetId, () => athleteData.value?.maxes, () => !!athleteData.value], ([list]) => {
  list.forEach(ex => {
    const declared = sourceMaxes.value.find(m => m.exercise_name === ex.name)?.weight_kg
    const estimated = declared ? null : estimatedMax(ex)
    maxes[ex.name] = declared ?? estimated ?? null
    maxSource[ex.name] = declared ? 'profile' : estimated ? 'estimated' : 'none'
  })
}, { immediate: true })

function sourceLabel(name) {
  return {
    profile: 'из профиля',
    estimated: 'расчётный по тренировкам',
    manual: 'введено вручную',
    none: 'нет данных — введите 1ПМ',
  }[maxSource[name]]
}
const loadedExercises = computed(() => cycleExercises.value.filter(ex => ex.loaded))
const missingMaxes = computed(() => loadedExercises.value.some(ex => !(maxes[ex.name] > 0)))

// Same rounding convention as starting a cycle workout directly (workouts/startWorkoutFromCycle)
function calcWeight(maxKg, percent) {
  return Math.round(maxKg * percent / 100 / 2.5) * 2.5
}

// ── Schedule preview ─────────────────────────────────────────────────────
// Walk forward day by day from the start date, assigning each selected
// weekday to the next unscheduled cycle workout in order.
// Per-workout date changes on top of the weekday pattern ("T6 moves to
// Saturday"); a new start date or weekday set lays the cycle out afresh.
const dateOverrides = reactive({})
function moveWorkout(workoutId, date) {
  if (date) dateOverrides[workoutId] = date
  else delete dateOverrides[workoutId]
}
watch([startDate, () => [...selectedDays.value], activeCycle], () => {
  Object.keys(dateOverrides).forEach(k => delete dateOverrides[k])
})

const preview = computed(() => {
  if (!activeCycle.value || !selectedDays.value.length) return []
  const workouts = activeCycle.value.workouts
  const result = []
  const cur = new Date(startDate.value + 'T00:00:00')
  let guard = 0
  while (result.length < workouts.length && guard < 2000) {
    if (selectedDays.value.includes(cur.getDay())) {
      const workout = workouts[result.length]
      const moved = dateOverrides[workout.id]
      result.push({
        workout,
        date: moved || toDateStr(cur),
        moved: !!moved,
        label: workout.title?.trim() || `Тренировка ${workout.workout_number}`,
      })
    }
    cur.setDate(cur.getDate() + 1)
    guard++
  }
  // A moved workout landing on or before the previous one breaks the cycle's order.
  result.forEach((p, i) => { p.outOfOrder = i > 0 && p.date <= result[i - 1].date })
  return result
})

function plural(n, one, few, many) {
  const m10 = n % 10, m100 = n % 100
  if (m10 === 1 && m100 !== 11) return one
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few
  return many
}
const workoutWord = computed(() => plural(preview.value.length, 'тренировку', 'тренировки', 'тренировок'))

function weekday(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'short' })
}


function close() {
  emit('update:modelValue', false)
}

async function submit() {
  if (!preview.value.length || missingMaxes.value) return
  saving.value = true
  error.value = ''
  const cycle = activeCycle.value
  // One id for this layout of the cycle — its progress charts group by it.
  const scheduleId = crypto.randomUUID()
  try {
    for (const item of preview.value) {
      const exercises = item.workout.exercises.map(ex => ({
        exerciseId: ex.exercise_id
          ?? store.state.exercises.library.find(e => e.name === ex.exercise_name)?.id
          ?? `cycle-${ex.id}`,
        exerciseName: ex.exercise_name,
        sets: ex.sets.map(s => ({ weight: s.percent_1rm > 0 ? calcWeight(maxes[ex.exercise_name], s.percent_1rm) : 0, reps: s.reps })),
      }))
      const payload = {
        title: `${item.label} — ${cycle.title}`,
        type: 'Силовая',
        scheduledDate: item.date,
        notes: item.workout.notes || '',
        exercises,
        cycleId: cycle.id,
        cycleScheduleId: scheduleId,
      }
      if (targetId.value) {
        await store.dispatch('coach/createPlan', { athleteId: targetId.value, payload })
      } else {
        await store.dispatch('planned/createPlannedWorkout', payload)
      }
    }
    store.dispatch('ui/showToast', { message: `Запланировано ${preview.value.length} ${workoutWord.value}`, type: 'success' })
    emit('scheduled', scheduleId)
    close()
    if (props.athleteId) return
    router.push(targetId.value ? `/coach/athletes/${targetId.value}/cycles/${scheduleId}` : '/planning')
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    saving.value = false
  }
}
</script>
