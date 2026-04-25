<template>
  <div
    class="relative overflow-hidden rounded-xl shadow-sm border border-gray-100 dark:border-gray-800"
    @touchstart.passive="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Delete reveal layer -->
    <div
      v-if="!props.disabled"
      class="absolute inset-0 bg-red-500 flex items-center justify-end pr-5 gap-2 select-none cursor-pointer"
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
