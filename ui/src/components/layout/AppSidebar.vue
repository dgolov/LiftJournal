<template>
  <aside :class="['fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-100 flex flex-col transition-transform duration-300',
    isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0']">
    <!-- Logo -->
    <div class="h-16 flex items-center gap-3 px-6 border-b border-gray-100">
      <span class="text-2xl">💪</span>
      <span class="font-bold text-gray-900 text-lg">LiftJournal</span>
    </div>

    <!-- Nav -->
    <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="['flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
          'hover:bg-gray-50',
          $route.path === item.to || $route.path.startsWith(item.to + '/') && item.to !== '/'
            ? 'bg-primary/10 text-primary'
            : 'text-gray-600']"
        @click="closeSidebar"
      >
        <span class="text-lg">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- New workout button -->
    <div class="p-4 border-t border-gray-100">
      <RouterLink to="/workouts/new" @click="closeSidebar"
        class="flex items-center justify-center gap-2 w-full btn-primary btn rounded-xl py-3 text-sm font-semibold">
        <span class="text-lg">+</span>
        Новая тренировка
      </RouterLink>
      <p class="text-xs text-gray-400 text-center mt-2 truncate">{{ userName }}</p>
    </div>
  </aside>

  <!-- Mobile overlay -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-30 bg-black/30 lg:hidden"
    @click="closeSidebar"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const isOpen = computed(() => store.state.ui.sidebarOpen)
const userName = computed(() => store.getters['auth/userName'])

function closeSidebar() {
  store.commit('ui/SET_SIDEBAR', false)
}

const navItems = [
  { to: '/history', icon: '📋', label: 'История тренировок' },
  { to: '/exercises', icon: '🏋️', label: 'Упражнения' },
  { to: '/cycles', icon: '📊', label: 'Циклы' },
  { to: '/profile', icon: '👤', label: 'Профиль' }
]
</script>
