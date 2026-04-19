<template>
  <div v-if="exercise">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 mt-1 transition-colors" @click="$router.back()">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ exercise.name }}</h2>
        <div class="flex flex-wrap gap-1.5 mt-2">
          <BaseBadge color="indigo">{{ exercise.muscleGroup }}</BaseBadge>
          <BaseBadge color="gray">{{ exercise.equipment }}</BaseBadge>
          <BaseBadge v-for="m in exercise.secondaryMuscles" :key="m" color="gray">{{ m }}</BaseBadge>
        </div>
        <p v-if="exercise.description" class="text-sm text-gray-600 dark:text-gray-400 mt-2">{{ exercise.description }}</p>
      </div>
    </div>

    <!-- PR Card (strength) -->
    <div v-if="pr && !isCardio" class="card p-4 mb-6 border-l-4 border-yellow-400">
      <div class="flex items-center gap-2 mb-3">
        <Trophy class="w-6 h-6 text-yellow-500" />
        <p class="text-xs text-gray-500 uppercase tracking-wide font-semibold">Личные рекорды</p>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div class="text-center">
          <p class="text-xs text-gray-400 mb-0.5">Расч. 1ПМ</p>
          <p class="text-lg font-bold text-yellow-500">{{ pr.best1RM }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.best1RMDate) }}</p>
        </div>
        <div class="text-center border-x border-gray-100 dark:border-gray-700">
          <p class="text-xs text-gray-400 mb-0.5">Лучший вес</p>
          <p class="text-lg font-bold text-primary">{{ pr.bestWeight }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.bestWeightDate) }}</p>
        </div>
        <div class="text-center">
          <p class="text-xs text-gray-400 mb-0.5">Лучший тоннаж</p>
          <p class="text-lg font-bold text-green-500">{{ pr.bestVolume }} кг</p>
          <p class="text-xs text-gray-400">{{ formatDate(pr.bestVolumeDate) }}</p>
        </div>
      </div>
    </div>

    <!-- PR Card (cardio) -->
    <div v-if="pr && isCardio" class="card p-4 mb-6 border-l-4 border-yellow-400">
      <div class="flex items-center gap-2 mb-3">
        <Trophy class="w-6 h-6 text-yellow-500" />
        <p class="text-xs text-gray-500 uppercase tracking-wide font-semibold">Личный рекорд</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-gray-400 mb-0.5">Лучшая сессия</p>
        <p class="text-lg font-bold text-yellow-500">{{ pr.bestDuration }} мин.</p>
        <p class="text-xs text-gray-400">{{ formatDate(pr.bestDurationDate) }}</p>
      </div>
    </div>

    <!-- Chart -->
    <div class="card p-4 mb-6">
      <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Прогресс</h3>
      <ProgressChart :data="progress" :is-cardio="isCardio" />
    </div>

    <!-- Sessions table -->
    <div class="card p-4">
      <!-- Header + controls -->
      <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <h3 class="font-semibold text-gray-900 dark:text-white">История сессий</h3>
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Page size -->
          <select v-model.number="pageSize" class="input py-1.5 text-xs pr-7 w-auto">
            <option :value="10">10 / стр.</option>
            <option :value="25">25 / стр.</option>
            <option :value="50">50 / стр.</option>
            <option :value="100">100 / стр.</option>
          </select>
          <!-- Toggle filters -->
          <button
            :class="['flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
              showFilters ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary']"
            @click="showFilters = !showFilters"
          >
            <Filter class="w-3.5 h-3.5" />Фильтры<span v-if="hasFilters" class="w-1.5 h-1.5 rounded-full bg-white/80 inline-block" />
          </button>
        </div>
      </div>

      <!-- Filter panel -->
      <div v-if="showFilters" class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 mb-4 space-y-3">
        <div class="flex gap-3">
          <div class="flex-1">
            <label class="label text-xs">От</label>
            <input type="date" v-model="filterDateFrom" class="input py-1.5 text-xs" />
          </div>
          <div class="flex-1">
            <label class="label text-xs">До</label>
            <input type="date" v-model="filterDateTo" class="input py-1.5 text-xs" />
          </div>
        </div>
        <div v-if="!isCardio" class="flex gap-3">
          <div class="flex-1">
            <label class="label text-xs">Тоннаж от (кг)</label>
            <input type="number" v-model.number="filterVolumeMin" min="0" placeholder="0" class="input py-1.5 text-xs" />
          </div>
          <div class="flex-1">
            <label class="label text-xs">Тоннаж до (кг)</label>
            <input type="number" v-model.number="filterVolumeMax" min="0" placeholder="∞" class="input py-1.5 text-xs" />
          </div>
        </div>
        <button v-if="hasFilters" class="text-xs text-primary hover:underline" @click="resetFilters">Сбросить фильтры</button>
      </div>

      <template v-if="filteredSessions.length">
        <!-- Stats row -->
        <div class="flex gap-4 text-xs text-gray-400 mb-3 px-1">
          <span>Всего: <strong class="text-gray-700 dark:text-gray-300">{{ filteredSessions.length }}</strong></span>
          <span v-if="!isCardio">Ср. тоннаж: <strong class="text-gray-700 dark:text-gray-300">{{ avgVolume }} кг</strong></span>
        </div>

        <!-- Table (strength) -->
        <div v-if="!isCardio" class="overflow-x-auto -mx-4">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs border-b border-gray-100 dark:border-gray-800">
                <SortTh key-name="date"   align="left"   class="pl-4 pr-2" label="Дата" />
                <th class="px-2 py-2 text-left font-medium text-gray-400 uppercase tracking-wide hidden sm:table-cell">Тренировка</th>
                <th class="px-2 py-2 text-center font-medium text-gray-400 uppercase tracking-wide">Подходы</th>
                <SortTh key-name="weight" align="right"  class="px-2"      label="Лучший" />
                <SortTh key-name="orm"    align="right"  class="px-2"      label="1ПМ" />
                <SortTh key-name="volume" align="right"  class="pr-4 pl-2" label="Тоннаж" />
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50 dark:divide-gray-800/60">
              <tr
                v-for="session in paginatedSessions" :key="session.date + session.workoutId"
                class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                @click="$router.push(`/workouts/${session.workoutId}`)"
              >
                <td class="pl-4 pr-2 py-2.5 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(session.date) }}</td>
                <td class="px-2 py-2.5 text-gray-600 dark:text-gray-400 text-xs truncate max-w-[140px] hidden sm:table-cell">{{ session.workoutTitle }}</td>
                <td class="px-2 py-2.5 text-center">
                  <span class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ session.setsCount }}</span>
                  <span v-if="session.totalSetsCount > session.setsCount" class="text-xs text-gray-400">+{{ session.totalSetsCount - session.setsCount }}✗</span>
                </td>
                <td class="px-2 py-2.5 text-right">
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">{{ session.maxWeight > 0 ? session.maxWeight : 'б/в' }}</span>
                  <span v-if="session.maxWeight > 0" class="text-xs text-gray-400"> кг×{{ session.maxWeightReps }}</span>
                </td>
                <td class="px-2 py-2.5 text-right">
                  <span class="font-semibold text-yellow-500 text-sm">{{ session.best1RM }}</span>
                  <span class="text-xs text-gray-400"> кг</span>
                </td>
                <td class="pr-4 pl-2 py-2.5 text-right">
                  <span class="font-semibold text-green-500 text-sm">{{ session.totalVolume }}</span>
                  <span class="text-xs text-gray-400"> кг</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Table (cardio) -->
        <div v-else class="overflow-x-auto -mx-4">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs border-b border-gray-100 dark:border-gray-800">
                <SortTh key-name="date"     align="left"  class="pl-4 pr-2" label="Дата" />
                <th class="px-2 py-2 text-left font-medium text-gray-400 uppercase tracking-wide hidden sm:table-cell">Тренировка</th>
                <th class="px-2 py-2 text-center font-medium text-gray-400 uppercase tracking-wide">Подходы</th>
                <SortTh key-name="duration" align="right" class="pr-4 pl-2" label="Длительность" />
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50 dark:divide-gray-800/60">
              <tr
                v-for="session in paginatedSessions" :key="session.date + session.workoutId"
                class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                @click="$router.push(`/workouts/${session.workoutId}`)"
              >
                <td class="pl-4 pr-2 py-2.5 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(session.date) }}</td>
                <td class="px-2 py-2.5 text-gray-600 dark:text-gray-400 text-xs truncate max-w-[140px] hidden sm:table-cell">{{ session.workoutTitle }}</td>
                <td class="px-2 py-2.5 text-center text-xs font-medium text-gray-700 dark:text-gray-300">{{ session.setsCount }}</td>
                <td class="pr-4 pl-2 py-2.5 text-right">
                  <span class="font-semibold text-primary text-sm">{{ session.totalMinutes }}</span>
                  <span class="text-xs text-gray-400"> мин.</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 pt-3 border-t border-gray-100 dark:border-gray-800">
          <button
            :disabled="page === 1"
            :class="['flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors',
              page === 1 ? 'text-gray-300 dark:text-gray-600 cursor-not-allowed' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800']"
            @click="page--"
          >
            <ChevronLeft class="w-4 h-4" /> Назад
          </button>

          <div class="flex items-center gap-1">
            <button
              v-for="p in pageRange" :key="p"
              :class="['w-8 h-8 rounded-lg text-sm font-medium transition-colors',
                p === page ? 'bg-primary text-white' :
                p === '…' ? 'text-gray-400 cursor-default' :
                'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800']"
              :disabled="p === '…'"
              @click="p !== '…' && (page = p)"
            >{{ p }}</button>
          </div>

          <button
            :disabled="page === totalPages"
            :class="['flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors',
              page === totalPages ? 'text-gray-300 dark:text-gray-600 cursor-not-allowed' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800']"
            @click="page++"
          >
            Вперёд <ChevronRight class="w-4 h-4" />
          </button>
        </div>
        <p class="text-xs text-gray-400 text-center mt-2">
          {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, filteredSessions.length) }} из {{ filteredSessions.length }}
        </p>
      </template>

      <BaseEmptyState v-else title="Нет данных" :description="hasFilters ? 'Попробуйте изменить фильтры' : 'Добавьте это упражнение в тренировку, чтобы отслеживать прогресс'">
        <template #icon><BarChart3 class="w-12 h-12" /></template>
      </BaseEmptyState>
    </div>
  </div>

  <div v-else class="text-center py-16 text-gray-400">Упражнение не найдено</div>
</template>

<script setup>
import { computed, ref, watch, h } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, ChevronRight, Trophy, BarChart3, Filter, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-vue-next'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ProgressChart from '@/components/exercises/ProgressChart.vue'

const route = useRoute()
const store = useStore()

const exercise = computed(() => store.getters['exercises/exerciseById'](route.params.id))
const isCardio = computed(() => exercise.value?.muscleGroup === 'Кардио')
const progress = computed(() => store.getters['exercises/progressForExercise'](route.params.id))
const pr = computed(() => store.getters['exercises/personalRecord'](route.params.id))

// ── Sort-able column header component ─────────────────────────────────────────
const SortTh = {
  props: { keyName: String, label: String, align: { default: 'left' } },
  setup(props) {
    return () => {
      const active = sortKey.value === props.keyName
      const icon = !active
        ? h(ChevronsUpDown, { class: 'w-3 h-3 opacity-30' })
        : sortDir.value === 'asc'
          ? h(ChevronUp,   { class: 'w-3 h-3 text-primary' })
          : h(ChevronDown, { class: 'w-3 h-3 text-primary' })
      const alignCls = props.align === 'right' ? 'justify-end' : 'justify-start'
      return h('th', {
        class: `py-2 cursor-pointer select-none group`,
        onClick: () => setSort(props.keyName),
      }, [
        h('div', { class: `flex items-center gap-1 ${alignCls}` }, [
          h('span', {
            class: `text-xs font-medium uppercase tracking-wide transition-colors ${active ? 'text-primary' : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}`
          }, props.label),
          icon,
        ])
      ])
    }
  }
}

// ── History filters & sort ────────────────────────────────────────────────────
const pageSize = ref(10)
const page = ref(1)
const sortKey = ref('date')
const sortDir = ref('desc')
const showFilters = ref(false)

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}
const filterDateFrom = ref('')
const filterDateTo = ref('')
const filterVolumeMin = ref(null)
const filterVolumeMax = ref(null)

const hasFilters = computed(() =>
  filterDateFrom.value || filterDateTo.value ||
  filterVolumeMin.value != null || filterVolumeMax.value != null
)

function resetFilters() {
  filterDateFrom.value = ''
  filterDateTo.value = ''
  filterVolumeMin.value = null
  filterVolumeMax.value = null
}

// Reset page when filters/sort change
watch([sortKey, sortDir, pageSize, filterDateFrom, filterDateTo, filterVolumeMin, filterVolumeMax], () => { page.value = 1 })

const filteredSessions = computed(() => {
  let list = [...progress.value]
  if (filterDateFrom.value) list = list.filter(s => s.date >= filterDateFrom.value)
  if (filterDateTo.value)   list = list.filter(s => s.date <= filterDateTo.value)
  if (!isCardio.value) {
    if (filterVolumeMin.value != null) list = list.filter(s => s.totalVolume >= filterVolumeMin.value)
    if (filterVolumeMax.value != null) list = list.filter(s => s.totalVolume <= filterVolumeMax.value)
  }
  const d = sortDir.value === 'asc' ? 1 : -1
  list.sort((a, b) => {
    switch (sortKey.value) {
      case 'date':     return d * a.date.localeCompare(b.date)
      case 'volume':   return d * (a.totalVolume - b.totalVolume)
      case 'weight':   return d * (a.maxWeight - b.maxWeight)
      case 'orm':      return d * (a.best1RM - b.best1RM)
      case 'duration': return d * ((a.totalMinutes || 0) - (b.totalMinutes || 0))
      default:         return -a.date.localeCompare(b.date)
    }
  })
  return list
})

const totalPages = computed(() => Math.ceil(filteredSessions.value.length / pageSize.value))

const paginatedSessions = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredSessions.value.slice(start, start + pageSize.value)
})

const avgVolume = computed(() => {
  if (!filteredSessions.value.length) return 0
  const sum = filteredSessions.value.reduce((s, x) => s + (x.totalVolume || 0), 0)
  return Math.round(sum / filteredSessions.value.length)
})

const pageRange = computed(() => {
  const total = totalPages.value
  const cur = page.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = new Set([1, total, cur, cur - 1, cur + 1].filter(p => p >= 1 && p <= total))
  const sorted = [...pages].sort((a, b) => a - b)
  const result = []
  for (let i = 0; i < sorted.length; i++) {
    if (i > 0 && sorted[i] - sorted[i - 1] > 1) result.push('…')
    result.push(sorted[i])
  }
  return result
})

function formatDate(date) {
  return new Date(date + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
