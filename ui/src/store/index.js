import { createStore } from 'vuex'
import workouts from './modules/workouts.js'
import exercises from './modules/exercises.js'
import user from './modules/user.js'
import ui from './modules/ui.js'

export default createStore({
  modules: { workouts, exercises, user, ui }
})
