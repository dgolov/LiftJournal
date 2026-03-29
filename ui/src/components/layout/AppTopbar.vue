<template>
  <header class="fixed top-0 left-0 right-0 lg:left-64 z-30 h-16 bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800 flex items-center px-4 gap-4">
    <!-- Mobile hamburger -->
    <button class="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400" @click="toggleSidebar">
      <Menu class="w-5 h-5" />
    </button>

    <h1 class="flex-1 text-lg font-semibold text-gray-900 dark:text-gray-100">{{ pageTitle }}</h1>

    <!-- Quick add button (desktop) -->
    <RouterLink to="/workouts/new" class="hidden sm:flex btn-primary btn text-sm">
      + Тренировка
    </RouterLink>

    <!-- Theme toggle -->
    <button
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
      :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
      @click="toggleTheme"
    >
      <Sun v-if="isDark" class="w-5 h-5" />
      <Moon v-else class="w-5 h-5" />
    </button>

    <!-- Avatar -->
    <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary cursor-pointer">
      {{ initial }}
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { Menu, Sun, Moon } from 'lucide-vue-next'

const store = useStore()
const route = useRoute()

const initial = computed(() => store.state.user.profile.name?.charAt(0) || 'A')
const isDark = computed(() => store.state.user.theme === 'dark')

const titleMap = {
  history: 'История тренировок',
  'workout-create': 'Новая тренировка',
  'workout-detail': 'Тренировка',
  exercises: 'Упражнения',
  'exercise-detail': 'Упражнение',
  profile: 'Профиль'
}

const pageTitle = computed(() => titleMap[route.name] || 'LiftJournal')

function toggleSidebar() {
  store.commit('ui/TOGGLE_SIDEBAR')
}

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  store.dispatch('user/setTheme', next)
}
</script>
