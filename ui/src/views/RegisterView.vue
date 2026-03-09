<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="text-4xl mb-3">🏋️</div>
        <h1 class="text-2xl font-bold text-gray-900">LiftJournal</h1>
        <p class="text-sm text-gray-500 mt-1">Дневник пауэрлифтинга</p>
      </div>

      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-5">Регистрация</h2>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="label">Имя</label>
            <input
              v-model="form.name"
              type="text"
              class="input"
              placeholder="Иван"
              autocomplete="name"
              required
            />
          </div>
          <div>
            <label class="label">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="input"
              placeholder="you@example.com"
              autocomplete="email"
              required
            />
          </div>
          <div>
            <label class="label">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              class="input"
              placeholder="Минимум 6 символов"
              autocomplete="new-password"
              minlength="6"
              required
            />
          </div>

          <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? 'Создание...' : 'Создать аккаунт' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          Уже есть аккаунт?
          <RouterLink to="/login" class="text-primary font-medium hover:underline">Войти</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const form = reactive({ name: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await store.dispatch('auth/register', { name: form.name, email: form.email, password: form.password })
    await Promise.all([
      store.dispatch('workouts/initWorkouts'),
      store.dispatch('exercises/initExercises'),
      store.dispatch('user/initUser'),
    ])
    router.push('/')
  } catch (e) {
    const msg = e.message || ''
    error.value = msg.includes('400') ? 'Email уже зарегистрирован' : 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>
