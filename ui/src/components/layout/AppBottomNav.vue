<template>
  <nav class="fixed bottom-0 left-0 right-0 z-30 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 flex lg:hidden pb-safe-nav">
    <RouterLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      :class="['flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors',
        $route.path.startsWith(item.to) ? 'text-primary' : 'text-gray-400 hover:text-gray-600']"
    >
      <span class="text-2xl mb-0.5">{{ item.icon }}</span>
      {{ item.label }}
    </RouterLink>
    <RouterLink to="/workouts/new"
      class="flex-1 flex flex-col items-center pt-2 pb-1 text-xs font-medium transition-colors"
      :class="$route.path === '/workouts/new' ? 'text-primary' : 'text-gray-400 hover:text-gray-600'">
      <span class="text-2xl mb-0.5">➕</span>
      Запись
    </RouterLink>
  </nav>
</template>

<script setup>
const navItems = [
  { to: '/history', icon: '📋', label: 'История' },
  { to: '/exercises', icon: '🏋️', label: 'Упражнения' },
  { to: '/cycles', icon: '📊', label: 'Циклы' },
  { to: '/profile', icon: '👤', label: 'Профиль' }
]
</script>
