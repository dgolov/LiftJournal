<template>
  <div class="max-w-3xl">
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-steel-100 dark:hover:bg-steel-900 text-steel-700 dark:text-steel-300 mt-1 transition-colors" @click="$router.back()">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <div class="min-w-0">
        <RouterLink v-if="athleteId" :to="`/coach/athletes/${athleteId}`" class="text-sm text-primary hover:underline">
          {{ athleteData?.summary?.name || 'Подопечный' }}
        </RouterLink>
        <h2 class="text-2xl font-bold text-ink dark:text-white">{{ schedule?.title || 'Цикл' }}</h2>
        <p v-if="schedule" class="text-sm text-steel-700 dark:text-steel-300 mt-0.5">
          {{ formatDate(schedule.from) }} – {{ formatDate(schedule.to) }}
          <template v-if="schedule.createdByName"> · от {{ schedule.createdByName }}</template>
        </p>
      </div>
    </div>

    <div v-if="loading && !schedule" class="text-center py-16 text-steel-300">Загрузка…</div>
    <div v-else-if="!schedule" class="card p-6 text-center text-steel-700 dark:text-steel-300">
      Цикл не найден — возможно, его тренировки удалили из плана.
    </div>

    <template v-else>
      <!-- Progress through the cycle -->
      <div class="card p-4 mb-4">
        <div class="flex items-baseline justify-between gap-3 mb-2">
          <p class="text-sm text-steel-700 dark:text-steel-300">
            Выполнено <strong class="text-ink dark:text-white text-lg tabular-nums">{{ schedule.completed }}</strong> из {{ schedule.total }}
          </p>
          <p class="text-xs text-steel-700 dark:text-steel-300 tabular-nums">
            <template v-if="schedule.skipped">пропущено {{ schedule.skipped }} · </template>осталось {{ remaining }}
          </p>
        </div>
        <!-- One segment per cycle workout, in order -->
        <div class="flex gap-0.5" role="img" :aria-label="`Выполнено ${schedule.completed} из ${schedule.total}`">
          <RouterLink
            v-for="p in schedule.plans" :key="p.id"
            :to="planLink(p)"
            :title="`${p.title} — ${formatDate(p.scheduledDate)}: ${statusLabel[p.status]}`"
            :class="['h-2 flex-1 rounded-full transition-opacity hover:opacity-70', segmentClass(p.status)]"
          />
        </div>
      </div>

      <!-- Charts per main lift -->
      <div class="flex items-center justify-between gap-3 flex-wrap mb-3">
        <h3 class="font-semibold text-ink dark:text-white">
          {{ usingMainExercises ? 'Основные упражнения' : 'Упражнения цикла' }}
        </h3>
        <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5">
          <button
            v-for="m in metrics" :key="m.value"
            :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              metric === m.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white']"
            @click="metric = m.value"
          >{{ m.label }}</button>
        </div>
      </div>
      <p v-if="!usingMainExercises" class="text-xs text-steel-700 dark:text-steel-300 mb-3">
        В цикле не отмечены основные упражнения, поэтому показаны все. Отметить их можно в редакторе цикла.
      </p>

      <div class="space-y-4">
        <div v-for="ex in exerciseSeries" :key="ex.name" class="card p-4">
          <div class="flex items-start justify-between gap-3 mb-3">
            <RouterLink :to="exerciseLink(ex.id)" class="font-semibold text-ink dark:text-white hover:text-primary">{{ ex.name }}</RouterLink>
            <p class="text-xs text-steel-700 dark:text-steel-300 text-right tabular-nums">
              {{ metricSummary(ex) }}
            </p>
          </div>
          <CycleExerciseChart :points="ex.points" :metric="metric" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft } from 'lucide-vue-next'
import CycleExerciseChart from '@/components/exercises/CycleExerciseChart.vue'
import { computeProgress, cycleSchedules } from '@/utils/progress.js'

const route = useRoute()
const store = useStore()

// Coach mode (/coach/athletes/:athleteId/cycles/:scheduleId) reads the
// athlete's data; otherwise it's the current user's own plan.
const athleteId = computed(() => route.params.athleteId ? Number(route.params.athleteId) : null)
const athleteData = computed(() => athleteId.value ? store.getters['coach/athleteById'](athleteId.value) : null)
const source = computed(() => athleteId.value
  ? { workouts: athleteData.value?.workouts || [], planned: athleteData.value?.planned || [], maxes: athleteData.value?.maxes || [] }
  : { workouts: store.state.workouts.workouts, planned: store.state.planned.plannedWorkouts, maxes: store.state.user.maxes })

const loading = ref(false)
onMounted(async () => {
  loading.value = true
  try {
    if (athleteId.value) await store.dispatch('coach/loadAthlete', { id: athleteId.value, force: true })
    else await store.dispatch('planned/fetchPlannedWorkouts')
  } finally {
    loading.value = false
  }
})

const schedule = computed(() => cycleSchedules(source.value.planned).find(s => s.id === route.params.scheduleId) || null)
const remaining = computed(() => schedule.value.total - schedule.value.completed - schedule.value.skipped)

const statusLabel = { planned: 'запланировано', completed: 'выполнено', skipped: 'пропущено' }
function segmentClass(status) {
  return { completed: 'bg-success', skipped: 'bg-steel-300 dark:bg-steel-700', planned: 'bg-steel-100 dark:bg-steel-700/50' }[status]
}
function planLink(p) {
  if (p.status === 'completed' && p.completedWorkoutId) {
    return athleteId.value ? `/coach/athletes/${athleteId.value}/workouts/${p.completedWorkoutId}` : `/workouts/${p.completedWorkoutId}`
  }
  return athleteId.value ? `/coach/athletes/${athleteId.value}` : `/planning/${p.id}`
}
function exerciseLink(exerciseId) {
  return athleteId.value ? `/coach/athletes/${athleteId.value}/exercises/${exerciseId}` : `/exercises/${exerciseId}`
}

// The lifts to chart: the cycle's main exercises, matched to the ids the
// plans actually carry; without any marked, every lift in the cycle.
const usingMainExercises = computed(() => !!schedule.value?.mainExercises.length)
const lifts = computed(() => {
  if (!schedule.value) return []
  const seen = new Map()
  schedule.value.plans.forEach(p => p.exercises.forEach(e => {
    if (!seen.has(e.exerciseName)) seen.set(e.exerciseName, { id: e.exerciseId, name: e.exerciseName })
  }))
  if (!usingMainExercises.value) return [...seen.values()]
  return schedule.value.mainExercises
    .map(m => [...seen.values()].find(e => (m.exerciseId && e.id === m.exerciseId) || e.name === m.exerciseName))
    .filter(Boolean)
})

const metrics = [
  { value: 'intensity', label: 'Интенсивность' },
  { value: 'lifts', label: 'КПШ' },
  { value: 'tonnage', label: 'Тоннаж' },
]
const metric = ref('intensity')

// One point per cycle workout that includes the lift: what the plan asked
// for and what was done, from the same series as the exercise charts.
const exerciseSeries = computed(() => lifts.value.map(lift => {
  const args = {
    exercise: store.getters['exercises/exerciseById'](lift.id) || { id: lift.id, name: lift.name },
    exerciseId: lift.id,
    ...source.value,
  }
  const planSessions = computeProgress({ ...args, source: 'plan' })
  const factSessions = computeProgress({ ...args, source: 'fact' })
  const points = schedule.value.plans
    .filter(p => p.exercises.some(e => e.exerciseId === lift.id))
    .map((p, i) => ({
      label: workoutName(p) ? [`Т${i + 1}`, workoutName(p)] : `Т${i + 1}`,
      title: `${p.title}, ${formatDate(p.scheduledDate)}`,
      plan: planSessions.find(s => s.workoutId === p.id) || null,
      fact: p.completedWorkoutId ? factSessions.find(s => s.workoutId === p.completedWorkoutId) || null : null,
    }))
  return { ...lift, points }
}))

// The cycle workout's own name, from a plan titled "<name> — <cycle title>";
// default "Тренировка N" names add nothing to the chart axis.
function workoutName(p) {
  const name = p.title.split(' — ')[0].trim()
  if (/^Тренировка \d+$/.test(name)) return ''
  return name.length > 14 ? `${name.slice(0, 13)}…` : name
}

// Totals over the workouts done so far, against what the plan asked for them.
function metricSummary(ex) {
  const done = ex.points.filter(p => p.fact)
  if (!done.length) return 'ещё не выполнялось'
  if (metric.value === 'intensity') {
    const avg = side => Math.round(done.reduce((s, p) => s + (p[side]?.relIntensity || 0), 0) / done.length)
    return `средняя ${avg('fact')}% · по плану ${avg('plan')}%`
  }
  const key = metric.value === 'lifts' ? 'lifts' : 'totalVolume'
  const unit = metric.value === 'lifts' ? '' : ' кг'
  const sum = side => done.reduce((s, p) => s + (p[side]?.[key] || 0), 0)
  return `${sum('fact')}${unit} из ${sum('plan')}${unit} за ${done.length} ${plural(done.length, 'тренировку', 'тренировки', 'тренировок')}`
}

function plural(n, one, few, many) {
  const m10 = n % 10, m100 = n % 100
  if (m10 === 1 && m100 !== 11) return one
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few
  return many
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}
</script>
