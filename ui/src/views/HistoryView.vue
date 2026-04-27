<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">История</h2>
      <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 gap-0.5">
        <button
          :class="['p-2 rounded-md transition-colors', viewMode === 'calendar'
            ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
            : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
          title="Календарь"
          @click="switchView('calendar')"
        ><CalendarDays class="w-4 h-4" /></button>
        <button
          :class="['p-2 rounded-md transition-colors', viewMode === 'list'
            ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
            : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
          title="Список"
          @click="switchView('list')"
        ><List class="w-4 h-4" /></button>
      </div>
    </div>

    <!-- Month stats (shared) -->
    <div class="grid grid-cols-3 gap-3 mb-5">
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-primary">{{ monthWorkouts.length }}</div>
        <div class="text-xs text-gray-400 mt-0.5">тренировок</div>
      </div>
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-gray-900 dark:text-white">{{ monthTotalVolume }}</div>
        <div class="text-xs text-gray-400 mt-0.5">тоннаж</div>
      </div>
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-gray-900 dark:text-white">{{ monthTotalDuration }}</div>
        <div class="text-xs text-gray-400 mt-0.5">часов</div>
      </div>
    </div>

    <!-- Month navigation -->
    <div class="flex items-center gap-2 mb-5">
      <button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="prevMonth">
        <ChevronLeft class="w-4 h-4" />
      </button>
      <div class="flex-1 text-center">
        <span class="text-base font-semibold text-gray-900 dark:text-white capitalize">{{ monthLabel }}</span>
      </div>
      <button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="nextMonth">
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>

    <!-- CALENDAR VIEW -->
    <template v-if="viewMode === 'calendar'">
      <div class="grid grid-cols-7 mb-1">
        <div v-for="d in weekDays" :key="d" class="text-center text-xs font-medium text-gray-400 dark:text-gray-500 py-1">{{ d }}</div>
      </div>

      <div class="grid grid-cols-7 gap-1">
        <button
          v-for="day in calendarDays"
          :key="day.dateStr"
          :class="dayClass(day)"
          @click="selectDay(day)"
        >
          <span class="text-sm leading-none">{{ day.date.getDate() }}</span>
          <div class="flex justify-center gap-0.5 mt-1 h-1.5">
            <div
              v-for="(dot, i) in dayDots(day).slice(0, 3)"
              :key="i"
              :class="['w-1.5 h-1.5 rounded-full', selectedDate === day.dateStr ? 'bg-white/80' : dot]"
            />
          </div>
        </button>
      </div>

      <!-- Selected day panel -->
      <div v-if="selectedDate" class="mt-4">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-sm font-semibold text-gray-700 dark:text-gray-300 capitalize">{{ selectedDateLabel }}</span>
          <div class="flex-1 h-px bg-gray-100 dark:bg-gray-800" />
          <button
            v-if="selectedDate >= todayStr"
            class="text-xs px-2.5 py-1 rounded-lg bg-primary text-white font-medium hover:bg-primary/90 transition-colors flex items-center gap-1"
            @click="planForDay(selectedDate)"
          >
            <Plus class="w-3 h-3" /> Запланировать
          </button>
          <button
            v-else
            class="text-xs px-2.5 py-1 rounded-lg bg-gray-700 text-white font-medium hover:bg-gray-600 transition-colors flex items-center gap-1"
            @click="addWorkoutForDay(selectedDate)"
          >
            <Plus class="w-3 h-3" /> Добавить тренировку
          </button>
          <button class="text-gray-300 hover:text-gray-500 transition-colors ml-1" @click="selectedDate = null"><X class="w-4 h-4" /></button>
        </div>

        <div v-if="selectedDayWorkouts.length || selectedDayPlanned.length" class="space-y-3">
          <WorkoutCard v-for="w in selectedDayWorkouts" :key="w.id" :workout="w" />
          <PlanCard v-for="p in selectedDayPlanned" :key="p.id" :plan="p" />
        </div>
        <div v-else class="card p-6 text-center text-sm text-gray-400">В этот день ничего нет</div>
      </div>

    </template>

    <!-- LIST VIEW -->
    <template v-else>

      <!-- Filters (list only) -->
      <div class="card p-4 mb-5 space-y-3">
        <div class="flex flex-wrap gap-2">
          <button
            :class="['text-sm px-3 py-1.5 rounded-full font-medium border transition-colors',
              !activeType ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary']"
            @click="setFilter('type', null)"
          >Все</button>
          <button
            v-for="type in workoutTypes" :key="type"
            :class="['text-sm px-3 py-1.5 rounded-full font-medium border transition-colors',
              activeType === type ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary']"
            @click="setFilter('type', type)"
          >{{ type }}</button>
        </div>
        <input :value="filters.search" placeholder="Поиск по всем записям..." class="input" @input="setFilter('search', $event.target.value)" />
        <div class="flex gap-3">
          <input type="date" :value="filters.dateFrom || ''" class="input flex-1" @input="setFilter('dateFrom', $event.target.value || null)" />
          <input type="date" :value="filters.dateTo || ''" class="input flex-1" @input="setFilter('dateTo', $event.target.value || null)" />
        </div>
        <div class="flex items-center justify-between">
          <span v-if="isSearching" class="text-xs text-gray-400">По всем записям · найдено <strong class="text-gray-600 dark:text-gray-300">{{ monthCombinedItems.length }}</strong></span>
          <button v-if="hasActiveFilters" class="btn btn-ghost text-sm" @click="resetFilters">Сбросить фильтры</button>
        </div>
      </div>

      <div v-if="monthCombinedItems.length" class="space-y-3">
        <template v-for="item in monthCombinedItems" :key="item.id">
          <WorkoutCard v-if="item._kind === 'workout'" :workout="item" />
          <PlanCard v-else :plan="item" />
        </template>
      </div>
      <BaseEmptyState v-else title="Ничего нет" :description="hasActiveFilters ? 'Попробуйте изменить фильтры' : 'В этом месяце нет записей'">
        <template #icon><Activity class="w-12 h-12" /></template>
      </BaseEmptyState>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { CalendarDays, List, ChevronLeft, ChevronRight, Activity, X, Clock, CheckCircle2, Ban, Plus } from 'lucide-vue-next'
import WorkoutCard from '@/components/workout/WorkoutCard.vue'
import PlanCard from '@/components/workout/PlanCard.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import { WORKOUT_TYPES } from '@/services/mockData.js'

const store = useStore()
const router = useRouter()
const workoutTypes = WORKOUT_TYPES

onMounted(async () => {
  if (!store.state.workouts.workouts.length) await store.dispatch('workouts/initWorkouts')
  if (!store.state.planned.plannedWorkouts.length) store.dispatch('planned/fetchPlannedWorkouts')
  const ids = store.state.workouts.workouts.map(w => w.id)
  if (ids.length) store.dispatch('social/fetchWorkoutsMeta', ids)
})

// --- View state ---
const viewMode = ref('calendar')
const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())
const selectedDate = ref(null)

function switchView(mode) { viewMode.value = mode; selectedDate.value = null }

function prevMonth() {
  selectedDate.value = null
  if (currentMonth.value === 0) { currentMonth.value = 11; currentYear.value-- } else currentMonth.value--
}
function nextMonth() {
  selectedDate.value = null
  if (currentMonth.value === 11) { currentMonth.value = 0; currentYear.value++ } else currentMonth.value++
}

const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value, 1).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
)

// --- Workouts data ---
const allWorkouts = computed(() => store.getters['workouts/allWorkouts'])

const workoutsByDate = computed(() => {
  const map = {}
  for (const w of allWorkouts.value) {
    if (!map[w.date]) map[w.date] = []
    map[w.date].push(w)
  }
  return map
})

const monthWorkouts = computed(() => {
  const prefix = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`
  return allWorkouts.value.filter(w => w.date.startsWith(prefix))
})

const monthTotalVolume = computed(() => {
  const v = monthWorkouts.value.reduce((sum, w) =>
    sum + w.exercises.reduce((s, ex) => s + ex.sets.reduce((ss, set) => ss + set.weight * set.reps, 0), 0), 0)
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v + ' кг'
})

const monthTotalDuration = computed(() => {
  const mins = monthWorkouts.value.reduce((sum, w) => sum + (w.durationMinutes || 0), 0)
  return (mins / 60).toFixed(1)
})

// --- Planned data ---
const allPlanned = computed(() => store.getters['planned/all'])

const plannedByDate = computed(() => {
  const map = {}
  for (const p of allPlanned.value) {
    const d = p.scheduledDate
    if (!map[d]) map[d] = []
    map[d].push(p)
  }
  return map
})

const monthPlanned = computed(() => {
  const prefix = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`
  return allPlanned.value.filter(p => p.scheduledDate.startsWith(prefix))
})

// --- Calendar grid ---
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

function toDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const todayStr = toDateStr(today)

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

const typeDotMap = {
  'Силовая': 'bg-indigo-500', 'Кардио': 'bg-green-500',
  'Растяжка': 'bg-purple-500', 'HIIT': 'bg-orange-500', 'Другое': 'bg-gray-400',
}
function typeColorDot(type) { return typeDotMap[type] || 'bg-gray-400' }

function dayDots(day) {
  const dots = []
  for (const w of (workoutsByDate.value[day.dateStr] || [])) dots.push(typeColorDot(w.type))
  for (const p of (plannedByDate.value[day.dateStr] || [])) dots.push('bg-amber-400')
  return dots
}

function dayClass(day) {
  const base = 'flex flex-col items-center justify-center py-2 rounded-xl transition-all min-h-[44px] select-none'
  const isSelected = day.dateStr === selectedDate.value
  const isToday = day.dateStr === todayStr
  const hasWorkout = !!workoutsByDate.value[day.dateStr]?.length
  const hasPlanned = !!plannedByDate.value[day.dateStr]?.length

  if (isSelected) return `${base} bg-primary text-white shadow-sm`
  if (!day.isCurrentMonth) return `${base} opacity-25 text-gray-400 cursor-default`
  if (isToday) return `${base} ring-2 ring-primary ring-inset text-primary font-bold`
  if (hasWorkout) return `${base} bg-primary/10 dark:bg-primary/20 text-gray-900 dark:text-white font-medium hover:bg-primary/20`
  if (hasPlanned) return `${base} bg-amber-50 dark:bg-amber-900/20 text-gray-700 dark:text-gray-300 hover:bg-amber-100 dark:hover:bg-amber-900/30`
  return `${base} text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800`
}

function selectDay(day) {
  if (!day.isCurrentMonth) return
  selectedDate.value = selectedDate.value === day.dateStr ? null : day.dateStr
}

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  return new Date(selectedDate.value + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
})

// --- Filters ---
const filters = computed(() => store.state.workouts.filters)
const activeType = computed(() => filters.value.type)
const hasActiveFilters = computed(() =>
  filters.value.type || filters.value.dateFrom || filters.value.dateTo || filters.value.search
)

function applyWorkoutFilters(ws) {
  let list = ws
  if (activeType.value) list = list.filter(w => w.type === activeType.value)
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    list = list.filter(w =>
      w.title.toLowerCase().includes(q) ||
      w.exercises.some(e => e.exerciseName?.toLowerCase().includes(q))
    )
  }
  if (filters.value.dateFrom) list = list.filter(w => w.date >= filters.value.dateFrom)
  if (filters.value.dateTo) list = list.filter(w => w.date <= filters.value.dateTo)
  return list
}

function applyPlanFilters(ps) {
  let list = ps
  if (activeType.value) list = list.filter(p => p.type === activeType.value)
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    list = list.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.exercises?.some(e => e.exerciseName?.toLowerCase().includes(q))
    )
  }
  if (filters.value.dateFrom) list = list.filter(p => p.scheduledDate >= filters.value.dateFrom)
  if (filters.value.dateTo) list = list.filter(p => p.scheduledDate <= filters.value.dateTo)
  return list
}

// Calendar: selected day
const selectedDayWorkouts = computed(() => {
  if (!selectedDate.value) return []
  return applyWorkoutFilters([...(workoutsByDate.value[selectedDate.value] || [])])
})
const selectedDayPlanned = computed(() => {
  if (!selectedDate.value) return []
  return applyPlanFilters([...(plannedByDate.value[selectedDate.value] || [])])
})

const isSearching = computed(() => !!filters.value.search?.trim())

watch(isSearching, (searching) => {
  if (searching) switchView('list')
})

// List: when searching — all records; otherwise current month only
const monthCombinedItems = computed(() => {
  const baseWorkouts = isSearching.value ? [...allWorkouts.value] : [...monthWorkouts.value]
  const basePlans    = isSearching.value ? [...allPlanned.value]  : [...monthPlanned.value]
  const workouts = applyWorkoutFilters(baseWorkouts).map(w => ({ ...w, _kind: 'workout', _sortDate: w.date }))
  const plans    = applyPlanFilters(basePlans).map(p => ({ ...p, _kind: 'plan', _sortDate: p.scheduledDate }))
  return [...workouts, ...plans].sort((a, b) => b._sortDate.localeCompare(a._sortDate))
})

function setFilter(key, value) { store.commit('workouts/SET_FILTER', { key, value }) }
function resetFilters() { store.commit('workouts/RESET_FILTERS') }

function planForDay(dateStr) {
  router.push({ path: '/planning/new', query: { date: dateStr } })
}

function addWorkoutForDay(dateStr) {
  store.commit('workouts/RESET_ACTIVE_WORKOUT')
  store.commit('workouts/SET_ACTIVE_WORKOUT_FIELD', { field: 'date', value: dateStr })
  router.push('/workouts/new')
}
</script>
