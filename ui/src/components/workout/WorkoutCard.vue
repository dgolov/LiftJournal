<template>
  <!-- Swipe wrapper — overflow-hidden clips the sliding card to reveal the red zone -->
  <div
    class="relative overflow-hidden rounded-xl shadow-sm border border-gray-100 dark:border-gray-800"
    @touchstart.passive="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Delete reveal layer (always behind the card) -->
    <div
      class="absolute inset-0 bg-red-500 flex items-center justify-end pr-5 gap-2 cursor-pointer select-none"
      @click.stop="onDeleteZoneTap"
    >
      <span class="text-white text-sm font-semibold">Удалить</span>
      <Trash2 class="w-4 h-4 text-white flex-shrink-0" />
    </div>

    <!-- Sliding card -->
    <div
      class="bg-white dark:bg-gray-900 p-4 relative cursor-pointer"
      :style="{
        transform: `translateX(${swipeX}px)`,
        transition: swiping ? 'none' : 'transform 0.28s cubic-bezier(0.25, 1, 0.5, 1)',
      }"
      @click="onCardClick"
    >
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
            <span class="text-xs text-gray-400">{{ formattedDate }}</span>
          </div>
          <h3 class="font-semibold text-gray-900 dark:text-white truncate">{{ workout.title }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ workout.exercises.length }} упр. · {{ totalSets }} подх. · {{ formatDuration(workout.durationMinutes) }}
          </p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
            Тоннаж: {{ formatVolume(totalVolume) }} кг
          </p>
          <div v-if="socialMeta" class="flex items-center gap-3 mt-1.5">
            <span class="flex items-center gap-1 text-xs text-gray-400">
              <Heart class="w-3 h-3" :class="socialMeta.isLiked ? 'fill-red-400 text-red-400' : ''" />
              {{ socialMeta.likesCount }}
            </span>
            <span class="flex items-center gap-1 text-xs text-gray-400">
              <MessageCircle class="w-3 h-3" />
              {{ socialMeta.commentsCount }}
            </span>
          </div>
        </div>
        <!-- Desktop-only trash button -->
        <button
          class="hidden lg:flex w-10 h-10 items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
          title="Удалить"
          @click.stop="confirmDelete"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>

  <BaseModal v-model="showConfirm" title="Удалить тренировку?" max-width="sm">
    <p class="text-sm text-gray-600 dark:text-gray-400">Это действие нельзя отменить.</p>
    <template #footer>
      <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
      <BaseButton variant="danger" :disabled="deleting" @click="doDelete">
        {{ deleting ? 'Удаление...' : 'Удалить' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { Trash2, Heart, MessageCircle } from 'lucide-vue-next'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  workout: { type: Object, required: true }
})

const store = useStore()
const router = useRouter()
const showConfirm = ref(false)
const deleting = ref(false)

// ── Swipe ──────────────────────────────────────────────────────────────────────
const swipeX = ref(0)
const swiping = ref(false)

const SNAP_POINT = -88      // px — snapped-open width of delete zone
const AUTO_DELETE_PX = -220 // px — swipe this far to auto-delete without confirmation

let startX = 0
let startY = 0
let baseX = 0
let axis = null  // null | 'h' | 'v'

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
    // Rubber-band resistance past auto-delete threshold
    swipeX.value = AUTO_DELETE_PX + (raw - AUTO_DELETE_PX) * 0.15
  } else {
    swipeX.value = raw
  }
}

function onTouchEnd() {
  swiping.value = false

  if (swipeX.value <= AUTO_DELETE_PX * 0.65) {
    // Fly card off screen then delete
    swipeX.value = -window.innerWidth
    setTimeout(doDelete, 260)
  } else if (swipeX.value < SNAP_POINT / 2) {
    swipeX.value = SNAP_POINT
  } else {
    swipeX.value = 0
  }
}

function snapClosed() { swipeX.value = 0 }

function onCardClick() {
  if (swipeX.value !== 0) { snapClosed(); return }
  router.push(`/workouts/${props.workout.id}`)
}

function onDeleteZoneTap() {
  snapClosed()
  showConfirm.value = true
}

function confirmDelete() {
  showConfirm.value = true
}

async function doDelete() {
  deleting.value = true
  try {
    await store.dispatch('workouts/deleteWorkout', props.workout.id)
    store.dispatch('ui/showToast', { message: 'Тренировка удалена', type: 'success' })
  } finally {
    deleting.value = false
    showConfirm.value = false
    swipeX.value = 0
  }
}

const socialMeta = computed(() => store.state.social.workoutMeta[props.workout.id] || null)

// ── Display ────────────────────────────────────────────────────────────────────
const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[props.workout.type] || 'gray')

const formattedDate = computed(() => {
  const d = new Date(props.workout.date + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
})

const totalSets = computed(() =>
  props.workout.exercises.reduce((n, ex) => n + ex.sets.length, 0)
)

const totalVolume = computed(() =>
  props.workout.exercises.reduce((total, ex) =>
    total + ex.sets.filter(s => !s.failed).reduce((s, set) => s + set.weight * set.reps, 0), 0)
)

function formatVolume(v) {
  return v >= 1000 ? (v / 1000).toFixed(1) + ' т' : v
}

function formatDuration(minutes) {
  if (!minutes) return '—'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0) return `${h} ч ${m > 0 ? m + ' мин' : ''}`
  return `${m} мин`
}
</script>
