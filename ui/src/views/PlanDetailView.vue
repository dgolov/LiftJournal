<template>
  <div v-if="plan" class="max-w-2xl">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-3">
        <button class="p-2 hover:bg-steel-100 dark:hover:bg-steel-700 text-steel-700 dark:text-steel-300 transition-colors" @click="$router.back()">
          <ChevronLeft class="w-5 h-5" />
        </button>
        <div class="ml-auto flex items-center flex-wrap justify-end gap-1">
          <RouterLink
            v-if="plan.status === 'completed' && plan.completedWorkoutId"
            :to="`/workouts/${plan.completedWorkoutId}`"
            class="flex items-center gap-1 px-2 h-8 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
          >
            <ExternalLink class="w-3.5 h-3.5" /> Открыть тренировку
          </RouterLink>
          <template v-if="plan.status === 'planned'">
            <button
              class="flex items-center gap-1 px-3 h-8 text-xs font-display font-semibold uppercase tracking-wide bg-primary text-white hover:bg-primary-dark transition-colors"
              @click="startPlan"
            >
              <Play class="w-3.5 h-3.5" /> Начать
            </button>
            <button
              class="flex items-center gap-1 px-2 h-8 text-xs font-medium text-steel-700 dark:text-steel-300 hover:bg-steel-100 dark:hover:bg-steel-700 transition-colors"
              @click="$router.push(`/planning/${plan.id}/edit`)"
            >
              <Pencil class="w-3.5 h-3.5" /> Изменить
            </button>
            <button
              class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary transition-colors"
              title="Перенести или пропустить"
              @click="showSkipConfirm = true"
            >
              <Ban class="w-4 h-4" />
            </button>
          </template>
          <button
            v-if="plan.status === 'skipped'"
            class="flex items-center gap-1 px-3 h-8 text-xs font-display font-semibold uppercase tracking-wide bg-primary text-white hover:bg-primary-dark transition-colors"
            @click="showMarkCompleted = true"
          >
            <CheckCircle2 class="w-3.5 h-3.5" /> Всё-таки выполнил
          </button>
          <button
            class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary transition-colors"
            title="Удалить"
            @click="confirmDelete"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
      <div>
        <div class="flex items-center gap-2 mb-1 flex-wrap">
          <BaseBadge :color="typeColor">{{ plan.type }}</BaseBadge>
          <span :class="['text-xs px-2 py-0.5 font-medium', badge.class]">{{ badge.label }}</span>
        </div>
        <h2 class="text-2xl font-bold text-ink dark:text-white">{{ plan.title }}</h2>
        <p class="text-sm text-steel-700 dark:text-steel-300 mt-1">
          {{ formattedDate }} · {{ plan.exercises.length }} упр. · {{ totalSets }} подходов
        </p>
        <p v-if="plan.notes" class="text-sm text-steel-700 dark:text-steel-300 mt-2 italic">{{ plan.notes }}</p>
      </div>
    </div>

    <!-- Exercises -->
    <div class="space-y-4">
      <div v-for="ex in plan.exercises" :key="ex.exerciseId" class="card p-4">
        <h3 class="font-display font-semibold text-ink dark:text-white mb-3">{{ ex.exerciseName }}</h3>
        <div class="space-y-2">
          <div v-for="(set, i) in ex.sets" :key="set.id" class="flex items-center gap-1 text-sm font-mono">
            <span class="text-steel-700 dark:text-steel-300 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>
            <span class="font-medium text-ink dark:text-white">{{ set.weight > 0 ? set.weight + ' кг' : 'Б/в' }}</span>
            <span class="text-steel-300">×</span>
            <span class="font-medium text-ink dark:text-white">{{ set.reps }} повт.</span>
          </div>
          <p v-if="!ex.sets.length" class="text-sm text-steel-700 dark:text-steel-300">Подходы не заданы</p>
        </div>
      </div>
      <div v-if="!plan.exercises.length" class="text-center py-8 text-steel-700 dark:text-steel-300">Упражнения не добавлены</div>
    </div>

    <SkipOrRescheduleModal v-model="showSkipConfirm" :plan="plan" />
    <MarkCompletedModal v-model="showMarkCompleted" :plan="plan" />

    <BaseModal v-model="showDeleteConfirm" title="Удалить план?" max-width="sm">
      <p class="text-sm text-steel-700 dark:text-steel-300 mb-3">«{{ plan.title }}»</p>
      <template v-if="plan.recurrenceGroupId">
        <div class="space-y-2">
          <button
            :class="['w-full text-left px-4 py-3 rounded-xl border transition-colors text-sm',
              deleteScope === 'one' ? 'border-primary bg-primary/5' : 'border-steel-300 dark:border-steel-700']"
            @click="deleteScope = 'one'"
          >
            <p class="font-medium text-ink dark:text-white">Только эту тренировку</p>
            <p class="text-xs text-steel-700 dark:text-steel-300 mt-0.5">{{ plan.scheduledDate }}</p>
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
  </div>

  <div v-else class="text-center py-16 text-steel-700 dark:text-steel-300">
    План не найден
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, Pencil, Trash2, Play, Ban, ExternalLink, CheckCircle2 } from 'lucide-vue-next'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import SkipOrRescheduleModal from '@/components/workout/SkipOrRescheduleModal.vue'
import MarkCompletedModal from '@/components/workout/MarkCompletedModal.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const showSkipConfirm = ref(false)
const showMarkCompleted = ref(false)
const showDeleteConfirm = ref(false)
const deleteScope = ref('one')

const plan = computed(() => store.getters['planned/byId'](route.params.id))

const today = new Date().toISOString().split('T')[0]

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[plan.value?.type] || 'gray')

const badge = computed(() => {
  const p = plan.value
  if (!p) return { label: '', class: '' }
  const isOverdue = p.status === 'planned' && p.scheduledDate < today
  if (p.status === 'completed') return { label: 'Выполнено', class: 'bg-success/15 text-success' }
  if (p.status === 'skipped') return { label: 'Пропущено', class: 'bg-steel-100 text-steel-300 dark:bg-steel-700' }
  if (isOverdue) return { label: 'Просрочено', class: 'bg-hazard/20 text-hazard' }
  return { label: 'Запланировано', class: 'bg-primary/10 text-primary' }
})

const formattedDate = computed(() => {
  if (!plan.value) return ''
  const d = new Date(plan.value.scheduledDate + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
})

const totalSets = computed(() => plan.value?.exercises.reduce((n, ex) => n + ex.sets.length, 0) ?? 0)

async function startPlan() {
  await store.dispatch('workouts/startWorkoutFromPlan', plan.value)
  router.push('/workouts/new')
}

function confirmDelete() {
  deleteScope.value = 'one'
  showDeleteConfirm.value = true
}

async function doDelete() {
  try {
    if (deleteScope.value === 'all' && plan.value.recurrenceGroupId) {
      await store.dispatch('planned/deleteUpcomingRecurring', plan.value)
      store.dispatch('ui/showToast', { message: 'Повторения удалены', type: 'success' })
    } else {
      await store.dispatch('planned/deletePlannedWorkout', plan.value.id)
      store.dispatch('ui/showToast', { message: 'План удалён', type: 'success' })
    }
    router.push('/planning')
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    showDeleteConfirm.value = false
  }
}

onMounted(async () => {
  if (!plan.value) await store.dispatch('planned/fetchPlannedWorkouts')
})
</script>
