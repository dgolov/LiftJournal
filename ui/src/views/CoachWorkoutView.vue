<template>
  <div class="max-w-2xl">
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-steel-100 dark:hover:bg-steel-900 text-steel-700 dark:text-steel-300 mt-1 transition-colors" @click="$router.back()">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <div class="min-w-0">
        <RouterLink :to="`/coach/athletes/${athleteId}`" class="text-sm text-primary hover:underline">
          {{ data?.summary?.name || 'Подопечный' }}
        </RouterLink>
        <h2 class="text-2xl font-bold text-ink dark:text-white">{{ workout?.title || 'Тренировка' }}</h2>
        <p v-if="workout" class="text-sm text-steel-700 dark:text-steel-300 mt-0.5">
          {{ formatDate(workout.date) }} · {{ workout.type }}
          <template v-if="workout.durationMinutes"> · {{ workout.durationMinutes }} мин</template>
          <template v-if="workoutTonnage"> · тоннаж {{ formatTonnage(workoutTonnage) }}</template>
        </p>
      </div>
    </div>

    <div v-if="!data" class="text-center py-16 text-steel-300">Загрузка…</div>
    <div v-else-if="!workout" class="card p-6 text-center text-steel-700 dark:text-steel-300">
      Тренировка не найдена — возможно, подопечный её удалил.
    </div>

    <template v-else>
      <p v-if="workout.notes" class="card p-4 mb-4 text-sm text-steel-700 dark:text-steel-300 whitespace-pre-line">{{ workout.notes }}</p>

      <!-- Plan this workout fulfilled -->
      <div v-if="plan" class="card p-4 mb-4 border-l-4 border-l-primary">
        <div class="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <p class="text-xs text-steel-700 dark:text-steel-300">
              Выполнено по плану<template v-if="plan.createdByName"> от {{ plan.createdById === myId ? 'вас' : plan.createdByName }}</template>
            </p>
            <p class="font-semibold text-ink dark:text-white">{{ plan.title }}</p>
          </div>
          <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5">
            <button
              v-for="m in modes" :key="m.value"
              :class="['px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                mode === m.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300']"
              @click="mode = m.value"
            >{{ m.label }}</button>
          </div>
        </div>
        <div v-if="mode === 'compare'" class="grid grid-cols-3 gap-4 mt-4">
          <div v-for="k in compareKeys" :key="k.key" class="tabular-nums">
            <p class="text-xs text-steel-700 dark:text-steel-300">{{ k.label }}</p>
            <p class="mt-0.5">
              <span class="text-lg font-semibold text-ink dark:text-white">{{ k.format(totals[k.key]) }}</span>
              <span class="text-xs text-steel-700 dark:text-steel-300"> из {{ k.format(planTotals[k.key]) }}</span>
            </p>
            <div class="h-1 mt-1.5 rounded-full bg-steel-100 dark:bg-steel-700 overflow-hidden">
              <div :class="['h-full rounded-full transition-[width]', progress(k.key).tone]" :style="{ width: progress(k.key).width }" />
            </div>
          </div>
        </div>
      </div>

      <!-- Exercises -->
      <div class="space-y-3">
        <div v-for="row in rows" :key="row.exerciseId" class="card p-4">
          <div class="flex items-start justify-between gap-3 mb-3">
            <RouterLink :to="`/coach/athletes/${athleteId}/exercises/${row.exerciseId}`" class="font-semibold text-ink dark:text-white hover:text-primary">
              {{ row.exerciseName }}
            </RouterLink>
            <BaseBadge v-if="plan && mode === 'compare' && !row.planned" color="gray">вне плана</BaseBadge>
            <BaseBadge v-else-if="plan && mode === 'compare' && !row.done" color="red">не выполнено</BaseBadge>
          </div>

          <SetLedger
            :plan-sets="row.planned?.sets || null"
            :fact-sets="row.done?.sets || null"
            :one-rep-max="row.stats?.baseline1RM || row.planStats?.baseline1RM || 0"
            :compare="!!plan && mode === 'compare'"
          />

          <p v-if="row.stats" class="mt-3 pt-3 border-t border-steel-100 dark:border-steel-700 text-xs text-steel-700 dark:text-steel-300 flex flex-wrap gap-x-3 gap-y-1">
            <span>КПШ {{ row.stats.lifts }}</span>
            <span>Тоннаж {{ row.stats.totalVolume }} кг</span>
            <span title="Абсолютная интенсивность — средний вес подъёма в рабочих подходах (от 50% 1ПМ)">Абс. инт. {{ row.stats.avgWeight }} кг</span>
            <span v-if="row.stats.relIntensity != null" :title="`Относительная интенсивность — от 1ПМ ${row.stats.baseline1RM} кг`">Отн. инт. {{ row.stats.relIntensity }}%</span>
            <span v-if="row.stats.best1RM">Расч. 1ПМ {{ row.stats.best1RM }} кг</span>
          </p>
        </div>
      </div>

      <WorkoutSocialPanel
        class="mt-6"
        :workout-id="workout.id"
        :coach-ids="[myId]"
        :placeholder="`Комментарий для ${data.summary?.name || 'подопечного'}…`"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft } from 'lucide-vue-next'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import SetLedger from '@/components/coach/SetLedger.vue'
import WorkoutSocialPanel from '@/components/social/WorkoutSocialPanel.vue'
import { apiErrorMessage } from '@/services/workoutService.js'
import { computeProgress } from '@/utils/progress.js'
import { comparableTotals } from '@/utils/setAlignment.js'

const route = useRoute()
const router = useRouter()
const store = useStore()

const athleteId = computed(() => Number(route.params.athleteId))
const myId = computed(() => store.state.auth.userId)
const data = computed(() => store.getters['coach/athleteById'](athleteId.value))
const workout = computed(() => data.value?.workouts.find(w => w.id === route.params.workoutId) || null)
const plan = computed(() => data.value?.planned.find(p => p.completedWorkoutId === route.params.workoutId) || null)

const modes = [{ value: 'compare', label: 'План / факт' }, { value: 'fact', label: 'Только факт' }]
const mode = ref('compare')

onMounted(async () => {
  try {
    await store.dispatch('coach/loadAthlete', { id: athleteId.value })
    // Arriving from a fresh "completed" notification, the cached history can
    // predate this workout — refetch once before calling it missing.
    if (!workout.value) await store.dispatch('coach/loadAthlete', { id: athleteId.value, force: true })
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
    router.replace('/coach')
  }
})

// Same series the athlete's charts are built from, so КПШ, intensity and the
// 1RM baseline here match the exercise pages exactly.
function sessionsFor(exerciseId, exerciseName, source) {
  return computeProgress({
    exercise: store.getters['exercises/exerciseById'](exerciseId) || { id: exerciseId, name: exerciseName },
    exerciseId,
    workouts: data.value.workouts,
    planned: data.value.planned,
    maxes: data.value.maxes,
    source,
  })
}

// One row per exercise from the fact and the plan, fact order first; plan-only
// exercises (skipped by the athlete) go last.
const rows = computed(() => {
  if (!workout.value) return []
  const planned = plan.value?.exercises || []
  const result = workout.value.exercises.map(ex => ({
    exerciseId: ex.exerciseId,
    exerciseName: ex.exerciseName,
    done: ex,
    planned: planned.find(p => p.exerciseId === ex.exerciseId) || null,
  }))
  planned.forEach(p => {
    if (!result.some(r => r.exerciseId === p.exerciseId)) {
      result.push({ exerciseId: p.exerciseId, exerciseName: p.exerciseName, done: null, planned: p })
    }
  })
  return result.map(r => {
    const fact = r.done && sessionsFor(r.exerciseId, r.exerciseName, 'fact').find(s => s.workoutId === workout.value.id)
    const planned = r.planned && plan.value && sessionsFor(r.exerciseId, r.exerciseName, 'plan').find(s => s.workoutId === plan.value.id)
    return { ...r, stats: fact?.lifts != null ? fact : null, planStats: planned?.lifts != null ? planned : null }
  })
})

// Plan-vs-fact totals over what the plan covered (see comparableTotals):
// unplanned warm-ups don't count as overshoot. Plain sums on both sides, so
// the top uses "Повторения", not КПШ — КПШ with its 50%-of-1RM rule stays in
// each exercise's own summary line.
const comparison = computed(() => {
  const acc = { plan: { tonnage: 0, reps: 0, sets: 0 }, fact: { tonnage: 0, reps: 0, sets: 0 } }
  rows.value.forEach(r => {
    const t = comparableTotals(r.planned?.sets || null, r.done?.sets || null)
    for (const side of ['plan', 'fact']) for (const k in t[side]) acc[side][k] += t[side][k]
  })
  return acc
})
const totals = computed(() => comparison.value.fact)
const planTotals = computed(() => comparison.value.plan)
// Header tonnage: everything lifted, warm-ups included.
const workoutTonnage = computed(() => rows.value.reduce((sum, r) => sum + (r.stats?.totalVolume || 0), 0))

const compareKeys = [
  { key: 'tonnage', label: 'Тоннаж', format: v => formatTonnage(v) },
  { key: 'reps', label: 'Повторения', format: v => String(v) },
  { key: 'sets', label: 'Подходов', format: v => String(v) },
]

// Completion of the plan for a total: the bar fills up to 100%; within ±5%
// reads as on target, below as under (primary), above as over (hazard).
function progress(key) {
  const fact = totals.value[key]
  const planned = planTotals.value[key]
  if (!planned) return { width: '0%', tone: 'bg-steel-300' }
  const ratio = fact / planned
  const tone = ratio > 1.05 ? 'bg-hazard' : ratio < 0.95 ? 'bg-primary' : 'bg-success'
  return { width: `${Math.min(ratio, 1) * 100}%`, tone }
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}
function formatTonnage(kg) {
  return kg >= 1000 ? `${(kg / 1000).toFixed(1)} т` : `${kg} кг`
}
</script>
