<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">История</h2>
      <div class="flex items-center gap-2">
        <!-- Export button -->
        <button
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400"
          title="Экспорт"
          @click="exportModalOpen = true"
        ><Download class="w-4 h-4" /></button>
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
    </div>

    <!-- Granularity toggle -->
    <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 mb-5 w-fit">
      <button
        v-for="g in granularityOptions" :key="g.value"
        :class="['px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
          granularity === g.value ? 'bg-white dark:bg-gray-700 shadow-sm text-primary' : 'text-gray-500']"
        @click="setGranularity(g.value)"
      >{{ g.label }}</button>
    </div>

    <!-- Period stats (shared) -->
    <div class="grid grid-cols-3 gap-3 mb-5">
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-primary">{{ periodWorkouts.length }}</div>
        <div class="text-xs text-gray-400 mt-0.5">тренировок</div>
      </div>
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-gray-900 dark:text-white">{{ periodTotalVolume }}</div>
        <div class="text-xs text-gray-400 mt-0.5">тоннаж</div>
      </div>
      <div class="card p-3 text-center">
        <div class="text-xl font-bold text-gray-900 dark:text-white">{{ periodTotalDuration }}</div>
        <div class="text-xs text-gray-400 mt-0.5">часов</div>
      </div>
    </div>

    <!-- Period navigation -->
    <div class="flex items-center gap-2 mb-5">
      <button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="prevPeriod">
        <ChevronLeft class="w-4 h-4" />
      </button>
      <div class="flex-1 text-center">
        <span class="text-base font-semibold text-gray-900 dark:text-white capitalize">{{ periodLabel }}</span>
      </div>
      <button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400" @click="nextPeriod">
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>

    <!-- CALENDAR VIEW -->
    <template v-if="viewMode === 'calendar'">
      <!-- Month grid -->
      <template v-if="granularity === 'month'">
        <div class="grid grid-cols-7 mb-1.5">
          <div v-for="d in weekDays" :key="d" class="text-center text-xs font-medium text-gray-400 dark:text-gray-500 py-1">{{ d }}</div>
        </div>

        <div class="grid grid-cols-7 gap-px bg-gray-200 dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800">
          <button
            v-for="day in calendarDays"
            :key="day.dateStr"
            :class="cellClass(day)"
            class="min-h-[74px] sm:min-h-[92px] p-1 sm:p-1.5 flex flex-col items-stretch text-left"
            @click="selectDay(day)"
          >
            <span :class="dayNumberClass(day)">{{ day.date.getDate() }}</span>
            <div class="flex-1 flex flex-col gap-0.5 mt-1 overflow-hidden">
              <span
                v-for="(item, i) in dayItems(day.dateStr).slice(0, 2)" :key="i"
                :class="['text-[9px] leading-tight px-1 py-0.5 rounded truncate', chipClass(item)]"
              >{{ item.label }}</span>
              <span v-if="dayItems(day.dateStr).length > 2" class="text-[9px] text-gray-400 dark:text-gray-500 px-1">
                +{{ dayItems(day.dateStr).length - 2 }} ещё
              </span>
            </div>
          </button>
        </div>
      </template>

      <!-- Week columns -->
      <template v-else-if="granularity === 'week'">
        <div class="grid grid-cols-7 mb-1.5">
          <div v-for="day in weekDaysArr" :key="day.dateStr" class="text-center py-1">
            <div class="text-xs font-medium text-gray-400 dark:text-gray-500">{{ weekDayShort(day.date) }}</div>
          </div>
        </div>

        <div class="grid grid-cols-7 gap-px bg-gray-200 dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800">
          <button
            v-for="day in weekDaysArr"
            :key="day.dateStr"
            :class="cellClass(day)"
            class="min-h-[220px] p-1.5 flex flex-col items-stretch text-left"
            @click="selectDay(day)"
          >
            <span :class="dayNumberClass(day)">{{ day.date.getDate() }}</span>
            <div class="flex-1 flex flex-col gap-1 mt-1.5 overflow-y-auto">
              <span
                v-for="(item, i) in dayItems(day.dateStr)" :key="i"
                :class="['text-[10px] leading-snug px-1.5 py-1 rounded', chipClass(item)]"
              >{{ item.label }}</span>
            </div>
            <span
              v-if="dayVolume(day.dateStr) > 0"
              :class="['text-[10px] font-medium text-center mt-1.5 pt-1.5 border-t', selectedDate === day.dateStr ? 'border-white/20 text-white/90' : 'border-gray-100 dark:border-gray-800 text-gray-500 dark:text-gray-400']"
            >{{ formatVolumeShort(dayVolume(day.dateStr)) }}</span>
          </button>
        </div>
      </template>

      <!-- Year: mini-months -->
      <template v-else>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div v-for="m in 12" :key="m" class="card p-2.5">
            <p class="text-xs font-semibold text-center text-gray-700 dark:text-gray-200 mb-1.5 capitalize">{{ miniMonthLabel(m - 1) }}</p>
            <div class="grid grid-cols-7 gap-[3px] mb-1">
              <span v-for="d in weekDaysNarrow" :key="d" class="text-[8px] text-center text-gray-300 dark:text-gray-600">{{ d }}</span>
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
          <span v-if="isSearching" class="text-xs text-gray-400">По всем записям · найдено <strong class="text-gray-600 dark:text-gray-300">{{ periodCombinedItems.length }}</strong></span>
          <button v-if="hasActiveFilters" class="btn btn-ghost text-sm" @click="resetFilters">Сбросить фильтры</button>
        </div>
      </div>

      <div v-if="periodCombinedItems.length" class="space-y-3">
        <template v-for="item in periodCombinedItems" :key="item.id">
          <WorkoutCard v-if="item._kind === 'workout'" :workout="item" />
          <PlanCard v-else :plan="item" />
        </template>
      </div>
      <BaseEmptyState v-else title="Ничего нет" :description="hasActiveFilters ? 'Попробуйте изменить фильтры' : 'За этот период нет записей'">
        <template #icon><Activity class="w-12 h-12" /></template>
      </BaseEmptyState>
    </template>

    <ExportModal v-model="exportModalOpen" :workouts="allWorkouts" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { CalendarDays, List, ChevronLeft, ChevronRight, Activity, X, Clock, CheckCircle2, Ban, Plus, Download } from 'lucide-vue-next'
import WorkoutCard from '@/components/workout/WorkoutCard.vue'
import PlanCard from '@/components/workout/PlanCard.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ExportModal from '@/components/ui/ExportModal.vue'
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
const selectedDate = ref(null)

function switchView(mode) { viewMode.value = mode; selectedDate.value = null }

// --- Granularity (week / month / year) ---
const granularityOptions = [
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'year', label: 'Год' },
]
const granularity = ref('month')
const anchorDate = ref(new Date(today))

function setGranularity(g) {
  granularity.value = g
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

function volumeOf(w) {
  return w.exercises.reduce((s, ex) => s + ex.sets.reduce((ss, set) => ss + set.weight * set.reps, 0), 0)
}

function formatVolumeShort(v) {
  if (!v) return ''
  return v >= 1000 ? (v / 1000).toFixed(1) + 'т' : Math.round(v) + 'кг'
}

function dayVolume(dateStr) {
  return (workoutsByDate.value[dateStr] || []).reduce((sum, w) => sum + volumeOf(w), 0)
}

// --- Period-aware aggregates (drive the stats row + list view, across all granularities) ---
const periodWorkouts = computed(() => {
  if (granularity.value === 'week') {
    const set = new Set(weekDaysArr.value.map(d => d.dateStr))
    return allWorkouts.value.filter(w => set.has(w.date))
  }
  if (granularity.value === 'year') {
    const prefix = `${currentYear.value}-`
    return allWorkouts.value.filter(w => w.date.startsWith(prefix))
  }
  return monthWorkouts.value
})

const periodPlanned = computed(() => {
  if (granularity.value === 'week') {
    const set = new Set(weekDaysArr.value.map(d => d.dateStr))
    return allPlanned.value.filter(p => set.has(p.scheduledDate))
  }
  if (granularity.value === 'year') {
    const prefix = `${currentYear.value}-`
    return allPlanned.value.filter(p => p.scheduledDate.startsWith(prefix))
  }
  return monthPlanned.value
})

const periodTotalVolume = computed(() => {
  const v = periodWorkouts.value.reduce((sum, w) => sum + volumeOf(w), 0)
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v + ' кг'
})

const periodTotalDuration = computed(() => {
  const mins = periodWorkouts.value.reduce((sum, w) => sum + (w.durationMinutes || 0), 0)
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
  const workout = workoutsByDate.value[dateStr]?.length
  const plans = plannedByDate.value[dateStr] || []
  let tone = ''
  if (workout) tone = 'bg-primary/15 dark:bg-primary/25 text-primary font-semibold'
  else if (plans.some(p => p.status === 'completed')) tone = 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 font-semibold'
  else if (plans.some(p => p.status === 'planned')) tone = 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 font-semibold'
  else if (plans.some(p => p.status === 'skipped')) tone = 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
  else tone = 'text-gray-500 dark:text-gray-400'
  if (isToday) return `${tone} ring-1 ring-primary`
  return tone
}

// --- Shared cell chips (month + week grids) ---
const workoutChipClasses = {
  'Силовая': 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
  'Кардио': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  'Растяжка': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  'HIIT': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  'Другое': 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300',
}
// Same status-based logic as everywhere else in the app — a skipped plan
// must not read the same as an upcoming one.
const planChipClasses = {
  planned: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  completed: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  skipped: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400',
}

function dayItems(dateStr) {
  const items = []
  for (const w of (workoutsByDate.value[dateStr] || [])) {
    items.push({ label: w.title || w.type, kind: 'workout', type: w.type })
  }
  for (const p of (plannedByDate.value[dateStr] || [])) {
    items.push({ label: p.title, kind: 'plan', status: p.status })
  }
  return items
}

function chipClass(item) {
  if (item.kind === 'workout') return workoutChipClasses[item.type] || workoutChipClasses['Другое']
  return planChipClasses[item.status] || planChipClasses.planned
}

// --- Shared cell styling (month + week grids) ---
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

// List: when searching — all records; otherwise the selected period (week/month/year)
const periodCombinedItems = computed(() => {
  const baseWorkouts = isSearching.value ? [...allWorkouts.value] : [...periodWorkouts.value]
  const basePlans    = isSearching.value ? [...allPlanned.value]  : [...periodPlanned.value]
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

// --- Export ---
const exportModalOpen = ref(false)
</script>
