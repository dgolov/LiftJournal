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
      <RouterLink v-if="isOwner" :to="`/cycles/${cycle.id}/edit`" class="btn btn-outline text-sm px-3 py-1.5 flex-shrink-0">
        Редактировать
      </RouterLink>
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

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="text-left px-3 py-2.5 text-xs font-semibold text-gray-500 w-12 flex-shrink-0">#</th>
              <th
                v-for="exName in exerciseColumns"
                :key="exName"
                class="text-left px-3 py-2.5 text-xs font-semibold text-gray-700 min-w-44"
              >
                <div>{{ exName }}</div>
                <div v-if="getMax(exName)" class="text-primary font-bold mt-0.5">ПМ: {{ getMax(exName) }} кг</div>
                <div v-else class="text-gray-400 font-normal mt-0.5">ПМ не задан</div>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr
              v-for="workout in cycle.workouts"
              :key="workout.id"
              class="hover:bg-gray-50/50"
            >
              <td class="px-3 py-2.5 font-bold text-gray-400 text-xs align-top">{{ workout.workout_number }}</td>
              <td
                v-for="exName in exerciseColumns"
                :key="exName"
                class="px-3 py-2.5 align-top"
              >
                <div v-if="getSets(workout, exName).length" class="space-y-0.5">
                  <div
                    v-for="(set, i) in getSets(workout, exName)"
                    :key="i"
                    class="flex items-baseline gap-1 flex-wrap"
                  >
                    <span class="font-semibold text-gray-800">{{ set.percent_1rm }}%</span>
                    <span class="text-gray-400 text-xs">×</span>
                    <span class="text-gray-700">{{ set.reps }} повт.</span>
                    <span v-if="getMax(exName)" class="text-primary font-bold text-xs ml-1">
                      = {{ calcWeight(getMax(exName), set.percent_1rm) }} кг
                    </span>
                  </div>
                </div>
                <span v-else class="text-gray-200">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-center py-16 text-gray-400">Загрузка...</div>
  <div v-else class="text-center py-16 text-gray-400">Цикл не найден</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'

const route = useRoute()
const store = useStore()

const loading = ref(false)
const cycle = computed(() => store.state.cycles.currentCycle)
const currentUserId = computed(() => store.state.auth.userId)
const isOwner = computed(() => cycle.value?.created_by === currentUserId.value)
const userMaxes = computed(() => store.state.user.maxes) // [{ exercise_name, weight_kg }]

onMounted(async () => {
  loading.value = true
  try { await store.dispatch('cycles/fetchCycle', route.params.id) }
  finally { loading.value = false }
})

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
