<template>
  <nav class="fixed bottom-0 left-0 right-0 z-30 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 flex lg:hidden pb-safe-nav">
    <RouterLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      :class="['flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors',
        $route.path.startsWith(item.to) ? 'text-primary' : 'text-gray-400 hover:text-gray-600']"
    >
      <component :is="item.icon" class="w-6 h-6 mb-0.5" />
      {{ item.label }}
    </RouterLink>
    <RouterLink to="/workouts/new"
      class="flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors"
      :class="$route.path === '/workouts/new' ? 'text-primary' : 'text-gray-400 hover:text-gray-600'">
      <Plus class="w-6 h-6 mb-0.5" />
      Запись
    </RouterLink>
  </nav>
</template>

<script setup>
import { markRaw } from 'vue'
import { ClipboardList, Dumbbell, Plus, CalendarDays, LayoutDashboard } from 'lucide-vue-next'

const navItems = [
  { to: '/dashboard', icon: markRaw(LayoutDashboard), label: 'Дашборд' },
  { to: '/history', icon: markRaw(ClipboardList), label: 'История' },
  { to: '/planning', icon: markRaw(CalendarDays), label: 'План' },
  { to: '/exercises', icon: markRaw(Dumbbell), label: 'Упражнения' },
]
</script>
