<template>
  <AppLayout>
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStore } from 'vuex'
import AppLayout from '@/components/layout/AppLayout.vue'
import { loadSession } from '@/store/modules/workouts.js'

const store = useStore()

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
