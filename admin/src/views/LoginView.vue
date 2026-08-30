<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="card p-6 w-full max-w-sm">
      <div class="flex items-center gap-2 mb-6">
        <ShieldCheck class="w-6 h-6 text-primary" />
        <h1 class="text-lg font-bold text-gray-900 dark:text-white">LiftJournal Admin</h1>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
          <input v-model="email" type="email" required class="input" autocomplete="username" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Пароль</label>
          <input v-model="password" type="password" required class="input" autocomplete="current-password" />
        </div>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ShieldCheck } from 'lucide-vue-next'
import adminService from '@/services/adminService.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await adminService.login(email.value, password.value)
    router.push('/users')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
