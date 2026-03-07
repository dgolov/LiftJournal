<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['pointer-events-auto flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg text-sm font-medium text-white', toastClass(toast.type)]"
        >
          <span>{{ toastIcon(toast.type) }}</span>
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const toasts = computed(() => store.state.ui.toasts)

function toastClass(type) {
  return { success: 'bg-green-600', error: 'bg-red-600', warning: 'bg-yellow-500' }[type] || 'bg-gray-700'
}
function toastIcon(type) {
  return { success: '✓', error: '✕', warning: '⚠' }[type] || 'ℹ'
}
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to { opacity: 0; transform: translateX(100%); }
</style>
