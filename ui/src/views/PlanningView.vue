<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-ink dark:text-white">Планирование</h2>
      <RouterLink to="/planning/new" class="btn btn-primary text-sm px-4 py-2">+ Запланировать</RouterLink>
    </div>

    <!-- Filter chips -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full border text-sm font-medium transition-all duration-200',
          activeTab === tab.value ? tab.activeClass : 'border-transparent bg-steel-100 dark:bg-steel-950 text-steel-700 dark:text-steel-300 hover:bg-steel-300/40 dark:hover:bg-steel-700']"
        @click="activeTab = tab.value"
      >
        <component :is="tab.icon" :class="['w-3.5 h-3.5', activeTab === tab.value ? '' : 'opacity-60']" />
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-16 text-steel-700 dark:text-steel-300">Загрузка...</div>

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
          <span class="text-sm font-semibold text-steel-700 dark:text-steel-300">{{ group.label }}</span>
          <div class="flex-1 h-px bg-steel-100 dark:bg-steel-700" />
        </div>

        <div class="space-y-3">
          <SwipeDeleteWrapper
            v-for="plan in group.items"
            :key="plan.id"
            delete-label="Удалить план"
            @delete="deletePlan(plan)"
          >
            <div class="bg-card dark:bg-steel-900 p-4 cursor-pointer" @click="$router.push(`/planning/${plan.id}`)">
            <div class="flex items-start gap-3">
              <!-- Status icon -->
              <div :class="['w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5', statusIcon(plan).bg]">
                <component :is="statusIcon(plan).icon" class="w-4 h-4" :class="statusIcon(plan).color" />
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap mb-0.5">
                  <span :class="['text-xs px-2 py-0.5 font-medium', statusBadge(plan).class]">
                    {{ statusBadge(plan).label }}
                  </span>
                  <span class="text-xs text-steel-700 dark:text-steel-300">{{ plan.type }}</span>
                </div>
                <h3 class="font-display font-semibold text-ink dark:text-white line-clamp-2">{{ plan.title }}</h3>
                <p v-if="plan.exercises.length" class="text-xs text-steel-700 dark:text-steel-300 mt-0.5 whitespace-nowrap">
                  {{ plan.exercises.length }} упр. · {{ totalSets(plan) }} подходов
                </p>
                <p v-if="plan.notes" class="text-xs text-steel-700 dark:text-steel-300 mt-1 italic line-clamp-1">{{ plan.notes }}</p>

                <!-- Actions row -->
                <div class="flex items-center gap-1 mt-2">
                  <template v-if="plan.status === 'planned'">
                    <button
                      class="px-3 py-1.5 bg-primary text-white text-xs font-display font-semibold uppercase tracking-wide hover:bg-primary-dark transition-colors"
                      @click.stop="startPlan(plan)"
                    >Начать</button>
                    <button
                      class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary transition-colors"
                      title="Редактировать"
                      @click.stop="$router.push(`/planning/${plan.id}/edit`)"
                    >
                      <Pencil class="w-4 h-4" />
                    </button>
                    <button
                      class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary transition-colors"
                      title="Пропустить"
                      @click.stop="skipPlan(plan)"
                    >
                      <Ban class="w-4 h-4" />
                    </button>
                  </template>
                  <template v-else-if="plan.status === 'completed' && plan.completedWorkoutId">
                    <RouterLink
                      :to="`/workouts/${plan.completedWorkoutId}`"
                      class="px-3 py-1.5 rounded-full border border-steel-300 dark:border-steel-700 text-steel-700 dark:text-steel-300 text-xs font-medium hover:border-primary hover:text-primary transition-colors"
                      @click.stop
                    >Открыть</RouterLink>
                  </template>
                  <template v-else-if="plan.status === 'skipped'">
                    <button
                      class="px-3 py-1.5 bg-primary text-white text-xs font-display font-semibold uppercase tracking-wide hover:bg-primary-dark transition-colors"
                      @click.stop="markCompletedPlan(plan)"
                    >Всё-таки выполнил</button>
                  </template>
                  <button
                    class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary transition-colors"
                    @click.stop="deletePlan(plan)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Exercises preview -->
            <div v-if="plan.exercises.length && plan.status === 'planned'" class="mt-3 pt-3 border-t-2 border-steel-100 dark:border-steel-700 flex flex-wrap gap-x-3 gap-y-1">
              <span
                v-for="ex in plan.exercises"
                :key="ex.exerciseId"
                class="text-xs text-steel-700 dark:text-steel-300"
              >· {{ ex.exerciseName }}</span>
            </div>
            </div>
          </SwipeDeleteWrapper>
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <BaseModal v-model="showDeleteConfirm" title="Удалить план?" max-width="sm">
      <p class="text-sm text-steel-700 dark:text-steel-300 mb-3">«{{ toDelete?.title }}»</p>
      <template v-if="toDelete?.recurrenceGroupId">
        <div class="space-y-2">
          <button
            :class="['w-full text-left px-4 py-3 rounded-xl border transition-colors text-sm',
              deleteScope === 'one' ? 'border-primary bg-primary/5' : 'border-steel-300 dark:border-steel-700']"
            @click="deleteScope = 'one'"
          >
            <p class="font-medium text-ink dark:text-white">Только эту тренировку</p>
            <p class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">{{ toDelete?.scheduledDate }}</p>
          </button>
          <button
            :class="['w-full text-left px-4 py-3 rounded-xl border transition-colors text-sm',
              deleteScope === 'all' ? 'border-primary bg-primary/10' : 'border-steel-300 dark:border-steel-700']"
            @click="deleteScope = 'all'"
          >
            <p class="font-medium text-ink dark:text-white">Эту и все следующие</p>
            <p class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">Удалит все запланированные повторения</p>
          </button>
        </div>
      </template>
      <template v-else>
        <p class="text-sm text-steel-700 dark:text-steel-300">Будет удалён безвозвратно.</p>
      </template>
      <template #footer>
        <BaseButton variant="ghost" @click="showDeleteConfirm = false">Отмена</BaseButton>
        <BaseButton variant="danger" @click="doDelete">Удалить</BaseButton>
      </template>
    </BaseModal>

    <SkipOrRescheduleModal v-model="showSkipConfirm" :plan="toSkip" />
    <MarkCompletedModal v-model="showMarkCompleted" :plan="toMarkCompleted" />
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
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'
import SkipOrRescheduleModal from '@/components/workout/SkipOrRescheduleModal.vue'
import MarkCompletedModal from '@/components/workout/MarkCompletedModal.vue'

const store = useStore()
const router = useRouter()

const loading = ref(false)
const activeTab = ref('planned')
const showDeleteConfirm = ref(false)
const toDelete = ref(null)
const deleteScope = ref('one')
const showSkipConfirm = ref(false)
const toSkip = ref(null)
const showMarkCompleted = ref(false)
const toMarkCompleted = ref(null)

const tabs = [
  { value: 'planned', label: 'Предстоящие', icon: markRaw(Clock), activeClass: 'border-hazard bg-hazard/20 text-hazard' },
  { value: 'completed', label: 'Выполненные', icon: markRaw(CheckCircle2), activeClass: 'border-success bg-success/15 text-success' },
  { value: 'skipped', label: 'Пропущенные', icon: markRaw(Ban), activeClass: 'border-steel-700 dark:border-steel-300 bg-steel-100 dark:bg-steel-700 text-steel-700 dark:text-steel-300' },
  { value: 'all', label: 'Все', icon: markRaw(CalendarDays), activeClass: 'border-primary bg-primary/15 text-primary' },
]

const allPlanned = computed(() => store.getters['planned/all'])

const today = new Date().toISOString().split('T')[0]

const filtered = computed(() => {
  if (activeTab.value === 'all') return allPlanned.value
  if (activeTab.value === 'planned') {
    // Overdue plans (still 'planned' but the date has passed) are excluded here —
    // they clutter "Предстоящие" without being actionable; still visible under "Все".
    return allPlanned.value.filter(p => p.status === 'planned' && p.scheduledDate >= today)
  }
  return allPlanned.value.filter(p => p.status === activeTab.value)
})

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
  if (plan.status === 'completed') return { icon: markRaw(CheckCircle2), bg: 'bg-success/15', color: 'text-success' }
  if (plan.status === 'skipped') return { icon: markRaw(Ban), bg: 'bg-steel-100 dark:bg-steel-700', color: 'text-steel-300' }
  if (isOverdue) return { icon: markRaw(AlertCircle), bg: 'bg-hazard/20', color: 'text-hazard' }
  return { icon: markRaw(Clock), bg: 'bg-primary/10', color: 'text-primary' }
}

function statusBadge(plan) {
  const isOverdue = plan.status === 'planned' && plan.scheduledDate < today
  if (plan.status === 'completed') return { label: 'Выполнено', class: 'bg-success/15 text-success' }
  if (plan.status === 'skipped') return { label: 'Пропущено', class: 'bg-steel-100 text-steel-300 dark:bg-steel-700' }
  if (isOverdue) return { label: 'Просрочено', class: 'bg-hazard/20 text-hazard' }
  return { label: 'Запланировано', class: 'bg-primary/10 text-primary' }
}

async function startPlan(plan) {
  await store.dispatch('workouts/startWorkoutFromPlan', plan)
  router.push('/workouts/new')
}

function skipPlan(plan) {
  toSkip.value = plan
  showSkipConfirm.value = true
}

function markCompletedPlan(plan) {
  toMarkCompleted.value = plan
  showMarkCompleted.value = true
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
