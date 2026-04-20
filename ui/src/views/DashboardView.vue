<template>
  <div class="space-y-6">

    <!-- Greeting -->
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-gray-400 mb-0.5">{{ todayLabel }}</p>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ greeting }}<template v-if="userName">, {{ firstName }}</template>!
        </h2>
      </div>
      <RouterLink to="/workouts/new"
        class="btn btn-primary px-4 py-2 text-sm flex-shrink-0">
        <Plus class="w-4 h-4" />
        Тренировка
      </RouterLink>
    </div>

    <!-- Top stat cards -->
    <div class="grid grid-cols-3 gap-3">
      <div class="card p-4 flex flex-col items-center text-center gap-1">
        <div class="flex items-center gap-1.5">
          <Flame :class="['w-5 h-5', currentStreak > 0 ? 'text-orange-400' : 'text-gray-300']" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">{{ currentStreak }}</span>
        </div>
        <span class="text-xs text-gray-400 leading-tight">стрик дней</span>
        <span v-if="longestStreak > 1" class="text-xs text-gray-300 dark:text-gray-600">макс {{ longestStreak }}</span>
      </div>

      <div class="card p-4 flex flex-col items-center text-center gap-1">
        <div class="flex items-center gap-1.5">
          <Dumbbell class="w-5 h-5 text-primary" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">{{ workoutsThisWeek }}</span>
        </div>
        <span class="text-xs text-gray-400 leading-tight">тренировок за неделю</span>
        <span class="text-xs text-gray-300 dark:text-gray-600">{{ workoutsThisMonth }} в этом мес.</span>
      </div>

      <div class="card p-4 flex flex-col items-center text-center gap-1">
        <div class="flex items-center gap-1.5">
          <TrendingUp :class="['w-5 h-5', volumeDelta >= 0 ? 'text-green-400' : 'text-red-400']" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatVolumeShort(monthVolume) }}</span>
        </div>
        <span class="text-xs text-gray-400 leading-tight">тоннаж за мес.</span>
        <span :class="['text-xs leading-tight', volumeDelta > 0 ? 'text-green-400' : volumeDelta < 0 ? 'text-red-400' : 'text-gray-300 dark:text-gray-600']">
          <template v-if="lastMonthVolume > 0">
            {{ volumeDelta >= 0 ? '+' : '' }}{{ Math.round(volumeDelta) }}%
          </template>
          <template v-else>—</template>
        </span>
      </div>
    </div>

    <!-- Personal records -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Trophy class="w-4 h-4 text-yellow-500" />
          Личные рекорды
        </h3>
        <RouterLink to="/exercises" class="text-xs text-primary hover:underline">Все упражнения</RouterLink>
      </div>

      <div v-if="topExercises.length" class="grid grid-cols-2 gap-3">
        <RouterLink
          v-for="item in topExercises"
          :key="item.id"
          :to="`/exercises/${item.id}`"
          class="card p-3.5 hover:shadow-md transition-shadow block"
        >
          <p class="text-xs text-gray-400 mb-1 truncate">{{ item.exercise.muscleGroup }}</p>
          <p class="font-semibold text-sm text-gray-900 dark:text-white mb-2 line-clamp-2 leading-tight">{{ item.exercise.name }}</p>
          <div class="space-y-0.5">
            <div class="flex items-baseline gap-1">
              <span class="text-lg font-bold text-primary leading-none">{{ item.pr.bestWeight }}</span>
              <span class="text-xs text-gray-400">кг × {{ item.pr.bestWeightReps }} повт.</span>
            </div>
            <div class="flex items-center gap-1 text-xs text-gray-400">
              <span>1ПМ:</span>
              <span class="font-medium text-gray-700 dark:text-gray-300">{{ item.pr.best1RM }} кг</span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else class="card p-6 text-center text-sm text-gray-400">
        Нет данных — запишите первую тренировку
      </div>
    </div>

    <!-- Recent workouts -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <ClipboardList class="w-4 h-4 text-gray-400" />
          Последние тренировки
        </h3>
        <RouterLink to="/history" class="text-xs text-primary hover:underline">Вся история</RouterLink>
      </div>

      <div v-if="recentWorkouts.length" class="space-y-2">
        <RouterLink
          v-for="w in recentWorkouts"
          :key="w.id"
          :to="`/workouts/${w.id}`"
          class="card p-3.5 flex items-center gap-3 hover:shadow-md transition-shadow block"
        >
          <div :class="['w-2 h-10 rounded-full flex-shrink-0', typeColorBar(w.type)]" />
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-gray-900 dark:text-white truncate">{{ w.title }}</p>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ formatDate(w.date) }}
              <template v-if="workoutVolume(w) > 0"> · {{ formatVolumeShort(workoutVolume(w)) }} тоннаж</template>
              <template v-if="w.durationMinutes"> · {{ w.durationMinutes }} мин</template>
            </p>
          </div>
          <ChevronRight class="w-4 h-4 text-gray-300 flex-shrink-0" />
        </RouterLink>
      </div>

      <div v-else class="card p-6 text-center text-sm text-gray-400">
        Пока нет тренировок
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Flame, Dumbbell, TrendingUp, Trophy, ClipboardList, Plus, ChevronRight } from 'lucide-vue-next'

const store = useStore()

onMounted(() => {
  if (!store.state.workouts.workouts.length) store.dispatch('workouts/initWorkouts')
  if (!store.state.exercises.library.length) store.dispatch('exercises/initExercises')
  if (!store.state.user.profile?.name) store.dispatch('user/initUser')
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
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v + ' кг'
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
