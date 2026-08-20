<template>
  <div
    v-if="showLoadingIndicator"
    class="fixed inset-0 z-[200] flex items-center justify-center bg-black/40"
  >
    <span class="w-10 h-10 border-4 border-white border-t-transparent rounded-full animate-spin" />
  </div>
  <component :is="isPublicRoute ? 'div' : AppLayout">
    <RouterView v-slot="{ Component }">
      <Transition name="fade">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
    <ToastContainer v-if="isPublicRoute" />
  </component>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import ToastContainer from '@/components/ui/ToastContainer.vue'
import { loadSession } from '@/store/modules/workouts.js'

const route = useRoute()
const isPublicRoute = computed(() => !!route.meta.public)

const store = useStore()

const isLoading = computed(() => store.getters['ui/isLoading'])
const showLoadingIndicator = ref(false)
let showSpinnerTimer = null

watch(isLoading, (loading) => {
  if (loading) {
    showSpinnerTimer = setTimeout(() => { showLoadingIndicator.value = true }, 300)
  } else {
    clearTimeout(showSpinnerTimer)
    showLoadingIndicator.value = false
  }
})

watch(
  () => store.state.user.theme,
  (theme) => document.documentElement.classList.toggle('dark', theme === 'dark'),
  { immediate: true }
)

// Start/stop WebSocket when auth state changes
watch(
  () => store.state.auth.token,
  (token) => {
    if (token) {
      store.dispatch('notifications/startWs')
    } else {
      store.dispatch('notifications/stopWs')
    }
  },
  { immediate: true }
)

onMounted(() => {
  const session = loadSession()
  if (!session?.startedAt) return

  const todayMidnight = new Date()
  todayMidnight.setHours(0, 0, 0, 0)

  if (new Date(session.startedAt) < todayMidnight) {
    // Session crossed midnight while browser was closed — auto-save now
    store.dispatch('workouts/autoSaveMidnight', { draft: session.draft, startedAt: session.startedAt })
  } else {
    // Session is still today — schedule midnight auto-save
    scheduleMidnightSave()
  }
})

function scheduleMidnightSave() {
  const now = new Date()
  const midnight = new Date(now)
  midnight.setDate(midnight.getDate() + 1)
  midnight.setHours(0, 0, 0, 0)
  const msToMidnight = midnight - now

  setTimeout(() => {
    const session = loadSession()
    if (session?.startedAt) {
      store.dispatch('workouts/autoSaveMidnight', { draft: session.draft, startedAt: session.startedAt })
    }
  }, msToMidnight)
}
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
