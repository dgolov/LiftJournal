<template>
  <div class="max-w-3xl">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-steel-100 dark:hover:bg-steel-900 text-steel-700 dark:text-steel-300 mt-1 transition-colors" @click="$router.push('/coach')">
        <ChevronLeft class="w-5 h-5" />
      </button>
      <PersonAvatar :name="summary?.name" :url="summary?.avatarUrl" size="lg" />
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold text-ink dark:text-white truncate">{{ summary?.name || 'Подопечный' }}</h2>
        <RouterLink :to="`/users/${athleteId}`" class="text-sm text-primary hover:underline">Профиль подопечного</RouterLink>
        <p v-if="summary" class="text-sm text-steel-700 dark:text-steel-300">
          <template v-if="summary.since">Занимается с {{ formatShortDate(summary.since) }} · </template>
          {{ summary.weekCompleted }} из {{ summary.weekPlanned }} на этой неделе
        </p>
        <p v-if="summary && !summary.canEditPlan" class="text-xs text-steel-700 dark:text-steel-300 mt-1 inline-flex items-center gap-1">
          <Lock class="w-3.5 h-3.5" /> Подопечный запретил менять свой план — только просмотр
        </p>
      </div>
    </div>

    <div v-if="loading && !data" class="text-center py-16 text-steel-300">Загрузка…</div>

    <template v-else-if="data">
      <div class="flex items-center justify-between gap-3 flex-wrap mb-4">
        <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5">
          <button
            v-for="t in tabs" :key="t.value"
            :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              tab === t.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white']"
            @click="tab = t.value"
          >{{ t.label }}</button>
        </div>
        <div v-if="summary?.canEditPlan" class="flex gap-2">
          <BaseButton variant="outline" @click="showCycleModal = true">Назначить цикл</BaseButton>
          <RouterLink
            :to="{ path: `/coach/athletes/${athleteId}/plan/new`, query: selectedDay >= todayStr ? { date: selectedDay } : {} }"
            class="btn btn-primary"
          >
            <Plus class="w-4 h-4" /> Запланировать
          </RouterLink>
        </div>
      </div>

      <!-- ── Calendar ───────────────────────────────────────────────────── -->
      <div v-if="tab === 'calendar'">
        <div class="flex items-center gap-2 mb-3">
          <button class="p-2 hover:bg-steel-100 dark:hover:bg-steel-700 transition-colors text-steel-700 dark:text-steel-300" @click="shiftMonth(-1)">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <div class="flex-1 text-center">
            <span class="text-base font-semibold text-ink dark:text-white capitalize">{{ monthLabel }}</span>
          </div>
          <button class="p-2 hover:bg-steel-100 dark:hover:bg-steel-700 transition-colors text-steel-700 dark:text-steel-300" @click="shiftMonth(1)">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <MonthCalendar
          class="mb-5"
          :year="monthCursor.getFullYear()"
          :month="monthCursor.getMonth()"
          :items-for="dayItems"
          :selected="selectedDay"
          @select="selectDay"
        />

        <h3 class="font-semibold text-ink dark:text-white mb-2">{{ formatLongDate(selectedDay) }}</h3>
        <p v-if="!dayPlans.length && !dayWorkouts.length" class="text-sm text-steel-300 mb-4">
          В этот день ничего нет.
        </p>

        <!-- Plans -->
        <div v-for="p in dayPlans" :key="p.id" class="card p-4 mb-3">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs text-steel-700 dark:text-steel-300 mb-0.5">
                План<template v-if="p.createdByName"> · от {{ p.createdById === myId ? 'вас' : p.createdByName }}</template>
              </p>
              <p class="font-semibold text-ink dark:text-white">{{ p.title }}</p>
            </div>
            <BaseBadge :color="planStatus[p.status].color">{{ planStatus[p.status].label }}</BaseBadge>
          </div>
          <p v-if="p.notes" class="text-sm text-steel-700 dark:text-steel-300 mt-2 whitespace-pre-line">{{ p.notes }}</p>
          <ul class="mt-3 space-y-1 text-sm">
            <li v-for="ex in p.exercises" :key="ex.exerciseId" class="flex gap-2">
              <span class="text-ink dark:text-white font-medium">{{ ex.exerciseName }}</span>
              <span class="text-steel-700 dark:text-steel-300">{{ formatSets(ex.sets) }}</span>
            </li>
          </ul>
          <RouterLink
            v-if="p.status === 'completed' && p.completedWorkoutId"
            :to="`/coach/athletes/${athleteId}/workouts/${p.completedWorkoutId}`"
            class="inline-block text-sm text-primary hover:underline mt-3"
          >Сравнить план и факт</RouterLink>
          <div v-if="p.status === 'planned' && summary?.canEditPlan" class="flex gap-2 mt-3">
            <RouterLink :to="`/coach/athletes/${athleteId}/plan/${p.id}/edit`" class="btn btn-outline text-xs px-3 py-1.5 min-h-0">
              <Pencil class="w-3.5 h-3.5" /> Изменить
            </RouterLink>
            <BaseButton size="sm" variant="ghost" @click="planToDelete = p">
              <Trash2 class="w-3.5 h-3.5" /> Удалить
            </BaseButton>
          </div>
        </div>

        <!-- Done workouts -->
        <div v-for="w in dayWorkouts" :key="w.id" class="card p-4 mb-3">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs text-success mb-0.5">Выполнено</p>
              <RouterLink :to="`/coach/athletes/${athleteId}/workouts/${w.id}`" class="font-semibold text-ink dark:text-white hover:text-primary">
                {{ w.title }}
              </RouterLink>
            </div>
            <RouterLink :to="`/coach/athletes/${athleteId}/workouts/${w.id}`" class="btn btn-outline text-xs px-3 py-1.5 min-h-0 flex-shrink-0">
              Открыть
            </RouterLink>
          </div>
          <p v-if="w.notes" class="text-sm text-steel-700 dark:text-steel-300 mt-1 whitespace-pre-line">{{ w.notes }}</p>
          <div v-for="ex in w.exercises" :key="ex.exerciseId" class="mt-3">
            <RouterLink :to="`/coach/athletes/${athleteId}/exercises/${ex.exerciseId}`" class="font-medium text-ink dark:text-white hover:text-primary">
              {{ ex.exerciseName }}
            </RouterLink>
            <p class="text-sm text-steel-700 dark:text-steel-300">
              <span v-for="(s, i) in ex.sets" :key="s.id" :class="s.failed ? 'line-through text-steel-300' : ''">
                {{ s.weight > 0 ? s.weight : 'б/в' }}×{{ s.reps }}<template v-if="s.rpe"> @{{ s.rpe }}</template><template v-if="i < ex.sets.length - 1">, </template>
              </span>
            </p>
            <p v-if="exerciseStats(w, ex)" class="text-xs text-steel-300 flex flex-wrap gap-x-3">
              <template v-for="st in [exerciseStats(w, ex)]" :key="'st'">
                <span>КПШ {{ st.lifts }}</span>
                <span>Тоннаж {{ st.totalVolume }} кг</span>
                <span>Абс. инт. {{ st.avgWeight }} кг</span>
                <span v-if="st.relIntensity != null">Отн. инт. {{ st.relIntensity }}%</span>
                <span v-if="st.best1RM">Расч. 1ПМ {{ st.best1RM }} кг</span>
              </template>
            </p>
          </div>
        </div>
      </div>

      <!-- ── Cycles ─────────────────────────────────────────────────────── -->
      <div v-else-if="tab === 'cycles'">
        <p v-if="!schedules.length" class="text-sm text-steel-700 dark:text-steel-300">
          Циклов в плане нет.<template v-if="summary?.canEditPlan"> Назначьте цикл — он разложится по дням с весами от 1ПМ подопечного.</template>
        </p>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="c in schedules" :key="c.id"
            :to="`/coach/athletes/${athleteId}/cycles/${c.id}`"
            class="card p-4 block hover:border-primary/40 transition-colors"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="font-semibold text-ink dark:text-white truncate">{{ c.title }}</p>
                <p class="text-xs text-steel-700 dark:text-steel-300">
                  {{ formatShortDate(c.from) }} – {{ formatShortDate(c.to) }}
                  <template v-if="c.mainExercises.length"> · {{ c.mainExercises.map(m => m.exerciseName).join(', ') }}</template>
                </p>
              </div>
              <p class="text-sm font-semibold text-ink dark:text-white tabular-nums flex-shrink-0">{{ c.completed }} / {{ c.total }}</p>
            </div>
            <div class="flex gap-0.5 mt-3">
              <span
                v-for="p in c.plans" :key="p.id"
                :class="['h-1.5 flex-1 rounded-full', { completed: 'bg-success', skipped: 'bg-steel-300 dark:bg-steel-700', planned: 'bg-steel-100 dark:bg-steel-700/50' }[p.status]]"
              />
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- ── Exercises ──────────────────────────────────────────────────── -->
      <div v-else-if="tab === 'exercises'">
        <p v-if="!exerciseList.length" class="text-sm text-steel-300">Подопечный ещё не записал ни одной тренировки.</p>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="ex in exerciseList" :key="ex.id"
            :to="`/coach/athletes/${athleteId}/exercises/${ex.id}`"
            class="card p-4 flex items-center gap-3 hover:border-primary/40 transition-colors"
          >
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-ink dark:text-white truncate">{{ ex.name }}</p>
              <p class="text-xs text-steel-700 dark:text-steel-300">
                {{ ex.sessions }} {{ plural(ex.sessions, 'сессия', 'сессии', 'сессий') }} · последняя {{ formatShortDate(ex.lastDate) }}
                <template v-if="ex.upcoming"> · в плане {{ ex.upcoming }}</template>
              </p>
            </div>
            <div v-if="ex.best1RM" class="text-right">
              <p class="text-sm font-semibold text-ink dark:text-white">{{ ex.best1RM }} кг</p>
              <p class="text-xs text-steel-300">расч. 1ПМ</p>
            </div>
            <ChevronRight class="w-4 h-4 text-steel-300" />
          </RouterLink>
        </div>
      </div>

      <!-- ── 1RM ────────────────────────────────────────────────────────── -->
      <div v-else>
        <div v-if="data.maxesHidden" class="card p-4 text-sm text-steel-700 dark:text-steel-300 flex items-center gap-2">
          <Lock class="w-4 h-4" /> Подопечный скрыл свои 1ПМ и вес тела.
        </div>
        <template v-else>
          <p v-if="!data.maxes.length" class="text-sm text-steel-300">В профиле подопечного 1ПМ не записаны — интенсивность считается от расчётного 1ПМ по тренировкам.</p>
          <div v-else class="card divide-y divide-steel-100 dark:divide-steel-700">
            <div v-for="m in data.maxes" :key="m.exercise_name" class="flex items-center justify-between p-4">
              <div>
                <p class="font-medium text-ink dark:text-white">{{ m.exercise_name }}</p>
                <p class="text-xs text-steel-300">записан {{ formatShortDate(m.recorded_at) }}</p>
              </div>
              <p class="text-lg font-semibold text-ink dark:text-white">{{ m.weight_kg }} кг</p>
            </div>
          </div>
        </template>
      </div>

      <div class="mt-10 pt-4 border-t border-steel-100 dark:border-steel-700">
        <button class="text-sm text-steel-700 dark:text-steel-300 hover:text-primary" @click="showEnd = true">
          Завершить сотрудничество
        </button>
      </div>
    </template>

    <ScheduleCycleModal v-model="showCycleModal" :athlete-id="athleteId" @scheduled="onCycleScheduled" />

    <!-- Delete plan -->
    <BaseModal :model-value="!!planToDelete" title="Удалить план?" max-width="sm" @update:model-value="planToDelete = null">
      <p class="text-sm text-steel-700 dark:text-steel-300">
        «{{ planToDelete?.title }}» пропадёт из плана {{ summary?.name }}.
      </p>
      <template #footer>
        <BaseButton variant="ghost" @click="planToDelete = null">Отмена</BaseButton>
        <BaseButton variant="danger" :loading="deleting" @click="deletePlan">Удалить</BaseButton>
      </template>
    </BaseModal>

    <!-- End coaching -->
    <BaseModal v-model="showEnd" title="Завершить сотрудничество?" max-width="sm">
      <p class="text-sm text-steel-700 dark:text-steel-300">
        Вы перестанете видеть тренировки {{ summary?.name }} и не сможете менять его план. Уже созданные вами тренировки останутся у подопечного.
      </p>
      <template #footer>
        <BaseButton variant="ghost" @click="showEnd = false">Отмена</BaseButton>
        <BaseButton variant="danger" :loading="ending" @click="endCoaching">Завершить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import MonthCalendar from '@/components/calendar/MonthCalendar.vue'
import { toDateStr } from '@/components/calendar/calendarStyles.js'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ChevronLeft, ChevronRight, Plus, Pencil, Trash2, Lock } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import PersonAvatar from '@/components/coach/PersonAvatar.vue'
import { apiErrorMessage } from '@/services/workoutService.js'
import { computeProgress, cycleSchedules } from '@/utils/progress.js'
import ScheduleCycleModal from '@/components/workout/ScheduleCycleModal.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const athleteId = computed(() => Number(route.params.athleteId))
const myId = computed(() => store.state.auth.userId)
const data = computed(() => store.getters['coach/athleteById'](athleteId.value))
const summary = computed(() => data.value?.summary)
const loading = ref(false)

const tabs = [
  { value: 'calendar', label: 'Календарь' },
  { value: 'cycles', label: 'Циклы' },
  { value: 'exercises', label: 'Упражнения' },
  { value: 'maxes', label: '1ПМ' },
]
const tab = ref('calendar')

onMounted(async () => {
  loading.value = true
  try {
    // Always refresh on open — the athlete may have trained since last visit.
    await store.dispatch('coach/loadAthlete', { id: athleteId.value, force: true })
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
    router.replace('/coach')
  } finally {
    loading.value = false
  }
})

// ── Calendar ──────────────────────────────────────────────────────────────
const todayStr = toDateStr(new Date())
const selectedDay = ref(todayStr)
const monthCursor = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))

const monthLabel = computed(() =>
  monthCursor.value.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' }))

function shiftMonth(delta) {
  const d = monthCursor.value
  monthCursor.value = new Date(d.getFullYear(), d.getMonth() + delta, 1)
}

const byDate = computed(() => {
  const map = {}
  const slot = date => (map[date] ||= { workouts: [], plans: [] })
  data.value?.workouts.forEach(w => slot(w.date).workouts.push(w))
  data.value?.planned.forEach(p => slot(p.scheduledDate).plans.push(p))
  return map
})

// Same chips as the history calendar: workouts by type, plans by status.
function dayItems(dateStr) {
  const slot = byDate.value[dateStr]
  if (!slot) return []
  return [
    ...slot.workouts.map(w => ({ label: w.title || w.type, kind: 'workout', type: w.type })),
    ...slot.plans.map(p => ({ label: p.title, kind: 'plan', status: p.status })),
  ]
}

function selectDay(day) {
  selectedDay.value = day.dateStr
  // Picking a padding day from a neighbouring month moves the grid there.
  if (!day.isCurrentMonth) monthCursor.value = new Date(day.date.getFullYear(), day.date.getMonth(), 1)
}

const dayPlans = computed(() => byDate.value[selectedDay.value]?.plans || [])
const dayWorkouts = computed(() => byDate.value[selectedDay.value]?.workouts || [])

const planStatus = {
  planned: { label: 'Запланировано', color: 'blue' },
  completed: { label: 'Выполнено', color: 'green' },
  skipped: { label: 'Пропущено', color: 'gray' },
}

function formatSets(sets) {
  // Collapse identical consecutive sets: 100×5, 100×5, 100×5 → 3×5 по 100 кг
  const groups = []
  sets.forEach(s => {
    const last = groups[groups.length - 1]
    if (last && last.weight === s.weight && last.reps === s.reps) last.count++
    else groups.push({ weight: s.weight, reps: s.reps, count: 1 })
  })
  return groups.map(g => `${g.weight > 0 ? g.weight : 'б/в'}×${g.reps}${g.count > 1 ? `×${g.count}` : ''}`).join(', ')
}

// Load metrics for one exercise in one workout, from the same series the
// athlete's exercise charts use — so the numbers match everywhere.
function exerciseName(d, exerciseId) {
  for (const w of d.workouts) {
    const ex = w.exercises.find(e => e.exerciseId === exerciseId)
    if (ex) return ex.exerciseName
  }
  return ''
}
// Rebuilt whenever the athlete's data is reloaded (`d` is read eagerly so the
// computed tracks it); per-exercise series are then computed lazily once.
const progressCache = computed(() => {
  const d = data.value
  const cache = {}
  return exerciseId => (cache[exerciseId] ||= d ? computeProgress({
    exercise: store.getters['exercises/exerciseById'](exerciseId) || { id: exerciseId, name: exerciseName(d, exerciseId) },
    exerciseId,
    workouts: d.workouts,
    planned: d.planned,
    maxes: d.maxes,
  }) : [])
})
function exerciseStats(workout, ex) {
  const session = progressCache.value(ex.exerciseId).find(s => s.workoutId === workout.id)
  return session && session.lifts != null ? session : null
}

// ── Exercises ─────────────────────────────────────────────────────────────
const exerciseList = computed(() => {
  if (!data.value) return []
  const map = {}
  data.value.workouts.forEach(w => w.exercises.forEach(ex => {
    const e = (map[ex.exerciseId] ||= { id: ex.exerciseId, name: ex.exerciseName, sessions: 0, lastDate: w.date, upcoming: 0 })
    e.sessions++
    if (w.date > e.lastDate) e.lastDate = w.date
  }))
  data.value.planned.forEach(p => {
    if (p.status !== 'planned') return
    p.exercises.forEach(ex => { if (map[ex.exerciseId]) map[ex.exerciseId].upcoming++ })
  })
  return Object.values(map)
    .map(e => {
      const sessions = progressCache.value(e.id)
      const best = sessions.reduce((m, s) => Math.max(m, s.best1RM || 0), 0)
      return { ...e, best1RM: best }
    })
    .sort((a, b) => b.lastDate.localeCompare(a.lastDate))
})

// ── Actions ───────────────────────────────────────────────────────────────
const schedules = computed(() => data.value ? cycleSchedules(data.value.planned) : [])
const showCycleModal = ref(false)
function onCycleScheduled(scheduleId) {
  router.push(`/coach/athletes/${athleteId.value}/cycles/${scheduleId}`)
}

const planToDelete = ref(null)
const deleting = ref(false)
async function deletePlan() {
  deleting.value = true
  try {
    await store.dispatch('coach/deletePlan', { athleteId: athleteId.value, planId: planToDelete.value.id })
    store.dispatch('ui/showToast', { message: 'План удалён', type: 'success' })
    planToDelete.value = null
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
  } finally {
    deleting.value = false
  }
}

const showEnd = ref(false)
const ending = ref(false)
async function endCoaching() {
  ending.value = true
  try {
    await store.dispatch('coach/end', summary.value.linkId)
    store.dispatch('ui/showToast', { message: 'Сотрудничество завершено', type: 'success' })
    router.replace('/coach')
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
  } finally {
    ending.value = false
  }
}

// ── Formatting ────────────────────────────────────────────────────────────
function formatLongDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })
}
function formatShortDate(dateStr) {
  return new Date(dateStr.slice(0, 10) + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
function plural(n, one, few, many) {
  const m10 = n % 10, m100 = n % 100
  if (m10 === 1 && m100 !== 11) return one
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few
  return many
}
</script>
