import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import store from './store/index.js'
import './assets/main.css'

const app = createApp(App)
app.use(store)
app.use(router)

async function init() {
  if (store.getters['auth/isAuthenticated']) {
    try {
      await Promise.all([
        store.dispatch('workouts/initWorkouts'),
        store.dispatch('exercises/initExercises'),
        store.dispatch('user/initUser'),
      ])
    } catch {
      // Token may be expired — clear and redirect to login
      store.commit('auth/CLEAR_AUTH')
    }
  }
  app.mount('#app')
}

init()
