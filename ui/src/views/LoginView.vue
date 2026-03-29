<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <Dumbbell class="w-10 h-10 text-primary mx-auto mb-3" />
        <h1 class="text-2xl font-bold text-gray-900">LiftJournal</h1>
        <p class="text-sm text-gray-500 mt-1">Дневник пауэрлифтинга</p>
      </div>

      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-5">Вход</h2>

        <form @submit.prevent="submit" class="space-y-4">
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
              placeholder="••••••••"
              autocomplete="current-password"
              required
            />
          </div>

          <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          Нет аккаунта?
          <RouterLink to="/register" class="text-primary font-medium hover:underline">Зарегистрироваться</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Dumbbell } from 'lucide-vue-next'

const store = useStore()
const router = useRouter()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await store.dispatch('auth/login', { email: form.email, password: form.password })
    await Promise.all([
      store.dispatch('workouts/initWorkouts'),
      store.dispatch('exercises/initExercises'),
      store.dispatch('user/initUser'),
    ])
    router.push('/')
  } catch (e) {
    console.log(e);
    error.value = 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>
