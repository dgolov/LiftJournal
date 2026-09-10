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
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 dark:border-gray-800 mb-5">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
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

      <!-- TAB: Workouts -->
      <div v-else-if="activeTab === 'workouts'">
        <!-- View toggle + month nav -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 gap-0.5">
            <button
              :class="['p-2 rounded-md transition-colors', workoutsView === 'calendar'
                ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
              title="Календарь"
              @click="switchWorkoutsView('calendar')"
            ><CalendarDays class="w-4 h-4" /></button>
            <button
              :class="['p-2 rounded-md transition-colors', workoutsView === 'list'
                ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
              title="Список"
              @click="switchWorkoutsView('list')"
            ><List class="w-4 h-4" /></button>
          </div>
          <div v-if="!selectedDate" class="flex items-center gap-1">
            <button class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="prevMonth">
              <ChevronLeft class="w-4 h-4" />
            </button>
            <span class="text-sm font-semibold text-gray-900 dark:text-white capitalize min-w-[8.5rem] text-center">
              {{ monthLabel }}<span v-if="monthLoading" class="text-xs text-gray-400 font-normal"> · загрузка…</span>
            </span>
            <button class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="nextMonth">
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- CALENDAR -->
        <template v-if="workoutsView === 'calendar' && !selectedDate">
          <div class="grid grid-cols-7 mb-1.5">
            <div v-for="d in weekDays" :key="d" class="text-center text-xs font-medium text-gray-400 dark:text-gray-500 py-1">{{ d }}</div>
          </div>
          <div class="grid grid-cols-7 gap-px bg-gray-200 dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800">
            <button
              v-for="day in calendarDays"
              :key="day.dateStr"
              :class="cellClass(day)"
              class="min-h-[74px] sm:min-h-[92px] p-1 sm:p-1.5 flex flex-col items-stretch text-left"
              @click="day.isCurrentMonth && (selectedDate = day.dateStr)"
            >
              <span :class="dayNumberClass(day)">{{ day.date.getDate() }}</span>
              <div class="flex-1 flex flex-col gap-0.5 mt-1 overflow-hidden">
                <span
                  v-for="(w, i) in (workoutsByDate[day.dateStr] || []).slice(0, 2)" :key="i"
                  :class="['text-[9px] leading-tight px-1 py-0.5 rounded truncate', chipClass(w)]"
                >{{ w.title || w.type }}</span>
                <span v-if="(workoutsByDate[day.dateStr] || []).length > 2" class="text-[9px] text-gray-400 dark:text-gray-500 px-1">
                  +{{ workoutsByDate[day.dateStr].length - 2 }} ещё
                </span>
              </div>
            </button>
          </div>
        </template>

        <!-- DAY DRILL-DOWN -->
        <template v-else-if="workoutsView === 'calendar' && selectedDate">
          <button
            class="flex items-center gap-1 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors -ml-1 mb-3"
            @click="selectedDate = null"
          >
            <ChevronLeft class="w-4 h-4" /> Назад к календарю
          </button>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white capitalize mb-3">{{ selectedDateLabel }}</h3>
          <div v-if="(workoutsByDate[selectedDate] || []).length" class="space-y-3">
            <PublicWorkoutCard v-for="w in workoutsByDate[selectedDate]" :key="w.id" :workout="w" />
          </div>
          <BaseEmptyState v-else title="В этот день ничего нет" description="У пользователя нет тренировок в этот день">
            <template #icon><CalendarDays class="w-12 h-12" /></template>
          </BaseEmptyState>
        </template>

        <!-- LIST -->
        <template v-else>
          <div v-if="monthLoading && !monthWorkouts.length" class="space-y-3">
            <div v-for="i in 4" :key="i" class="card p-4 animate-pulse">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
              <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
            </div>
          </div>
          <BaseEmptyState
            v-else-if="!monthWorkouts.length"
            title="Нет тренировок"
            description="У этого пользователя нет записей за выбранный месяц"
          >
            <template #icon><Dumbbell class="w-10 h-10" /></template>
          </BaseEmptyState>
          <div v-else class="space-y-3">
            <PublicWorkoutCard v-for="w in monthWorkouts" :key="w.id" :workout="w" />
          </div>
        </template>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-400">Пользователь не найден</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { ChevronLeft, ChevronRight, CalendarDays, List, Dumbbell, Flame, Medal, Target } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ActivityHeatmap from '@/components/social/ActivityHeatmap.vue'
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

// The route stays on the same component when navigating from one public
// profile to another (e.g. clicking a follower inside this same view), so
// everything below is keyed off `userId` via a watcher, not onMounted.
watch(userId, loadProfile, { immediate: true })

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
    loadMonth(),
  ])
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

// --- Workouts tab: calendar/list, month-scoped so a profile with a large
// history is paged through month-by-month instead of loaded all at once ---
const workoutsView = ref('calendar')
const anchorDate = ref(new Date())
const selectedDate = ref(null)
const monthLoading = ref(false)
const monthCache = reactive({}) // { 'YYYY-MM': { status: 'loading'|'loaded', workouts: [] } }

function switchWorkoutsView(mode) { workoutsView.value = mode; selectedDate.value = null }

function resetWorkoutsCalendar() {
  for (const key in monthCache) delete monthCache[key]
  anchorDate.value = new Date()
  selectedDate.value = null
}

const currentYear = computed(() => anchorDate.value.getFullYear())
const currentMonth = computed(() => anchorDate.value.getMonth())
const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value, 1).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
)

function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
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

async function loadMonth() {
  const uid = userId.value
  monthLoading.value = true
  try {
    await ensureMonth(uid, currentYear.value, currentMonth.value)
  } finally {
    monthLoading.value = false
  }
  // Prefetch neighboring months in the background so paging feels instant
  const prev = new Date(currentYear.value, currentMonth.value - 1, 1)
  const next = new Date(currentYear.value, currentMonth.value + 1, 1)
  ensureMonth(uid, prev.getFullYear(), prev.getMonth())
  ensureMonth(uid, next.getFullYear(), next.getMonth())
}

function prevMonth() {
  selectedDate.value = null
  const d = new Date(anchorDate.value)
  d.setMonth(d.getMonth() - 1)
  anchorDate.value = d
  loadMonth()
}
function nextMonth() {
  selectedDate.value = null
  const d = new Date(anchorDate.value)
  d.setMonth(d.getMonth() + 1)
  anchorDate.value = d
  loadMonth()
}

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
const monthWorkouts = computed(() => {
  const prefix = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`
  return cachedWorkouts.value.filter(w => w.date.startsWith(prefix))
})

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startOffset = (firstDay.getDay() + 6) % 7

  const days = []
  for (let i = 0; i < startOffset; i++) {
    const d = new Date(year, month, 1 - startOffset + i)
    days.push({ date: d, isCurrentMonth: false, dateStr: toDateStr(d) })
  }
  for (let n = 1; n <= lastDay.getDate(); n++) {
    const d = new Date(year, month, n)
    days.push({ date: d, isCurrentMonth: true, dateStr: toDateStr(d) })
  }
  const tail = (7 - days.length % 7) % 7
  for (let i = 1; i <= tail; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ date: d, isCurrentMonth: false, dateStr: toDateStr(d) })
  }
  return days
})

const workoutChipClasses = {
  'Силовая': 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
  'Кардио': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  'Растяжка': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  'HIIT': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  'Другое': 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300',
}
function chipClass(w) { return workoutChipClasses[w.type] || workoutChipClasses['Другое'] }

function cellClass(day) {
  const isSelected = day.dateStr === selectedDate.value
  const isOtherMonth = !day.isCurrentMonth
  if (isSelected) return 'bg-primary/10 dark:bg-primary/15'
  if (isOtherMonth) return 'bg-gray-50 dark:bg-gray-900/40'
  return 'bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800/60 transition-colors'
}
function dayNumberClass(day) {
  const isToday = day.dateStr === todayStr
  const isOtherMonth = !day.isCurrentMonth
  const base = 'w-5 h-5 flex items-center justify-center rounded-full text-xs flex-shrink-0'
  if (isToday) return `${base} bg-primary text-white font-bold`
  if (isOtherMonth) return `${base} text-gray-300 dark:text-gray-700`
  return `${base} text-gray-600 dark:text-gray-300`
}

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  return new Date(selectedDate.value + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
})
</script>
