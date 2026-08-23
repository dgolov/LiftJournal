<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Пользователи</h2>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else class="card overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-800 text-left text-xs text-gray-400 uppercase tracking-wide">
            <th class="px-4 py-2.5">ID</th>
            <th class="px-4 py-2.5">Имя</th>
            <th class="px-4 py-2.5">Email</th>
            <th class="px-4 py-2.5">Роль</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-b border-gray-50 dark:border-gray-800/60 last:border-0">
            <td class="px-4 py-2.5 text-gray-400">{{ u.id }}</td>
            <td class="px-4 py-2.5 font-medium text-gray-900 dark:text-white">{{ u.name || '—' }}</td>
            <td class="px-4 py-2.5 text-gray-500">{{ u.email || '—' }}</td>
            <td class="px-4 py-2.5">
              <span
                v-if="u.isAdmin"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary"
              >Админ</span>
              <span v-else class="text-gray-400 text-xs">Пользователь</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!users.length" class="text-center py-12 text-gray-400 text-sm">Нет пользователей</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService from '@/services/adminService.js'

const users = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    users.value = await adminService.fetchUsers()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
