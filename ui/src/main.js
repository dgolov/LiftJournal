import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import store from './store/index.js'
import './assets/main.css'

const app = createApp(App)
app.use(store)
app.use(router)

Promise.all([
  store.dispatch('workouts/initWorkouts'),
  store.dispatch('exercises/initExercises'),
  store.dispatch('user/initUser')
]).then(() => {
  app.mount('#app')
})
