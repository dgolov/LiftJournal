<template>
  <nav class="fixed bottom-0 left-0 right-0 z-30 bg-card/90 backdrop-blur-md dark:bg-steel-900/90 border-t border-steel-100 dark:border-steel-700 flex lg:hidden pb-safe-nav">
    <RouterLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      :class="['flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors border-t-2 -mt-[2px]',
        $route.path.startsWith(item.to) ? 'text-primary border-primary' : 'text-steel-300 border-transparent hover:text-steel-700']"
    >
      <component :is="item.icon" class="w-6 h-6 mb-0.5" />
      {{ item.label }}
    </RouterLink>
    <RouterLink to="/workouts/new"
      class="flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors border-t-2 -mt-[2px]"
      :class="$route.path === '/workouts/new' ? 'text-primary border-primary' : 'text-steel-300 border-transparent hover:text-steel-700'">
      <Plus class="w-6 h-6 mb-0.5" />
      Запись
    </RouterLink>
  </nav>
</template>

<script setup>
import { markRaw } from 'vue'
import { ClipboardList, Dumbbell, Plus, CalendarDays, LayoutDashboard, Users } from 'lucide-vue-next'

const navItems = [
  { to: '/dashboard', icon: markRaw(LayoutDashboard), label: 'Дашборд' },
  { to: '/feed', icon: markRaw(Users), label: 'Лента' },
  { to: '/history', icon: markRaw(ClipboardList), label: 'История' },
  { to: '/exercises', icon: markRaw(Dumbbell), label: 'Упражнения' },
]
</script>
