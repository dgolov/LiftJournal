<template>
  <div class="min-h-screen flex items-center justify-center bg-ink px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-primary border-2 border-white mb-4">
          <Dumbbell class="w-7 h-7 text-white" />
        </div>
        <h1 class="text-4xl font-display font-bold text-white uppercase tracking-wide">LiftForge</h1>
        <p class="text-sm text-steel-300 mt-2">Дневник пауэрлифтинга</p>
      </div>

      <div class="bg-card border-2 border-white shadow-[6px_6px_0_theme(colors.primary.DEFAULT)] p-6">
        <h2 class="text-lg font-display font-semibold text-ink mb-5">Вход</h2>

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

          <p v-if="error" class="text-sm text-primary font-medium">{{ error }}</p>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-steel-700">
          Нет аккаунта?
          <RouterLink to="/register" class="text-primary font-semibold hover:underline">Зарегистрироваться</RouterLink>
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
