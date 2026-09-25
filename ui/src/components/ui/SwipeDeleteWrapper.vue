<template>
  <div
    :class="['relative overflow-hidden', bordered ? 'rounded-2xl border border-steel-100 shadow-soft dark:border-steel-700 dark:shadow-none' : '']"
    @touchstart.passive.stop="onTouchStart"
    @touchmove.stop="onTouchMove"
    @touchend.stop="onTouchEnd"
  >
    <!-- Delete reveal layer -->
    <div
      v-if="!props.disabled"
      class="absolute inset-0 bg-primary flex items-center justify-end pr-5 gap-2 select-none cursor-pointer"
      @click.stop="onZoneTap"
    >
      <span class="text-white text-sm font-semibold">{{ deleteLabel }}</span>
      <Trash2 class="w-4 h-4 text-white flex-shrink-0" />
    </div>

    <!-- Sliding content -->
    <div
      :style="{
        transform: `translateX(${swipeX}px)`,
        transition: swiping ? 'none' : 'transform 0.28s cubic-bezier(0.25, 1, 0.5, 1)',
      }"
      class="relative"
    >
      <!-- Intercept taps when swiped open so they only snap back -->
      <div v-if="swipeX < -5" class="absolute inset-0 z-10" @click.stop="snapClosed" />
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Trash2 } from 'lucide-vue-next'

const props = defineProps({
  deleteLabel: { type: String, default: 'Удалить' },
  disabled: { type: Boolean, default: false },
  // Card-level usages (templates, plans, exercises...) rely on this
  // wrapper for their own border. Small repeated rows (a single set)
  // look too heavy with one — they opt out.
  bordered: { type: Boolean, default: true },
})

const emit = defineEmits(['delete'])

const swipeX = ref(0)
const swiping = ref(false)

const SNAP_POINT = -88
const AUTO_DELETE_PX = -220

let startX = 0, startY = 0, baseX = 0, axis = null

function onTouchStart(e) {
  if (props.disabled) return
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
  swipeX.value = raw > 0 ? 0 : raw < AUTO_DELETE_PX ? AUTO_DELETE_PX + (raw - AUTO_DELETE_PX) * 0.15 : raw
}

function onTouchEnd() {
  swiping.value = false
  if (swipeX.value <= AUTO_DELETE_PX * 0.65) {
    swipeX.value = -window.innerWidth
    setTimeout(() => emit('delete'), 260)
  } else if (swipeX.value < SNAP_POINT / 2) {
    swipeX.value = SNAP_POINT
  } else {
    swipeX.value = 0
  }
}

function snapClosed() { swipeX.value = 0 }

function onZoneTap() {
  swipeX.value = 0
  emit('delete')
}
</script>
