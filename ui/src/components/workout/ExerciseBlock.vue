<template>
  <div
    class="relative overflow-hidden rounded-xl shadow-sm border border-gray-100 dark:border-gray-800"
    @touchstart.passive="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Delete reveal layer -->
    <div
      class="absolute inset-0 bg-red-500 flex items-center justify-end pr-5 gap-2 cursor-pointer select-none"
      @click.stop="onDeleteZoneTap"
    >
      <span class="text-white text-sm font-semibold">Удалить упражнение</span>
      <Trash2 class="w-4 h-4 text-white flex-shrink-0" />
    </div>

    <!-- Sliding card content -->
    <div
      class="bg-white dark:bg-gray-900 p-4 relative"
      :style="{
        transform: `translateX(${swipeX}px)`,
        transition: swiping ? 'none' : 'transform 0.28s cubic-bezier(0.25, 1, 0.5, 1)',
      }"
      @click="snapClosed"
    >
      <div class="flex items-center justify-between mb-3" @click.stop>
        <div class="flex items-center gap-2 min-w-0">
          <span class="drag-handle flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 cursor-grab active:cursor-grabbing touch-none p-1 -ml-1">
            <GripVertical class="w-4 h-4" />
          </span>
          <div class="min-w-0">
            <h4 class="font-semibold text-gray-900 dark:text-white">{{ exercise.exerciseName }}</h4>
            <p class="text-xs text-gray-400">{{ exercise.sets.length }} {{ isCardio ? 'сессий' : 'подход(ов)' }}</p>
          </div>
        </div>
        <button
          class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
          @click.stop="removeExercise"
        >
          <Trash2 class="w-5 h-5" />
        </button>
      </div>

      <!-- Header row -->
      <div v-if="isCardio" class="flex items-center gap-1 mb-2 text-xs text-gray-400 font-medium">
        <span class="w-5" />
        <span class="flex-1 text-center">Мин.</span>
        <span class="w-10" />
        <span class="w-8" />
      </div>
      <div v-else class="flex items-center gap-1 mb-2 text-xs text-gray-400 font-medium">
        <span class="w-5" />
        <span class="flex-1 text-center">Вес (кг)</span>
        <span class="w-3" />
        <span class="flex-1 text-center">Повт.</span>
        <span class="w-10" />
        <span class="w-8" />
      </div>

      <div class="space-y-2" @click.stop>
        <ExerciseSetRow
          v-for="(set, i) in exercise.sets"
          :key="set.id"
          :set="set"
          :exercise-id="exercise.exerciseId"
          :index="i"
          :is-cardio="isCardio"
          @remove="removeSet(set.id)"
        />
      </div>

      <button
        class="mt-3 w-full py-2 text-sm text-primary hover:text-primary-dark font-medium border border-dashed border-primary/30 hover:border-primary/60 rounded-lg transition-colors"
        @click.stop="addSet"
      >
        {{ isCardio ? '+ Добавить сессию' : '+ Добавить подход' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { Trash2, GripVertical } from 'lucide-vue-next'
import ExerciseSetRow from './ExerciseSetRow.vue'

const props = defineProps({
  exercise: { type: Object, required: true }
})

const store = useStore()
const exerciseData = computed(() => store.getters['exercises/exerciseById'](props.exercise.exerciseId))
const isCardio = computed(() => exerciseData.value?.muscleGroup === 'Кардио')

// ── Swipe ──────────────────────────────────────────────────────────────────────
const swipeX = ref(0)
const swiping = ref(false)

const SNAP_POINT = -100
const AUTO_DELETE_PX = -220

let startX = 0
let startY = 0
let baseX = 0
let axis = null

function onTouchStart(e) {
  startX = e.touches[0].clientX
  startY = e.touches[0].clientY
  baseX = swipeX.value
  swiping.value = true
  axis = null
}

function onTouchMove(e) {
  const dx = e.touches[0].clientX - startX
  const dy = e.touches[0].clientY - startY

  if (axis === null) {
    if (Math.abs(dx) < 4 && Math.abs(dy) < 4) return
    axis = Math.abs(dx) > Math.abs(dy) ? 'h' : 'v'
    if (axis === 'v') { swiping.value = false; return }
  }
  if (axis !== 'h') return

  e.preventDefault()

  const raw = baseX + dx
  if (raw > 0) {
    swipeX.value = 0
  } else if (raw < AUTO_DELETE_PX) {
    swipeX.value = AUTO_DELETE_PX + (raw - AUTO_DELETE_PX) * 0.15
  } else {
    swipeX.value = raw
  }
}

function onTouchEnd() {
  swiping.value = false

  if (swipeX.value <= AUTO_DELETE_PX * 0.65) {
    swipeX.value = -window.innerWidth
    setTimeout(removeExercise, 260)
  } else if (swipeX.value < SNAP_POINT / 2) {
    swipeX.value = SNAP_POINT
  } else {
    swipeX.value = 0
  }
}

function snapClosed() {
  if (swipeX.value !== 0) swipeX.value = 0
}

function onDeleteZoneTap() {
  swipeX.value = 0
  setTimeout(removeExercise, 280)
}

// ── Actions ────────────────────────────────────────────────────────────────────
function addSet() {
  store.commit('workouts/ADD_SET_TO_EXERCISE', props.exercise.exerciseId)
}

function removeSet(setId) {
  store.commit('workouts/REMOVE_SET', { exerciseId: props.exercise.exerciseId, setId })
}

function removeExercise() {
  store.commit('workouts/REMOVE_EXERCISE_FROM_ACTIVE', props.exercise.exerciseId)
}
</script>
