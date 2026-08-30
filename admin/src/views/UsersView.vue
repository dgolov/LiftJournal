<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Пользователи</h2>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else>
      <p v-if="actionError" class="text-sm text-danger mb-3">{{ actionError }}</p>

      <div class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 text-left text-xs text-gray-400 uppercase tracking-wide">
              <th class="px-4 py-2.5">ID</th>
              <th class="px-4 py-2.5">Имя</th>
              <th class="px-4 py-2.5">Email</th>
              <th class="px-4 py-2.5">Роль</th>
              <th class="px-4 py-2.5" colspan="2"></th>
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
              <td class="px-4 py-2.5 text-right">
                <button
                  v-if="u.isAdmin"
                  class="btn-outline text-xs px-3 py-1.5 hover:!bg-danger/10 hover:!text-danger hover:!border-danger/40 disabled:opacity-40 disabled:cursor-not-allowed"
                  :disabled="busyId === u.id || u.id === currentUserId"
                  :title="u.id === currentUserId ? 'Нельзя снять права администратора с самого себя' : ''"
                  @click="revoke(u)"
                >Снять права</button>
                <button
                  v-else
                  class="btn-outline text-xs px-3 py-1.5"
                  :disabled="busyId === u.id"
                  @click="grant(u)"
                >Сделать админом</button>
              </td>
              <td class="px-4 py-2.5 text-right">
                <button
                  class="btn-outline text-xs px-3 py-1.5"
                  :disabled="busyId === u.id"
                  @click="openResetPassword(u)"
                >Сбросить пароль</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!users.length" class="text-center py-12 text-gray-400 text-sm">Нет пользователей</p>
      </div>
    </div>

    <!-- Reset password modal -->
    <div v-if="resetting" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="closeResetPassword">
      <div class="card p-5 w-full max-w-sm">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-1">Сбросить пароль</h3>
        <p class="text-xs text-gray-400 mb-3">{{ resetting.name || resetting.email }}</p>
        <input
          v-model="newPassword"
          type="text"
          placeholder="Новый пароль"
          class="input"
          @keyup.enter="submitResetPassword"
        />
        <p class="text-xs text-gray-400 mt-1.5">Не короче 6 символов</p>
        <p v-if="resetError" class="text-sm text-danger mt-2">{{ resetError }}</p>
        <div class="flex justify-end gap-2 mt-4">
          <button class="btn-outline text-sm px-3 py-1.5" @click="closeResetPassword">Отмена</button>
          <button
            class="btn-primary text-sm px-3 py-1.5"
            :disabled="newPassword.trim().length < 6 || busyId === resetting.id"
            @click="submitResetPassword"
          >Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService, { authState } from '@/services/adminService.js'

const users = ref([])
const loading = ref(true)
const error = ref('')
const actionError = ref('')
const busyId = ref(null)
const currentUserId = authState.userId

const resetting = ref(null)
const newPassword = ref('')
const resetError = ref('')

onMounted(async () => {
  try {
    users.value = await adminService.fetchUsers()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function setAdmin(u, isAdmin) {
  actionError.value = ''
  busyId.value = u.id
  try {
    const updated = await adminService.setUserAdmin(u.id, isAdmin)
    const i = users.value.findIndex(x => x.id === u.id)
    if (i !== -1) users.value[i] = updated
  } catch (e) {
    actionError.value = e.message
  } finally {
    busyId.value = null
  }
}

function grant(u) {
  setAdmin(u, true)
}

function revoke(u) {
  if (!confirm(`Снять права администратора у пользователя «${u.name || u.email}»?`)) return
  setAdmin(u, false)
}

function openResetPassword(u) {
  resetting.value = u
  newPassword.value = ''
  resetError.value = ''
}

function closeResetPassword() {
  resetting.value = null
}

async function submitResetPassword() {
  const u = resetting.value
  const password = newPassword.value.trim()
  if (password.length < 6) return
  resetError.value = ''
  busyId.value = u.id
  try {
    await adminService.resetPassword(u.id, password)
    resetting.value = null
  } catch (e) {
    resetError.value = e.message
  } finally {
    busyId.value = null
  }
}
</script>
