<template>
  <div v-if="cycle">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-6">
      <button class="p-2 rounded-xl hover:bg-gray-100 text-gray-500 mt-1 flex-shrink-0" @click="$router.back()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 flex-wrap mb-1">
          <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', cycle.is_public ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
            {{ cycle.is_public ? 'Публичный' : 'Приватный' }}
          </span>
          <span v-if="cycle.author_name" class="text-xs text-gray-500">{{ cycle.author_name }}</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">{{ cycle.title }}</h2>
        <p v-if="cycle.description" class="text-sm text-gray-600 mt-1">{{ cycle.description }}</p>
        <p class="text-xs text-gray-400 mt-1">{{ cycle.workouts.length }} тренировок</p>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <div class="flex rounded-xl border border-gray-200 overflow-hidden text-xs font-medium">
          <button
            :class="['px-3 py-1.5 transition-colors', viewMode === 'list' ? 'bg-primary text-white' : 'text-gray-500 hover:bg-gray-50']"
            @click="viewMode = 'list'"
          >Список</button>
          <button
            :class="['px-3 py-1.5 transition-colors', viewMode === 'table' ? 'bg-primary text-white' : 'text-gray-500 hover:bg-gray-50']"
            @click="viewMode = 'table'"
          >Таблица</button>
        </div>
        <RouterLink v-if="isOwner" :to="`/cycles/${cycle.id}/edit`" class="btn btn-outline text-sm px-3 py-1.5">
          Редактировать
        </RouterLink>
      </div>
    </div>

    <!-- Run progress / Start button -->
    <div class="card p-4 mb-4">
      <div v-if="currentRun">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-700">Прогресс цикла</span>
          <span class="text-sm font-bold text-primary">{{ completedCount }} / {{ totalCount }}</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2">
          <div
            class="bg-primary h-2 rounded-full transition-all"
            :style="{ width: progressPct + '%' }"
          />
        </div>
        <p v-if="completedCount === totalCount" class="text-xs text-green-600 font-medium mt-2">Цикл завершён!</p>
      </div>
      <div v-else class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-gray-700">Цикл не начат</p>
          <p class="text-xs text-gray-400 mt-0.5">Начните цикл чтобы отслеживать прогресс</p>
        </div>
        <BaseButton :loading="startingRun" @click="startRun">Начать цикл</BaseButton>
      </div>
    </div>

    <!-- 1RM notice -->
    <div v-if="missingMaxes.length" class="card p-3 mb-4 border-l-4 border-amber-400 flex items-start gap-2">
      <span class="text-lg flex-shrink-0">⚠️</span>
      <div class="text-sm text-gray-700">
        Укажите ваши ПМ в <RouterLink to="/profile" class="text-primary font-medium underline">Профиле</RouterLink>
        для расчёта весов:
        <span class="font-semibold">{{ missingMaxes.join(', ') }}</span>
      </div>
    </div>

    <!-- List view -->
    <div v-if="viewMode === 'list'" class="space-y-3">
      <div
        v-for="workout in cycle.workouts"
        :key="workout.id"
        class="card p-4"
      >
        <div class="flex items-center justify-between mb-2">
          <p class="text-xs font-bold text-gray-400">Тренировка {{ workout.workout_number }}</p>
          <span v-if="currentRun && completedIds.has(workout.id)" class="text-xs text-green-600 font-semibold">✓ Выполнена</span>
          <BaseButton
            v-else-if="currentRun"
            size="sm"
            variant="outline"
            :loading="startingWorkout === workout.id"
            @click="openStartModal(workout.id)"
          >Начать тренировку</BaseButton>
        </div>
        <div class="space-y-3">
          <div v-for="exName in exerciseColumns" :key="exName">
            <template v-if="getSets(workout, exName).length">
              <p class="text-sm font-semibold text-gray-800 mb-1">{{ exName }}</p>
              <div class="space-y-0.5 pl-2">
                <div v-for="(set, i) in getSets(workout, exName)" :key="i" class="text-sm text-gray-700">
                  <span class="text-gray-400 text-xs w-5 inline-block">{{ i + 1 }}.</span>
                  <template v-if="getMax(exName)">
                    <span class="font-bold text-primary">{{ calcWeight(getMax(exName), set.percent_1rm) }} кг</span>
                    <span class="text-gray-400"> / </span>{{ set.reps }} повт.
                    <span class="text-gray-400 text-xs ml-1">({{ set.percent_1rm }}%)</span>
                  </template>
                  <template v-else>
                    <span class="font-bold text-gray-700">{{ set.percent_1rm }}%</span>
                    <span class="text-gray-400"> / </span>{{ set.reps }} повт.
                  </template>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Table view -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm border-collapse">
          <thead>
            <!-- Row 1: exercise names -->
            <tr class="bg-gray-50">
              <th class="border border-gray-200 px-3 py-2 text-center text-xs font-semibold text-gray-500 w-10" rowspan="2">#</th>
              <th
                v-for="exName in exerciseColumns"
                :key="exName"
                :colspan="maxSetsPerExercise[exName]"
                class="border border-gray-200 px-3 py-2 text-center text-xs font-semibold text-gray-700"
              >
                <div>{{ exName }}</div>
                <div v-if="getMax(exName)" class="text-primary font-bold mt-0.5">ПМ: {{ getMax(exName) }} кг</div>
                <div v-else class="text-amber-500 font-normal mt-0.5">ПМ не задан</div>
              </th>
            </tr>
            <!-- Row 2: set numbers -->
            <tr class="bg-gray-50">
              <template v-for="exName in exerciseColumns" :key="exName">
                <th
                  v-for="n in maxSetsPerExercise[exName]"
                  :key="n"
                  class="border border-gray-200 px-2 py-1.5 text-center text-xs text-gray-400 font-medium w-28"
                >
                  подход {{ n }}
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="workout in cycle.workouts"
              :key="workout.id"
              class="hover:bg-primary/5"
            >
              <td class="border border-gray-200 px-3 py-2.5 font-bold text-gray-400 text-xs text-center">
                {{ workout.workout_number }}
                <div v-if="currentRun" class="mt-1">
                  <span v-if="completedIds.has(workout.id)" class="text-green-500 text-base">✓</span>
                  <button
                    v-else
                    :disabled="startingWorkout === workout.id"
                    class="text-primary text-xs font-semibold hover:underline disabled:opacity-50"
                    @click="openStartModal(workout.id)"
                  >▶ старт</button>
                </div>
              </td>
              <template v-for="exName in exerciseColumns" :key="exName">
                <td
                  v-for="n in maxSetsPerExercise[exName]"
                  :key="n"
                  class="border border-gray-200 px-3 py-2.5 text-center whitespace-nowrap"
                >
                  <template v-if="getSets(workout, exName)[n - 1]">
                    <template v-if="getMax(exName)">
                      <span class="font-bold text-primary">{{ calcWeight(getMax(exName), getSets(workout, exName)[n - 1].percent_1rm) }} кг</span>
                      <span class="text-gray-400"> / </span>
                      <span class="text-gray-700">{{ getSets(workout, exName)[n - 1].reps }} повт.</span>
                    </template>
                    <template v-else>
                      <span class="font-bold text-gray-700">{{ getSets(workout, exName)[n - 1].percent_1rm }}%</span>
                      <span class="text-gray-400"> / </span>
                      <span class="text-gray-700">{{ getSets(workout, exName)[n - 1].reps }} повт.</span>
                    </template>
                  </template>
                  <span v-else class="text-gray-300">—</span>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-center py-16 text-gray-400">Загрузка...</div>
  <div v-else class="text-center py-16 text-gray-400">Цикл не найден</div>

  <!-- Start workout modal -->
  <BaseModal v-model="showStartModal" title="Начать тренировку">
    <p class="text-sm text-gray-500 mb-3">Упражнения из цикла будут предзаполнены. Можно добавить подсобные упражнения прямо в тренировке.</p>
    <div>
      <label class="label">Заметки (необязательно)</label>
      <textarea v-model="workoutNotes" rows="2" class="input resize-none" placeholder="Самочувствие, план..."/>
    </div>
    <template #footer>
      <BaseButton variant="ghost" @click="showStartModal = false">Отмена</BaseButton>
      <BaseButton @click="confirmStartWorkout">Начать</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const loading = ref(false)
const viewMode = ref('table')
const startingRun = ref(false)
const startingWorkout = ref(null) // cycle_workout_id being started
const showStartModal = ref(false)
const pendingWorkoutId = ref(null)
const workoutNotes = ref('')

const cycle = computed(() => store.state.cycles.currentCycle)
const currentRun = computed(() => store.state.cycles.currentRun)
const currentUserId = computed(() => store.state.auth.userId)
const isOwner = computed(() => cycle.value?.created_by === currentUserId.value)
const userMaxes = computed(() => store.state.user.maxes)

const completedIds = computed(() => store.getters['cycles/completedWorkoutIds'])
const completedCount = computed(() => completedIds.value.size)
const totalCount = computed(() => cycle.value?.workouts.length ?? 0)
const progressPct = computed(() => totalCount.value ? Math.round(completedCount.value / totalCount.value * 100) : 0)

onMounted(async () => {
  loading.value = true
  try {
    await store.dispatch('cycles/fetchCycle', route.params.id)
    await store.dispatch('cycles/fetchCycleRun', route.params.id)
  } finally {
    loading.value = false
  }
})

async function startRun() {
  startingRun.value = true
  try { await store.dispatch('cycles/startCycleRun', route.params.id) }
  finally { startingRun.value = false }
}

function openStartModal(cycleWorkoutId) {
  pendingWorkoutId.value = cycleWorkoutId
  workoutNotes.value = ''
  showStartModal.value = true
}

function confirmStartWorkout() {
  const cycleWorkoutId = pendingWorkoutId.value
  showStartModal.value = false
  const cycleWorkout = cycle.value.workouts.find(w => w.id === cycleWorkoutId)
  store.dispatch('workouts/startWorkoutFromCycle', {
    cycleWorkout,
    cycleTitle: cycle.value.title,
    runId: currentRun.value.id,
    cycleWorkoutId,
    cycleId: route.params.id,
  })
  store.commit('workouts/SET_ACTIVE_WORKOUT_FIELD', { field: 'notes', value: workoutNotes.value })
  router.push('/workouts/new')
}

// Collect unique exercise names across all workouts (preserving first-seen order)
const exerciseColumns = computed(() => {
  if (!cycle.value) return []
  const seen = new Set()
  const cols = []
  for (const w of cycle.value.workouts) {
    for (const e of w.exercises) {
      if (!seen.has(e.exercise_name)) {
        seen.add(e.exercise_name)
        cols.push(e.exercise_name)
      }
    }
  }
  return cols
})

// Max sets count per exercise across all workouts (determines colspan)
const maxSetsPerExercise = computed(() => {
  const result = {}
  for (const exName of exerciseColumns.value) {
    result[exName] = Math.max(1, ...cycle.value.workouts.map(w => getSets(w, exName).length))
  }
  return result
})

const missingMaxes = computed(() =>
  exerciseColumns.value.filter(name => !getMax(name))
)

function getMax(exerciseName) {
  return userMaxes.value.find(m => m.exercise_name === exerciseName)?.weight_kg ?? null
}

function getSets(workout, exerciseName) {
  return workout.exercises.find(e => e.exercise_name === exerciseName)?.sets ?? []
}

/** Round to nearest 2.5 kg (standard powerlifting plate increment). */
function calcWeight(maxKg, percent) {
  const raw = maxKg * percent / 100
  const rounded = Math.round(raw / 2.5) * 2.5
  return rounded % 1 === 0 ? rounded.toFixed(1) : rounded
}
</script>
