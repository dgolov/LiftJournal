import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import store from './store/index.js'
import { onPendingChange, onNetworkError } from './services/workoutService.js'
import './assets/main.css'

const app = createApp(App)
app.use(store)
app.use(router)

onPendingChange(delta => {
  store.commit(delta > 0 ? 'ui/INC_PENDING' : 'ui/DEC_PENDING')
})
onNetworkError(() => {
  store.dispatch('ui/showToast', {
    message: 'Отсутствует соединение с сервером',
    type: 'error',
    duration: 4000,
  })
})

app.mount('#app')

async function loadInitialData() {
  if (!store.getters['auth/isAuthenticated']) return
  const results = await Promise.allSettled([
    store.dispatch('workouts/initWorkouts'),
    store.dispatch('exercises/initExercises'),
    store.dispatch('user/initUser'),
  ])
  const failed = results.filter(r => r.status === 'rejected')
  if (failed.length) failed.forEach(r => console.error('Failed to load initial data:', r.reason))
}

loadInitialData()
