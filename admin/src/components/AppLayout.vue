<template>
  <div class="min-h-screen">
    <header class="border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div class="max-w-4xl mx-auto px-4 py-3 flex items-center gap-6">
        <span class="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
          <ShieldCheck class="w-5 h-5 text-primary" /> LiftJournal Admin
        </span>
        <nav class="flex items-center gap-1">
          <RouterLink
            to="/users"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'users' ? 'bg-primary/10 text-primary' : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'"
          >Пользователи</RouterLink>
          <RouterLink
            to="/exercises"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'exercises' ? 'bg-primary/10 text-primary' : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'"
          >Упражнения</RouterLink>
        </nav>
        <div class="ml-auto flex items-center gap-3 text-sm text-gray-500">
          <span>{{ authState.name }}</span>
          <button class="btn-outline text-xs px-3 py-1.5" @click="onLogout">Выйти</button>
        </div>
      </div>
    </header>
    <main class="max-w-4xl mx-auto px-4 py-6">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ShieldCheck } from 'lucide-vue-next'
import { authState, logout } from '@/services/adminService.js'

const router = useRouter()

function onLogout() {
  logout()
  router.push('/login')
}
</script>
