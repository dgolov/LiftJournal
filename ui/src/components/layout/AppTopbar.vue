<template>
  <header class="fixed top-0 left-0 right-0 lg:left-64 z-30 h-16 bg-white border-b border-gray-100 flex items-center px-4 gap-4">
    <!-- Mobile hamburger -->
    <button class="lg:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-600" @click="toggleSidebar">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>

    <h1 class="flex-1 text-lg font-semibold text-gray-900">{{ pageTitle }}</h1>

    <!-- Quick add button (desktop) -->
    <RouterLink to="/workouts/new" class="hidden sm:flex btn-primary btn text-sm">
      + Тренировка
    </RouterLink>

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

const store = useStore()
const route = useRoute()

const initial = computed(() => store.state.user.profile.name?.charAt(0) || 'A')

const titleMap = {
  history: 'История тренировок',
  'workout-create': 'Новая тренировка',
  'workout-detail': 'Тренировка',
  exercises: 'Упражнения',
  'exercise-detail': 'Упражнение',
  profile: 'Профиль'
}

const pageTitle = computed(() => titleMap[route.name] || 'GymDiary')

function toggleSidebar() {
  store.commit('ui/TOGGLE_SIDEBAR')
}
</script>
