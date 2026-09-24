<template>
  <aside :class="['fixed inset-y-0 left-0 z-40 w-64 bg-card dark:bg-steel-900 border-r-2 border-ink dark:border-steel-700 flex flex-col pt-safe-top transition-transform duration-300',
    isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0']">
    <!-- Logo -->
    <div class="h-16 flex items-center gap-2.5 px-6 border-b-2 border-ink dark:border-steel-700">
      <Dumbbell class="w-6 h-6 text-primary flex-shrink-0" />
      <span class="font-display font-bold text-ink dark:text-white text-xl uppercase tracking-wide">LiftForge</span>
    </div>

    <!-- Nav -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="['flex items-center gap-3 px-3 py-2.5 text-sm font-medium transition-colors border-2 border-transparent',
          $route.path === item.to || $route.path.startsWith(item.to + '/') && item.to !== '/'
            ? 'bg-primary text-white'
            : 'text-steel-700 dark:text-steel-300 hover:border-steel-100 dark:hover:border-steel-700']"
        @click="closeSidebar"
      >
        <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- New workout button -->
    <div class="p-3 border-t-2 border-ink dark:border-steel-700">
      <RouterLink to="/workouts/new" @click="closeSidebar"
        class="btn btn-primary w-full">
        <Plus class="w-4 h-4" />
        Новая тренировка
      </RouterLink>
      <p class="text-xs text-steel-700 dark:text-steel-300 text-center mt-3 truncate">{{ userName }}</p>
      <p class="text-xs text-steel-300 dark:text-steel-700 text-center mt-0.5 font-mono">v{{ APP_VERSION }}</p>
    </div>
  </aside>

  <!-- Mobile overlay -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-30 bg-ink/40 lg:hidden"
    @click="closeSidebar"
  />
</template>

<script setup>
import { computed, markRaw } from 'vue'
import { APP_VERSION } from '@/version.js'
import { useStore } from 'vuex'
import { Dumbbell, ClipboardList, BarChart3, User, Plus, CalendarDays, BookOpen, LayoutDashboard, Users, LayoutTemplate } from 'lucide-vue-next'

const store = useStore()
const isOpen = computed(() => store.state.ui.sidebarOpen)
const userName = computed(() => store.getters['auth/userName'])

function closeSidebar() {
  store.commit('ui/SET_SIDEBAR', false)
}

const navItems = [
  { to: '/dashboard', icon: markRaw(LayoutDashboard), label: 'Дашборд' },
  { to: '/feed', icon: markRaw(Users), label: 'Лента' },
  { to: '/history', icon: markRaw(ClipboardList), label: 'История тренировок' },
  { to: '/planning', icon: markRaw(CalendarDays), label: 'Планирование' },
  { to: '/templates', icon: markRaw(LayoutTemplate), label: 'Шаблоны' },
  { to: '/exercises', icon: markRaw(Dumbbell), label: 'Упражнения' },
  { to: '/cycles', icon: markRaw(BarChart3), label: 'Циклы' },
  { to: '/profile', icon: markRaw(User), label: 'Профиль' },
  { to: '/about', icon: markRaw(BookOpen), label: 'Справка' },
]
</script>
