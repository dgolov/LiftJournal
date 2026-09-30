<template>
  <div>
    <button class="flex items-center gap-1 text-sm text-gray-500 hover:text-primary mb-4 transition-colors" @click="$router.back()">
      <ChevronLeft class="w-4 h-4" /> Назад
    </button>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card p-6 animate-pulse flex items-center gap-4 mb-4">
      <div class="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
      <div class="flex-1 space-y-2">
        <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-40" />
        <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-56" />
      </div>
    </div>

    <template v-else-if="profile">
      <!-- Profile header -->
      <div class="card p-5 flex items-start gap-4 mb-4">
        <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary flex-shrink-0">
          {{ profile.name.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ profile.name }}</h2>
              <p v-if="profile.age" class="text-sm text-gray-500 mt-0.5">{{ profile.age }} лет</p>
            </div>
            <BaseButton
              v-if="!isSelf"
              :variant="profile.isFollowing ? 'outline' : 'primary'"
              size="sm"
              :loading="followLoading"
              class="flex-shrink-0"
              @click="toggleFollow"
            >{{ profile.isFollowing ? 'Отписаться' : 'Подписаться' }}</BaseButton>
          </div>
          <div class="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-sm text-gray-500">
            <span class="whitespace-nowrap"><strong class="text-gray-900 dark:text-white">{{ profile.workoutsCount }}</strong> тренировок</span>
            <span class="whitespace-nowrap"><strong class="text-gray-900 dark:text-white">{{ profile.followersCount }}</strong> подписчиков</span>
            <span class="whitespace-nowrap"><strong class="text-gray-900 dark:text-white">{{ profile.followingCount }}</strong> подписок</span>
            <span v-if="profile.athletesCount != null" class="whitespace-nowrap"><strong class="text-gray-900 dark:text-white">{{ profile.athletesCount }}</strong> {{ athletesWord }}</span>
          </div>
          <div v-if="profile.coaches?.length || profile.currentWeight" class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-steel-700 dark:text-steel-300">
            <span v-if="profile.coaches?.length">
              {{ profile.coaches.length > 1 ? 'Тренеры' : 'Тренер' }}:
              <template v-for="(c, i) in profile.coaches" :key="c.id">
                <RouterLink :to="`/users/${c.id}`" class="font-medium text-ink dark:text-white hover:text-primary">{{ c.name }}</RouterLink><template v-if="i < profile.coaches.length - 1">, </template>
              </template>
            </span>
            <span
              v-if="profile.currentWeight"
              class="inline-flex items-center gap-1"
              :title="isSelf ? '' : 'Видно только вам как тренеру'"
            >
              <Lock v-if="!isSelf" class="w-3.5 h-3.5" />
              Вес <strong class="text-ink dark:text-white">{{ profile.currentWeight.kg }} кг</strong>
              <span class="text-xs">на {{ formatShortDate(profile.currentWeight.date) }}</span>
            </span>
          </div>
          <PublicProfileCoachBar v-if="!isSelf" :profile="profile" @changed="reloadProfile" />
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 dark:border-gray-800 mb-5">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="px-4 py-2.5 text-sm font-medium transition-colors border-b -mb-px"
          :class="activeTab === tab.id
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="activeTab = tab.id"
        >{{ tab.label }}</button>
      </div>

      <!-- TAB: Profile -->
      <div v-if="activeTab === 'profile'" class="space-y-5">
        <!-- Activity heatmap -->
        <div class="card p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Flame class="w-4 h-4 text-orange-400" />
            Активность за год
          </h3>
          <div v-if="activityLoading" class="h-20 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
          <ActivityHeatmap v-else :activity="activity" />
        </div>

        <!-- Achievements & Maxes row -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Achievements -->
          <div class="card p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Medal class="w-4 h-4 text-yellow-400" />
              Достижения
              <span v-if="achievements.length" class="text-xs text-gray-400 font-normal">({{ achievements.length }})</span>
            </h3>
            <div v-if="achievementsLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
            <div v-else-if="!achievements.length" class="text-sm text-gray-400 py-2">Пока нет достижений</div>
            <div v-else class="grid grid-cols-3 gap-2">
              <div
                v-for="a in achievements"
                :key="a.id"
                class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 dark:bg-gray-800/50 text-center"
                :title="a.title"
              >
                <span class="text-2xl leading-none">{{ a.icon }}</span>
                <span class="text-xs text-gray-600 dark:text-gray-400 leading-tight line-clamp-2">{{ a.title }}</span>
              </div>
            </div>
          </div>

          <!-- Personal maxes -->
          <div class="card p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Dumbbell class="w-4 h-4 text-primary" />
              Личные максимумы
            </h3>
            <div v-if="maxesLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
            <div v-else-if="!maxes.length" class="text-sm text-gray-400 py-2">Нет данных</div>
            <div v-else class="space-y-2">
              <div
                v-for="m in maxes"
                :key="m.exerciseName"
                class="flex items-center justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
              >
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ m.exerciseName }}</span>
                <span class="text-sm font-semibold text-primary">{{ m.weightKg }} кг</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Goals -->
        <div class="card p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Target class="w-4 h-4 text-green-500" />
            Активные цели
          </h3>
          <div v-if="goalsLoading" class="space-y-2">
            <div v-for="i in 2" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
          </div>
          <div v-else-if="!goals.length" class="text-sm text-gray-400 py-2">Нет активных целей</div>
          <div v-else class="space-y-2">
            <div
              v-for="g in goals"
              :key="g.text"
              class="flex items-start gap-2 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
            >
              <div class="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ g.text }}</p>
                <p v-if="g.targetDate" class="text-xs text-gray-400 mt-0.5">до {{ formatDate(g.targetDate) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: Workouts — same look as the history screen -->
      <div v-else-if="activeTab === 'workouts'">
        <div class="flex items-center justify-between gap-3 mb-5 flex-wrap">
          <div v-if="!selectedDate" class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5">
            <button
              v-for="g in granularityOptions" :key="g.value"
              :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors', segClass(granularity === g.value)]"
              @click="setGranularity(g.value)"
            >{{ g.label }}</button>
          </div>
          <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5 ml-auto">
            <button
              :class="['p-2 rounded-lg transition-colors', segClass(workoutsView === 'calendar')]"
              title="Календарь"
              @click="switchWorkoutsView('calendar')"
            ><CalendarDays class="w-4 h-4" /></button>
            <button
              :class="['p-2 rounded-lg transition-colors', segClass(workoutsView === 'list')]"
              title="Список"
              @click="switchWorkoutsView('list')"
            ><List class="w-4 h-4" /></button>
          </div>
        </div>

        <!-- Period stats -->
        <div v-if="!selectedDate" class="grid grid-cols-3 gap-3 mb-5">
          <div class="card p-3 text-center">
            <div class="text-xl font-display font-bold text-primary">{{ periodWorkouts.length }}</div>
            <div class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">тренировок</div>
          </div>
          <div class="card p-3 text-center">
            <div class="text-xl font-display font-bold text-ink dark:text-white">{{ periodTotalVolume }}</div>
            <div class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">тоннаж</div>
          </div>
          <div class="card p-3 text-center">
            <div class="text-xl font-display font-bold text-ink dark:text-white">{{ periodTotalDuration }}</div>
            <div class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">часов</div>
          </div>
        </div>

        <!-- Period navigation -->
        <div v-if="!selectedDate" class="flex items-center gap-2 mb-5">
          <button class="p-2 hover:bg-steel-100 dark:hover:bg-steel-700 transition-colors text-steel-700 dark:text-steel-300" @click="prevPeriod">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <div class="flex-1 text-center">
            <span class="text-base font-semibold text-ink dark:text-white capitalize">{{ periodLabel }}</span>
            <span v-if="periodLoading" class="text-xs text-steel-700 dark:text-steel-300 ml-2">загрузка…</span>
          </div>
          <button class="p-2 hover:bg-steel-100 dark:hover:bg-steel-700 transition-colors text-steel-700 dark:text-steel-300" @click="nextPeriod">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <!-- CALENDAR VIEW -->
        <template v-if="workoutsView === 'calendar' && !selectedDate">
          <MonthCalendar
            v-if="granularity === 'month'"
            :year="currentYear"
            :month="currentMonth"
            :items-for="dayItems"
            :selected="selectedDate"
            @select="selectDay"
          />

          <!-- Week columns -->
          <template v-else-if="granularity === 'week'">
            <div class="grid grid-cols-7 mb-1.5">
              <div v-for="day in weekDaysArr" :key="day.dateStr" class="text-center py-1">
                <div class="text-xs font-medium text-steel-700 dark:text-steel-300">{{ weekDayShort(day.date) }}</div>
              </div>
            </div>
            <div class="grid grid-cols-7 gap-px rounded-2xl overflow-hidden bg-steel-100 dark:bg-steel-700 border border-steel-100 dark:border-steel-700">
              <button
                v-for="day in weekDaysArr"
                :key="day.dateStr"
                :class="cellClass(day, selectedDate)"
                class="min-h-[220px] p-1.5 flex flex-col items-stretch text-left"
                @click="selectDay(day)"
              >
                <span :class="dayNumberClass(day, todayStr)">{{ day.date.getDate() }}</span>
                <div class="flex-1 flex flex-col gap-1 mt-1.5 overflow-y-auto">
                  <span
                    v-for="(item, i) in dayItems(day.dateStr)" :key="i"
                    :class="['text-[10px] leading-snug px-1.5 py-1 rounded', chipClass(item)]"
                  >{{ item.label }}</span>
                </div>
              </button>
            </div>
          </template>

          <!-- Year: mini-months -->
          <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div v-for="m in 12" :key="m" class="card p-2.5">
              <p class="text-xs font-display font-semibold text-center text-ink dark:text-steel-100 mb-1.5 capitalize">{{ miniMonthLabel(m - 1) }}</p>
              <div class="grid grid-cols-7 gap-[3px] mb-1">
                <span v-for="(d, i) in weekDaysNarrow" :key="i" class="text-[8px] text-center text-steel-300 dark:text-steel-700">{{ d }}</span>
              </div>
              <div class="grid grid-cols-7 gap-[3px]">
                <button
                  v-for="(day, i) in miniMonthDays(m - 1)" :key="i"
                  :class="['aspect-square rounded-sm text-[9px] flex items-center justify-center transition-colors',
                    !day.inMonth ? 'invisible' : miniDayClass(day.dateStr)]"
                  :disabled="!day.inMonth"
                  @click="day.inMonth && selectDay(day)"
                >{{ day.inMonth ? day.date.getDate() : '' }}</button>
              </div>
            </div>
          </div>
        </template>

        <!-- DAY DRILL-DOWN -->
        <template v-else-if="workoutsView === 'calendar' && selectedDate">
          <button
            class="flex items-center gap-1 text-sm font-medium text-steel-700 dark:text-steel-300 hover:text-primary transition-colors -ml-1 mb-3"
            @click="selectedDate = null"
          >
            <ChevronLeft class="w-4 h-4" /> Назад к календарю
          </button>
          <h3 class="text-lg font-bold text-ink dark:text-white capitalize mb-3">{{ selectedDateLabel }}</h3>
          <div v-if="(workoutsByDate[selectedDate] || []).length" class="space-y-3">
            <PublicWorkoutCard v-for="w in workoutsByDate[selectedDate]" :key="w.id" :workout="w" />
          </div>
          <BaseEmptyState v-else title="В этот день ничего нет" description="В этот день тренировок не было">
            <template #icon><CalendarDays class="w-12 h-12" /></template>
          </BaseEmptyState>
        </template>

        <!-- LIST VIEW -->
        <template v-else>
          <div v-if="periodLoading && !periodWorkouts.length" class="space-y-3">
            <div v-for="i in 4" :key="i" class="card p-4 animate-pulse">
              <div class="h-4 bg-steel-100 dark:bg-steel-700 rounded w-3/4 mb-2" />
              <div class="h-3 bg-steel-50 dark:bg-steel-700/60 rounded w-1/2" />
            </div>
          </div>
          <BaseEmptyState
            v-else-if="!periodWorkouts.length"
            title="Нет тренировок"
            description="У этого пользователя нет записей за выбранный период"
          >
            <template #icon><Dumbbell class="w-10 h-10" /></template>
          </BaseEmptyState>
          <div v-else class="space-y-3">
            <PublicWorkoutCard v-for="w in periodWorkoutsSorted" :key="w.id" :workout="w" />
          </div>
        </template>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-400">Пользователь не найден</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import PublicProfileCoachBar from '@/components/coach/PublicProfileCoachBar.vue'
import MonthCalendar from '@/components/calendar/MonthCalendar.vue'
import { cellClass, dayNumberClass, chipClass, toDateStr } from '@/components/calendar/calendarStyles.js'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { ChevronLeft, ChevronRight, CalendarDays, List, Dumbbell, Flame, Medal, Target, Lock } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ActivityHeatmap from '@/components/profile/ActivityHeatmap.vue'
import PublicWorkoutCard from '@/components/social/PublicWorkoutCard.vue'
import workoutService from '@/services/workoutService.js'

const store = useStore()
const route = useRoute()

const loading = ref(false)
const followLoading = ref(false)
const activityLoading = ref(false)
const maxesLoading = ref(false)
const goalsLoading = ref(false)
const achievementsLoading = ref(false)

const activity = ref([])
const maxes = ref([])
const goals = ref([])
const achievements = ref([])

const activeTab = ref('profile')
const tabs = [
  { id: 'profile', label: 'Профиль' },
  { id: 'workouts', label: 'Тренировки' },
]

const userId = computed(() => Number(route.params.id))
const currentUserId = computed(() => store.state.auth.userId)
const isSelf = computed(() => userId.value === currentUserId.value)
const profile = computed(() => store.state.social.profiles[userId.value] ?? null)

async function loadProfile(uid) {
  resetWorkoutsCalendar()

  loading.value = true
  try {
    await store.dispatch('social/getProfile', uid)
  } finally {
    loading.value = false
  }

  activityLoading.value = true
  maxesLoading.value = true
  goalsLoading.value = true
  achievementsLoading.value = true

  await Promise.allSettled([
    workoutService.fetchUserActivity(uid).then(d => { activity.value = d }).finally(() => { activityLoading.value = false }),
    workoutService.fetchUserMaxes(uid).then(d => { maxes.value = d }).finally(() => { maxesLoading.value = false }),
    workoutService.fetchUserGoals(uid).then(d => { goals.value = d }).finally(() => { goalsLoading.value = false }),
    workoutService.fetchUserAchievements(uid).then(d => { achievements.value = d }).finally(() => { achievementsLoading.value = false }),
  ])
}

// A noun-like adjective: "1 подопечный", but "2 / 5 подопечных".
const athletesWord = computed(() => {
  const n = profile.value?.athletesCount ?? 0
  return n % 10 === 1 && n % 100 !== 11 ? 'подопечный' : 'подопечных'
})

function formatShortDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function reloadProfile() {
  return store.dispatch('social/getProfile', userId.value)
}

async function toggleFollow() {
  if (!profile.value) return
  followLoading.value = true
  try {
    if (profile.value.isFollowing) {
      await store.dispatch('social/unfollow', userId.value)
    } else {
      await store.dispatch('social/follow', userId.value)
    }
    await store.dispatch('social/getProfile', userId.value)
  } finally {
    followLoading.value = false
  }
}

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

// --- Workouts tab: calendar/list with week/month/year granularity, mirroring
// HistoryView's layout — period-cached so a profile with a large history is
// paged through instead of loaded all at once ---
const workoutsView = ref('calendar')
const granularityOptions = [
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'year', label: 'Год' },
]
const granularity = ref('month')
const anchorDate = ref(new Date())
const selectedDate = ref(null)
const periodLoading = ref(false)
const monthCache = reactive({}) // { 'YYYY-MM': { status: 'loading'|'loaded', workouts: [] } }

watch(userId, loadProfile, { immediate: true })

function switchWorkoutsView(mode) { workoutsView.value = mode; selectedDate.value = null }
function setGranularity(g) { granularity.value = g; selectedDate.value = null }

function resetWorkoutsCalendar() {
  for (const key in monthCache) delete monthCache[key]
  granularity.value = 'month'
  anchorDate.value = new Date()
  selectedDate.value = null
}

function prevPeriod() {
  selectedDate.value = null
  const d = new Date(anchorDate.value)
  if (granularity.value === 'week') d.setDate(d.getDate() - 7)
  else if (granularity.value === 'month') d.setMonth(d.getMonth() - 1)
  else d.setFullYear(d.getFullYear() - 1)
  anchorDate.value = d
}
function nextPeriod() {
  selectedDate.value = null
  const d = new Date(anchorDate.value)
  if (granularity.value === 'week') d.setDate(d.getDate() + 7)
  else if (granularity.value === 'month') d.setMonth(d.getMonth() + 1)
  else d.setFullYear(d.getFullYear() + 1)
  anchorDate.value = d
}

const currentYear = computed(() => anchorDate.value.getFullYear())
const currentMonth = computed(() => anchorDate.value.getMonth())
const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value, 1).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
)
const periodLabel = computed(() => {
  if (granularity.value === 'week') {
    const days = weekDaysArr.value
    const start = days[0].date
    const end = days[6].date
    const sameMonth = start.getMonth() === end.getMonth()
    const startStr = start.toLocaleDateString('ru-RU', { day: 'numeric', month: sameMonth ? undefined : 'long' })
    const endStr = end.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    return `${startStr} – ${endStr}`
  }
  if (granularity.value === 'year') return String(currentYear.value)
  return monthLabel.value
})

const todayStr = toDateStr(new Date())

function monthKey(year, monthIndex) {
  return `${year}-${String(monthIndex + 1).padStart(2, '0')}`
}
function monthDateRange(year, monthIndex) {
  const from = `${year}-${String(monthIndex + 1).padStart(2, '0')}-01`
  const lastDay = new Date(year, monthIndex + 1, 0).getDate()
  const to = `${year}-${String(monthIndex + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
  return { from, to }
}

function ensureMonth(uid, year, monthIndex) {
  const key = monthKey(year, monthIndex)
  const existing = monthCache[key]
  if (existing) return existing.status === 'loading' ? existing.promise : Promise.resolve()

  const { from, to } = monthDateRange(year, monthIndex)
  const entry = reactive({ status: 'loading', workouts: [] })
  monthCache[key] = entry
  entry.promise = workoutService.fetchUserWorkouts(uid, { from, to })
    .then(ws => { entry.workouts = ws; entry.status = 'loaded' })
    .catch(() => { delete monthCache[key] }) // allow retry on next visit
  return entry.promise
}

// --- Week row (granularity === 'week') ---
const weekDaysArr = computed(() => {
  const d = new Date(anchorDate.value)
  const dow = (d.getDay() + 6) % 7
  const monday = new Date(d)
  monday.setDate(d.getDate() - dow)
  return Array.from({ length: 7 }, (_, i) => {
    const dt = new Date(monday)
    dt.setDate(monday.getDate() + i)
    return { date: dt, isCurrentMonth: true, dateStr: toDateStr(dt) }
  })
})

function weekDayShort(date) {
  return date.toLocaleDateString('ru-RU', { weekday: 'short' })
}

function monthsForCurrentView() {
  if (granularity.value === 'week') {
    const set = new Set(weekDaysArr.value.map(d => `${d.date.getFullYear()}:${d.date.getMonth()}`))
    return [...set].map(s => s.split(':').map(Number))
  }
  if (granularity.value === 'year') {
    return Array.from({ length: 12 }, (_, m) => [currentYear.value, m])
  }
  return [[currentYear.value, currentMonth.value]]
}

async function loadCurrentPeriod() {
  const uid = userId.value
  const months = monthsForCurrentView()
  periodLoading.value = true
  try {
    await Promise.all(months.map(([y, m]) => ensureMonth(uid, y, m)))
  } finally {
    periodLoading.value = false
  }
  // Prefetch neighboring months in the background so paging feels instant —
  // skipped for year view (would mean fetching a whole extra year just in case).
  if (granularity.value !== 'year') {
    const prev = new Date(currentYear.value, currentMonth.value - 1, 1)
    const next = new Date(currentYear.value, currentMonth.value + 1, 1)
    ensureMonth(uid, prev.getFullYear(), prev.getMonth())
    ensureMonth(uid, next.getFullYear(), next.getMonth())
  }
}

watch([granularity, anchorDate], loadCurrentPeriod, { immediate: true })

const cachedWorkouts = computed(() =>
  Object.values(monthCache).filter(e => e.status === 'loaded').flatMap(e => e.workouts)
)
const workoutsByDate = computed(() => {
  const map = {}
  for (const w of cachedWorkouts.value) {
    if (!map[w.date]) map[w.date] = []
    map[w.date].push(w)
  }
  return map
})

function volumeOf(w) {
  return w.exercises.reduce((s, ex) => s + ex.sets.reduce((ss, set) => ss + set.weight * set.reps, 0), 0)
}

// --- Period-aware aggregates (drive the stats row + list view, across all granularities) ---
const periodWorkouts = computed(() => {
  if (granularity.value === 'week') {
    const set = new Set(weekDaysArr.value.map(d => d.dateStr))
    return cachedWorkouts.value.filter(w => set.has(w.date))
  }
  if (granularity.value === 'year') {
    const prefix = `${currentYear.value}-`
    return cachedWorkouts.value.filter(w => w.date.startsWith(prefix))
  }
  const prefix = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`
  return cachedWorkouts.value.filter(w => w.date.startsWith(prefix))
})
const periodWorkoutsSorted = computed(() =>
  [...periodWorkouts.value].sort((a, b) => b.date.localeCompare(a.date))
)

const periodTotalVolume = computed(() => {
  const v = periodWorkouts.value.reduce((sum, w) => sum + volumeOf(w), 0)
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v + ' кг'
})
const periodTotalDuration = computed(() => {
  const mins = periodWorkouts.value.reduce((sum, w) => sum + (w.durationMinutes || 0), 0)
  return (mins / 60).toFixed(1)
})

// Calendar chips: this profile only shows done workouts, tinted by type.
function dayItems(dateStr) {
  return (workoutsByDate.value[dateStr] || []).map(w => ({ label: w.title || w.type, kind: 'workout', type: w.type }))
}

// Segmented control, same as everywhere else in the app.
function segClass(active) {
  return active
    ? 'bg-card text-primary shadow-soft dark:bg-steel-700'
    : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white'
}

// --- Year: mini-months (granularity === 'year') ---
const weekDaysNarrow = ['П', 'В', 'С', 'Ч', 'П', 'С', 'В']

function miniMonthLabel(monthIndex) {
  return new Date(currentYear.value, monthIndex, 1).toLocaleDateString('ru-RU', { month: 'long' })
}

function miniMonthDays(monthIndex) {
  const year = currentYear.value
  const firstDay = new Date(year, monthIndex, 1)
  const lastDay = new Date(year, monthIndex + 1, 0)
  const startOffset = (firstDay.getDay() + 6) % 7

  const days = []
  for (let i = 0; i < startOffset; i++) days.push({ inMonth: false })
  for (let n = 1; n <= lastDay.getDate(); n++) {
    const d = new Date(year, monthIndex, n)
    days.push({ date: d, inMonth: true, isCurrentMonth: true, dateStr: toDateStr(d) })
  }
  while (days.length < 42) days.push({ inMonth: false })
  return days
}

function miniDayClass(dateStr) {
  const isSelected = dateStr === selectedDate.value
  const isToday = dateStr === todayStr
  if (isSelected) return 'bg-primary text-white font-bold'
  const hasWorkout = (workoutsByDate.value[dateStr] || []).length > 0
  const tone = hasWorkout ? 'bg-primary/15 dark:bg-primary/25 text-primary font-semibold' : 'text-steel-700 dark:text-steel-300'
  if (isToday) return `${tone} ring-1 ring-primary`
  return tone
}

function selectDay(day) {
  if (!day.isCurrentMonth) return
  selectedDate.value = selectedDate.value === day.dateStr ? null : day.dateStr
}

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  return new Date(selectedDate.value + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
})
</script>
