<template>
  <div class="space-y-6">

    <!-- Greeting -->
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-steel-700 dark:text-steel-300 mb-0.5">{{ todayLabel }}</p>
        <h2 class="text-2xl font-bold text-ink dark:text-white">
          {{ greeting }}<template v-if="userName">, {{ firstName }}</template>!
        </h2>
      </div>
      <RouterLink to="/workouts/new"
        class="btn btn-primary px-4 py-2 text-sm flex-shrink-0">
        <Plus class="w-4 h-4" />
        Тренировка
      </RouterLink>
    </div>

    <!-- Today's planned workout -->
    <div v-if="todaysPlan" class="card border-l-[6px] border-l-primary p-4 flex items-center gap-3">
      <div class="w-10 h-10 border-2 border-primary bg-primary/10 flex items-center justify-center flex-shrink-0">
        <CalendarClock class="w-5 h-5 text-primary" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-xs text-primary font-semibold uppercase tracking-wide">Запланировано на сегодня</p>
        <p class="font-semibold text-sm text-ink dark:text-white truncate">{{ todaysPlan.title }}</p>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <button
          class="px-3 py-2 bg-primary text-white text-sm font-display font-semibold uppercase tracking-wide hover:bg-primary-dark transition-colors flex items-center gap-1.5"
          @click="startTodaysPlan"
        ><Play class="w-3.5 h-3.5" />Начать</button>
        <button
          class="w-9 h-9 flex items-center justify-center text-steel-700 dark:text-steel-300 hover:text-primary transition-colors"
          title="Пропустить"
          @click="skipTodaysPlan"
        ><Ban class="w-4 h-4" /></button>
      </div>
    </div>

    <!-- Top stat cards -->
    <div class="grid grid-cols-3 gap-3">
      <div class="card p-3 flex flex-col items-center text-center gap-1">
        <div class="h-7 flex items-center justify-center gap-1 text-steel-700 dark:text-steel-300">
          <Flame :class="['w-3.5 h-3.5 flex-shrink-0', currentStreak > 0 ? 'text-primary' : '']" />
          <span class="text-[11px] leading-tight">стрик дней</span>
        </div>
        <span :class="['text-2xl font-mono font-bold tabular-nums whitespace-nowrap', currentStreak > 0 ? 'text-primary' : 'text-ink dark:text-white']">{{ currentStreak }}</span>
        <span class="text-xs text-steel-300">{{ longestStreak > 1 ? `макс ${longestStreak}` : '—' }}</span>
      </div>

      <div class="card p-3 flex flex-col items-center text-center gap-1">
        <div class="h-7 flex items-center justify-center gap-1 text-steel-700 dark:text-steel-300">
          <Dumbbell :class="['w-3.5 h-3.5 flex-shrink-0', workoutsThisWeek > 0 ? 'text-primary' : '']" />
          <span class="text-[11px] leading-tight">тренировок за неделю</span>
        </div>
        <span :class="['text-2xl font-mono font-bold tabular-nums whitespace-nowrap', workoutsThisWeek > 0 ? 'text-primary' : 'text-ink dark:text-white']">{{ workoutsThisWeek }}</span>
        <span class="text-xs text-steel-300">{{ workoutsThisMonth }} в мес.</span>
      </div>

      <div class="card p-3 flex flex-col items-center text-center gap-1">
        <div class="h-7 flex items-center justify-center gap-1 text-steel-700 dark:text-steel-300">
          <TrendingUp :class="['w-3.5 h-3.5 flex-shrink-0', volumeDelta >= 0 ? 'text-success' : 'text-primary']" />
          <span class="text-[11px] leading-tight">тоннаж за мес.</span>
        </div>
        <span class="text-2xl font-mono font-bold tabular-nums whitespace-nowrap text-ink dark:text-white">{{ formatVolumeShort(monthVolume) }}</span>
        <span :class="['text-xs', volumeDelta > 0 ? 'text-success' : volumeDelta < 0 ? 'text-primary' : 'text-steel-300']">
          <template v-if="lastMonthVolume > 0">{{ volumeDelta >= 0 ? '+' : '' }}{{ Math.round(volumeDelta) }}%</template>
          <template v-else>—</template>
        </span>
      </div>
    </div>

    <!-- Plan adherence -->
    <div>
      <h3 class="text-base font-semibold text-ink dark:text-white flex items-center gap-2 mb-3">
        <CalendarCheck class="w-4 h-4 text-primary" />
        Выполнение плана
      </h3>

      <div class="card p-4">
        <div class="flex bg-steel-100 dark:bg-steel-950 p-0.5 gap-0.5 mb-4">
          <button
            v-for="p in adherencePeriods" :key="p.key"
            :class="['flex-1 py-1.5 text-xs font-medium transition-colors',
              adherencePeriod === p.key
                ? 'bg-card dark:bg-steel-700 text-primary'
                : 'text-steel-700 dark:text-steel-300 hover:text-primary']"
            @click="adherencePeriod = p.key"
          >{{ p.label }}</button>
        </div>

        <template v-if="adherenceStats.total > 0">
          <div class="flex items-end gap-2 mb-2">
            <span class="text-3xl font-display font-bold text-ink dark:text-white">{{ adherenceStats.rate }}%</span>
            <span class="text-xs text-steel-700 dark:text-steel-300 mb-1">выполнено из запланированного</span>
          </div>
          <div class="h-2.5 bg-steel-100 dark:bg-steel-950 overflow-hidden flex mb-4">
            <div class="h-full bg-success" :style="{ width: adherencePct(adherenceStats.completed) + '%' }" />
            <div class="h-full bg-steel-300 dark:bg-steel-700" :style="{ width: adherencePct(adherenceStats.skipped) + '%' }" />
          </div>
          <div class="grid grid-cols-2 gap-2 text-center">
            <div>
              <p class="text-sm font-bold text-success">{{ adherenceStats.completed }}</p>
              <p class="text-xs text-steel-700 dark:text-steel-300">Выполнено</p>
            </div>
            <div>
              <p class="text-sm font-bold text-steel-700 dark:text-steel-300">{{ adherenceStats.skipped }}</p>
              <p class="text-xs text-steel-700 dark:text-steel-300">Пропущено</p>
            </div>
          </div>
        </template>
        <div v-else class="text-center py-6 text-sm text-steel-700 dark:text-steel-300">
          Нет запланированных тренировок за этот период
        </div>
      </div>
    </div>

    <!-- Month-to-month comparison -->
    <div>
      <h3 class="text-base font-semibold text-ink dark:text-white flex items-center gap-2 mb-3">
        <BarChart2 class="w-4 h-4 text-primary" />
        Динамика по месяцам
      </h3>

      <div class="card p-4">
        <!-- Metric tabs -->
        <div class="flex bg-steel-100 dark:bg-steel-950 p-0.5 gap-0.5 mb-4">
          <button
            v-for="m in metrics" :key="m.key"
            :class="['flex-1 py-1.5 text-xs font-medium transition-colors',
              activeMetric === m.key
                ? 'bg-card dark:bg-steel-700 text-primary'
                : 'text-steel-700 dark:text-steel-300 hover:text-primary']"
            @click="activeMetric = m.key"
          >{{ m.label }}</button>
        </div>

        <!-- Bars -->
        <div class="space-y-2.5">
          <div v-for="(m, i) in monthlyStats" :key="m.prefix" class="flex items-center gap-3">
            <span class="text-xs text-steel-700 dark:text-steel-300 w-12 flex-shrink-0 capitalize">{{ m.shortLabel }}</span>
            <div class="flex-1 h-5 bg-steel-100 dark:bg-steel-950 overflow-hidden">
              <div
                :class="['h-full transition-all duration-500', barColor(i)]"
                :style="{ width: barWidth(m) + '%' }"
              />
            </div>
            <div class="w-20 flex items-center justify-end gap-1 flex-shrink-0">
              <span class="text-xs font-mono font-semibold text-ink dark:text-steel-100">{{ formatMetric(m) }}</span>
              <span
                v-if="i > 0"
                :class="['text-xs font-medium', delta(i) > 0 ? 'text-success' : delta(i) < 0 ? 'text-primary' : 'text-steel-300']"
              >{{ delta(i) > 0 ? '↑' : delta(i) < 0 ? '↓' : '' }}</span>
            </div>
          </div>
        </div>

        <!-- Summary: current vs prev -->
        <div v-if="monthlyStats.length >= 2" class="mt-4 pt-4 border-t-2 border-steel-100 dark:border-steel-700 grid grid-cols-3 gap-2 text-center">
          <div v-for="m in metrics" :key="m.key">
            <p class="text-xs text-steel-700 dark:text-steel-300 mb-0.5">{{ m.label }}</p>
            <p class="text-sm font-mono font-bold text-ink dark:text-white">{{ formatMetricRaw(monthlyStats.at(-1), m.key) }}</p>
            <p :class="['text-xs', deltaForMetric(m.key) > 0 ? 'text-success' : deltaForMetric(m.key) < 0 ? 'text-primary' : 'text-steel-300']">
              <template v-if="monthlyStats.at(-2)[m.key] > 0">
                {{ deltaForMetric(m.key) >= 0 ? '+' : '' }}{{ Math.round(deltaForMetric(m.key)) }}%
              </template>
              <template v-else>—</template>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Personal records -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-ink dark:text-white flex items-center gap-2">
          <Trophy class="w-4 h-4 text-hazard" />
          Личные рекорды
        </h3>
        <RouterLink to="/exercises" class="text-xs text-primary hover:underline">Все упражнения</RouterLink>
      </div>

      <div v-if="topExercises.length" class="grid grid-cols-2 gap-3">
        <RouterLink
          v-for="item in topExercises"
          :key="item.id"
          :to="`/exercises/${item.id}`"
          class="card p-3.5 hover:border-primary transition-colors block"
        >
          <p class="text-xs text-steel-700 dark:text-steel-300 mb-1 truncate">{{ item.exercise.muscleGroup }}</p>
          <p class="font-semibold text-sm text-ink dark:text-white mb-2 line-clamp-2 leading-tight">{{ item.exercise.name }}</p>
          <div class="space-y-0.5">
            <div class="flex items-baseline gap-1">
              <span class="text-lg font-mono font-bold text-primary leading-none">{{ item.pr.bestWeight }}</span>
              <span class="text-xs text-steel-700 dark:text-steel-300">кг × {{ item.pr.bestWeightReps }} повт.</span>
            </div>
            <div class="flex items-center gap-1 text-xs text-steel-700 dark:text-steel-300">
              <span>1ПМ:</span>
              <span class="font-mono font-medium text-ink dark:text-steel-100">{{ item.pr.best1RM }} кг</span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else class="card p-6 text-center text-sm text-steel-700 dark:text-steel-300">
        Нет данных — запишите первую тренировку
      </div>
    </div>

    <!-- Recent workouts -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-ink dark:text-white flex items-center gap-2">
          <ClipboardList class="w-4 h-4 text-steel-300" />
          Последние тренировки
        </h3>
        <RouterLink to="/history" class="text-xs text-primary hover:underline">Вся история</RouterLink>
      </div>

      <div v-if="recentWorkouts.length" class="space-y-2">
        <RouterLink
          v-for="w in recentWorkouts"
          :key="w.id"
          :to="`/workouts/${w.id}`"
          class="card p-3.5 flex items-center gap-3 hover:border-primary transition-colors block"
        >
          <div :class="['w-2 h-10 flex-shrink-0', typeColorBar(w.type)]" />
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-ink dark:text-white truncate">{{ w.title }}</p>
            <p class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">
              {{ formatDate(w.date) }}
              <template v-if="workoutVolume(w) > 0"> · {{ formatVolumeShort(workoutVolume(w)) }} тоннаж</template>
              <template v-if="w.durationMinutes"> · {{ w.durationMinutes }} мин</template>
            </p>
          </div>
          <ChevronRight class="w-4 h-4 text-steel-300 flex-shrink-0" />
        </RouterLink>
      </div>

      <div v-else class="card p-6 text-center text-sm text-steel-700 dark:text-steel-300">
        Пока нет тренировок
      </div>
    </div>

    <SkipOrRescheduleModal v-model="showSkipConfirm" :plan="todaysPlan" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Flame, Dumbbell, TrendingUp, Trophy, ClipboardList, Plus, ChevronRight, BarChart2, CalendarClock, CalendarCheck, Play, Ban } from 'lucide-vue-next'
import SkipOrRescheduleModal from '@/components/workout/SkipOrRescheduleModal.vue'

const store = useStore()
const router = useRouter()

onMounted(() => {
  if (!store.state.workouts.workouts.length) store.dispatch('workouts/initWorkouts')
  if (!store.state.exercises.library.length) store.dispatch('exercises/initExercises')
  if (!store.state.user.profile?.name) store.dispatch('user/initUser')
  if (!store.state.planned.plannedWorkouts.length) store.dispatch('planned/fetchPlannedWorkouts')
})

// ── Greeting ──────────────────────────────────────────────────────────────────
const userName = computed(() => store.getters['auth/userName'] || store.state.user.profile?.name || '')
const firstName = computed(() => userName.value.split(' ')[0])

const today = new Date()
const todayLabel = computed(() => today.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' }))

const greeting = computed(() => {
  const h = today.getHours()
  if (h < 6) return 'Доброй ночи'
  if (h < 12) return 'Доброе утро'
  if (h < 18) return 'Добрый день'
  return 'Добрый вечер'
})

// ── Workouts data ──────────────────────────────────────────────────────────────
const allWorkouts = computed(() => store.getters['workouts/allWorkouts'])

function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const todayStr = toDateStr(today)

// ── Today's planned workout ──────────────────────────────────────────────────
const todaysPlan = computed(() =>
  store.state.planned.plannedWorkouts.find(p => p.status === 'planned' && p.scheduledDate === todayStr)
)
const showSkipConfirm = ref(false)

async function startTodaysPlan() {
  await store.dispatch('workouts/startWorkoutFromPlan', todaysPlan.value)
  router.push('/workouts/new')
}

function skipTodaysPlan() {
  showSkipConfirm.value = true
}

// Current streak (consecutive days ending today or yesterday)
const currentStreak = computed(() => {
  const dates = [...new Set(allWorkouts.value.map(w => w.date))].sort().reverse()
  if (!dates.length) return 0
  const yesterday = toDateStr(new Date(today - 86400000))
  if (dates[0] !== todayStr && dates[0] !== yesterday) return 0
  let streak = 1
  for (let i = 1; i < dates.length; i++) {
    const diff = (new Date(dates[i - 1]) - new Date(dates[i])) / 86400000
    if (diff === 1) streak++
    else break
  }
  return streak
})

const longestStreak = computed(() => store.getters['workouts/longestStreak'])
const workoutsThisWeek = computed(() => store.getters['workouts/workoutsThisWeek'])

const workoutsThisMonth = computed(() => {
  const prefix = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  return allWorkouts.value.filter(w => w.date.startsWith(prefix)).length
})

// ── Volume ─────────────────────────────────────────────────────────────────────
function calcVol(workouts) {
  return workouts.reduce((sum, w) =>
    sum + w.exercises.reduce((s, ex) =>
      s + ex.sets.filter(set => !set.failed).reduce((ss, set) => ss + set.weight * set.reps, 0), 0), 0)
}

const monthVolume = computed(() => {
  const prefix = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  return calcVol(allWorkouts.value.filter(w => w.date.startsWith(prefix)))
})

const lastMonthVolume = computed(() => {
  const d = new Date(today.getFullYear(), today.getMonth() - 1, 1)
  const prefix = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  return calcVol(allWorkouts.value.filter(w => w.date.startsWith(prefix)))
})

const volumeDelta = computed(() => {
  if (!lastMonthVolume.value) return 0
  return ((monthVolume.value - lastMonthVolume.value) / lastMonthVolume.value) * 100
})

function formatVolumeShort(v) {
  if (!v) return '0'
  // Non-breaking space — the number and unit must never split across lines.
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v + ' кг'
}

// ── Plan adherence ─────────────────────────────────────────────────────────────
const adherencePeriod = ref('month')
const adherencePeriods = [
  { key: 'week', label: '7 дней', days: 7 },
  { key: 'month', label: '30 дней', days: 30 },
  { key: 'year', label: 'Год', days: 365 },
]

const allPlanned = computed(() => store.state.planned.plannedWorkouts)

const adherenceStats = computed(() => {
  const days = adherencePeriods.find(p => p.key === adherencePeriod.value).days
  let cutoff = null
  if (days) cutoff = toDateStr(new Date(today - days * 86400000))

  // The backend auto-flips any overdue 'planned' entry to 'skipped' the moment
  // the list is fetched (see expire_overdue in planned_workout.py) — so by the
  // time this runs, 'planned' items left are genuinely still upcoming, and only
  // 'completed'/'skipped' represent plans that have actually been resolved.
  const due = allPlanned.value.filter(p => {
    if (p.status !== 'completed' && p.status !== 'skipped') return false
    if (cutoff && p.scheduledDate < cutoff) return false
    return true
  })

  const completed = due.filter(p => p.status === 'completed').length
  const skipped = due.length - completed
  const total = due.length

  return { completed, skipped, total, rate: total > 0 ? Math.round((completed / total) * 100) : 0 }
})

function adherencePct(n) {
  return adherenceStats.value.total > 0 ? (n / adherenceStats.value.total) * 100 : 0
}

// ── Month-to-month comparison ─────────────────────────────────────────────────
const activeMetric = ref('volume')

const metrics = [
  { key: 'volume', label: 'Тоннаж' },
  { key: 'count', label: 'Тренировки' },
  { key: 'avgDuration', label: 'Ср. время' },
]

const monthlyStats = computed(() => {
  const result = []
  for (let i = 5; i >= 0; i--) {
    const d = new Date(today.getFullYear(), today.getMonth() - i, 1)
    const prefix = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const shortLabel = d.toLocaleDateString('ru-RU', { month: 'short' }).replace('.', '')
    const ws = allWorkouts.value.filter(w => w.date.startsWith(prefix))
    const volume = calcVol(ws)
    const count = ws.length
    const totalDur = ws.reduce((s, w) => s + (w.durationMinutes || 0), 0)
    const avgDuration = count > 0 ? Math.round(totalDur / count) : 0
    result.push({ prefix, shortLabel, volume, count, avgDuration })
  }
  return result
})

const metricMax = computed(() =>
  Math.max(...monthlyStats.value.map(m => m[activeMetric.value]), 1)
)

function barWidth(m) {
  return Math.round((m[activeMetric.value] / metricMax.value) * 100)
}

const barColors = ['bg-steel-300', 'bg-steel-300', 'bg-primary-light', 'bg-primary-light', 'bg-primary', 'bg-primary']
function barColor(i) { return barColors[i] ?? 'bg-primary' }

function delta(i) {
  const prev = monthlyStats.value[i - 1]?.[activeMetric.value] ?? 0
  const cur = monthlyStats.value[i][activeMetric.value]
  if (!prev) return 0
  return ((cur - prev) / prev) * 100
}

function deltaForMetric(key) {
  const prev = monthlyStats.value.at(-2)?.[key] ?? 0
  const cur = monthlyStats.value.at(-1)?.[key] ?? 0
  if (!prev) return 0
  return ((cur - prev) / prev) * 100
}

function formatMetric(m) {
  const v = m[activeMetric.value]
  if (activeMetric.value === 'volume') return formatVolumeShort(v)
  if (activeMetric.value === 'count') return v + ' тр.'
  return v ? v + ' мин' : '—'
}

function formatMetricRaw(m, key) {
  if (!m) return '—'
  const v = m[key]
  if (key === 'volume') return formatVolumeShort(v)
  if (key === 'count') return v + ' тр.'
  return v ? v + ' мин' : '—'
}

// ── Personal records ──────────────────────────────────────────────────────────
const topExercises = computed(() => {
  const freq = {}
  for (const w of allWorkouts.value) {
    for (const ex of w.exercises) {
      freq[ex.exerciseId] = (freq[ex.exerciseId] || 0) + 1
    }
  }
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([id]) => {
      const exercise = store.getters['exercises/exerciseById'](id)
      const pr = store.getters['exercises/personalRecord'](id)
      return { id, exercise, pr }
    })
    .filter(e => e.exercise && e.pr && e.exercise.muscleGroup !== 'Кардио')
})

// ── Recent workouts ────────────────────────────────────────────────────────────
const recentWorkouts = computed(() => allWorkouts.value.slice(0, 4))

function workoutVolume(w) {
  return w.exercises.reduce((s, ex) =>
    s + ex.sets.filter(set => !set.failed).reduce((ss, set) => ss + set.weight * set.reps, 0), 0)
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

const typeColorBar = type => ({
  'Силовая': 'bg-indigo-400',
  'Кардио': 'bg-green-400',
  'Растяжка': 'bg-purple-400',
  'HIIT': 'bg-orange-400',
}[type] || 'bg-gray-300')
</script>
