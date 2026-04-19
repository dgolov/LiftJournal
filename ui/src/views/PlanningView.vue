<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Планирование</h2>
      <RouterLink to="/planning/new" class="btn btn-primary text-sm px-4 py-2">+ Запланировать</RouterLink>
    </div>

    <!-- Filter chips -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm font-medium transition-all duration-200',
          activeTab === tab.value ? tab.activeClass : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700']"
        @click="activeTab = tab.value"
      >
        <component :is="tab.icon" :class="['w-3.5 h-3.5', activeTab === tab.value ? '' : 'opacity-60']" />
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">Загрузка...</div>

    <div v-else-if="!grouped.length">
      <BaseEmptyState
        title="Нет запланированных тренировок"
        :description="emptyDescription"
      >
        <template #icon><CalendarDays class="w-12 h-12" /></template>
        <RouterLink v-if="activeTab === 'planned'" to="/planning/new" class="mt-4 btn btn-primary">
          Запланировать тренировку
        </RouterLink>
      </BaseEmptyState>
    </div>

    <div v-else class="space-y-6">
      <div v-for="group in grouped" :key="group.date">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-sm font-semibold text-gray-500 dark:text-gray-400">{{ group.label }}</span>
          <div class="flex-1 h-px bg-gray-100 dark:bg-gray-800" />
        </div>

        <div class="space-y-3">
          <div
            v-for="plan in group.items"
            :key="plan.id"
            class="card p-4"
          >
            <div class="flex items-start gap-3">
              <!-- Status icon -->
              <div :class="['w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5', statusIcon(plan).bg]">
                <component :is="statusIcon(plan).icon" class="w-4 h-4" :class="statusIcon(plan).color" />
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap mb-0.5">
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', statusBadge(plan).class]">
                    {{ statusBadge(plan).label }}
                  </span>
                  <span class="text-xs text-gray-400">{{ plan.type }}</span>
                </div>
                <h3 class="font-semibold text-gray-900 dark:text-white line-clamp-2">{{ plan.title }}</h3>
                <p v-if="plan.exercises.length" class="text-xs text-gray-400 mt-0.5 whitespace-nowrap">
                  {{ plan.exercises.length }} упр. · {{ totalSets(plan) }} подходов
                </p>
                <p v-if="plan.notes" class="text-xs text-gray-500 mt-1 italic line-clamp-1">{{ plan.notes }}</p>

                <!-- Actions row -->
                <div class="flex items-center gap-1 mt-2">
                  <template v-if="plan.status === 'planned'">
                    <button
                      class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded-lg hover:bg-primary/90 transition-colors"
                      @click="startPlan(plan)"
                    >Начать</button>
                    <button
                      class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-gray-500 transition-colors"
                      title="Редактировать"
                      @click="$router.push(`/planning/${plan.id}/edit`)"
                    >
                      <Pencil class="w-4 h-4" />
                    </button>
                    <button
                      class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
                      title="Пропустить"
                      @click="skipPlan(plan)"
                    >
                      <Ban class="w-4 h-4" />
                    </button>
                  </template>
                  <template v-else-if="plan.status === 'completed' && plan.completedWorkoutId">
                    <RouterLink
                      :to="`/workouts/${plan.completedWorkoutId}`"
                      class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 text-xs font-medium rounded-lg hover:border-primary hover:text-primary transition-colors"
                    >Открыть</RouterLink>
                  </template>
                  <button
                    class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
                    @click="deletePlan(plan)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Exercises preview -->
            <div v-if="plan.exercises.length && plan.status === 'planned'" class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex flex-wrap gap-x-3 gap-y-1">
              <span
                v-for="ex in plan.exercises"
                :key="ex.exerciseId"
                class="text-xs text-gray-500 dark:text-gray-400"
              >· {{ ex.exerciseName }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <BaseModal v-model="showDeleteConfirm" title="Удалить план?" max-width="sm">
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">«{{ toDelete?.title }}»</p>
      <template v-if="toDelete?.recurrenceGroupId">
        <div class="space-y-2">
          <button
            :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
              deleteScope === 'one' ? 'border-primary bg-primary/5' : 'border-gray-200 dark:border-gray-700']"
            @click="deleteScope = 'one'"
          >
            <p class="font-medium text-gray-900 dark:text-white">Только эту тренировку</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ toDelete?.scheduledDate }}</p>
          </button>
          <button
            :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
              deleteScope === 'all' ? 'border-red-400 bg-red-50 dark:bg-red-900/10' : 'border-gray-200 dark:border-gray-700']"
            @click="deleteScope = 'all'"
          >
            <p class="font-medium text-gray-900 dark:text-white">Эту и все следующие</p>
            <p class="text-xs text-gray-400 mt-0.5">Удалит все запланированные повторения</p>
          </button>
        </div>
      </template>
      <template v-else>
        <p class="text-sm text-gray-500 dark:text-gray-400">Будет удалён безвозвратно.</p>
      </template>
      <template #footer>
        <BaseButton variant="ghost" @click="showDeleteConfirm = false">Отмена</BaseButton>
        <BaseButton variant="danger" @click="doDelete">Удалить</BaseButton>
      </template>
    </BaseModal>

    <!-- Skip confirm modal (recurring) -->
    <BaseModal v-model="showSkipConfirm" title="Пропустить тренировку?" max-width="sm">
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">«{{ toSkip?.title }}»</p>
      <div class="space-y-2">
        <button
          :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
            skipScope === 'one' ? 'border-primary bg-primary/5' : 'border-gray-200 dark:border-gray-700']"
          @click="skipScope = 'one'"
        >
          <p class="font-medium text-gray-900 dark:text-white">Только эту тренировку</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ toSkip?.scheduledDate }}</p>
        </button>
        <button
          :class="['w-full text-left px-4 py-3 rounded-xl border-2 transition-colors text-sm',
            skipScope === 'all' ? 'border-orange-400 bg-orange-50 dark:bg-orange-900/10' : 'border-gray-200 dark:border-gray-700']"
          @click="skipScope = 'all'"
        >
          <p class="font-medium text-gray-900 dark:text-white">Эту и все следующие</p>
          <p class="text-xs text-gray-400 mt-0.5">Пропустит все запланированные повторения</p>
        </button>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showSkipConfirm = false">Отмена</BaseButton>
        <BaseButton @click="doSkip">Пропустить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { CalendarDays, CheckCircle2, Clock, Ban, Pencil, Trash2, AlertCircle } from 'lucide-vue-next'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const store = useStore()
const router = useRouter()

const loading = ref(false)
const activeTab = ref('planned')
const showDeleteConfirm = ref(false)
const toDelete = ref(null)
const deleteScope = ref('one')
const showSkipConfirm = ref(false)
const toSkip = ref(null)
const skipScope = ref('one')

const tabs = [
  { value: 'planned', label: 'Предстоящие', icon: markRaw(Clock), activeClass: 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300' },
  { value: 'completed', label: 'Выполненные', icon: markRaw(CheckCircle2), activeClass: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' },
  { value: 'skipped', label: 'Пропущенные', icon: markRaw(Ban), activeClass: 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300' },
  { value: 'all', label: 'Все', icon: markRaw(CalendarDays), activeClass: 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300' },
]

const allPlanned = computed(() => store.getters['planned/all'])

const filtered = computed(() => {
  if (activeTab.value === 'all') return allPlanned.value
  return allPlanned.value.filter(p => p.status === activeTab.value)
})

const today = new Date().toISOString().split('T')[0]

function dateLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  const diff = Math.round((new Date(dateStr) - new Date(today)) / 86400000)
  const dayName = d.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
  if (dateStr === today) return `Сегодня — ${dayName}`
  if (diff === 1) return `Завтра — ${dayName}`
  if (diff === -1) return `Вчера — ${dayName}`
  return dayName.charAt(0).toUpperCase() + dayName.slice(1)
}

const grouped = computed(() => {
  const map = {}
  for (const plan of filtered.value) {
    const d = plan.scheduledDate
    if (!map[d]) map[d] = []
    map[d].push(plan)
  }
  return Object.keys(map).sort().map(date => ({
    date,
    label: dateLabel(date),
    items: map[date],
  }))
})

const emptyDescription = computed(() => {
  const map = {
    planned: 'Запланируйте тренировки наперёд',
    completed: 'Выполненные тренировки из плана появятся здесь',
    skipped: 'Пропущенные тренировки появятся здесь',
    all: 'Запланируйте тренировки наперёд',
  }
  return map[activeTab.value]
})

function totalSets(plan) {
  return plan.exercises.reduce((n, ex) => n + ex.sets.length, 0)
}

function statusIcon(plan) {
  const isOverdue = plan.status === 'planned' && plan.scheduledDate < today
  if (plan.status === 'completed') return { icon: markRaw(CheckCircle2), bg: 'bg-green-100 dark:bg-green-900/30', color: 'text-green-600' }
  if (plan.status === 'skipped') return { icon: markRaw(Ban), bg: 'bg-gray-100 dark:bg-gray-800', color: 'text-gray-400' }
  if (isOverdue) return { icon: markRaw(AlertCircle), bg: 'bg-orange-100 dark:bg-orange-900/30', color: 'text-orange-500' }
  return { icon: markRaw(Clock), bg: 'bg-primary/10', color: 'text-primary' }
}

function statusBadge(plan) {
  const isOverdue = plan.status === 'planned' && plan.scheduledDate < today
  if (plan.status === 'completed') return { label: 'Выполнено', class: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' }
  if (plan.status === 'skipped') return { label: 'Пропущено', class: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400' }
  if (isOverdue) return { label: 'Просрочено', class: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400' }
  return { label: 'Запланировано', class: 'bg-primary/10 text-primary' }
}

async function startPlan(plan) {
  await store.dispatch('workouts/startWorkoutFromPlan', plan)
  router.push('/workouts/new')
}

function skipPlan(plan) {
  if (plan.recurrenceGroupId) {
    toSkip.value = plan
    skipScope.value = 'one'
    showSkipConfirm.value = true
  } else {
    doSkipOne(plan)
  }
}

async function doSkipOne(plan) {
  try {
    await store.dispatch('planned/skipPlannedWorkout', plan.id)
    store.dispatch('ui/showToast', { message: 'Тренировка пропущена', type: 'info' })
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  }
}

async function doSkip() {
  try {
    if (skipScope.value === 'all') {
      await store.dispatch('planned/skipUpcomingRecurring', toSkip.value)
      store.dispatch('ui/showToast', { message: 'Все следующие пропущены', type: 'info' })
    } else {
      await doSkipOne(toSkip.value)
    }
  } finally {
    showSkipConfirm.value = false
  }
}

function deletePlan(plan) {
  toDelete.value = plan
  deleteScope.value = 'one'
  showDeleteConfirm.value = true
}

async function doDelete() {
  try {
    if (deleteScope.value === 'all' && toDelete.value.recurrenceGroupId) {
      await store.dispatch('planned/deleteUpcomingRecurring', toDelete.value)
      store.dispatch('ui/showToast', { message: 'Повторения удалены', type: 'success' })
    } else {
      await store.dispatch('planned/deletePlannedWorkout', toDelete.value.id)
      store.dispatch('ui/showToast', { message: 'План удалён', type: 'success' })
    }
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    showDeleteConfirm.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await store.dispatch('planned/fetchPlannedWorkouts')
  } finally {
    loading.value = false
  }
})
</script>
