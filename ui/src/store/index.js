import { createStore } from 'vuex'
import workouts, { saveSession } from './modules/workouts.js'
import exercises from './modules/exercises.js'
import user from './modules/user.js'
import ui from './modules/ui.js'
import auth from './modules/auth.js'
import cycles from './modules/cycles.js'
import planned from './modules/planned.js'

const store = createStore({
  modules: { workouts, exercises, user, ui, auth, cycles, planned }
})

// Sync activeWorkout draft to localStorage whenever exercises/sets change during an active session
const DRAFT_SYNC_MUTATIONS = [
  'workouts/ADD_EXERCISE_TO_ACTIVE',
  'workouts/REMOVE_EXERCISE_FROM_ACTIVE',
  'workouts/ADD_SET_TO_EXERCISE',
  'workouts/UPDATE_SET',
  'workouts/REMOVE_SET',
  'workouts/SET_ACTIVE_WORKOUT_FIELD',
  'workouts/SET_ACTIVE_WORKOUT_EXERCISES',
]
store.subscribe((mutation) => {
  const ts = store.state.workouts.workoutStartedAt
  if (!ts) return
  if (DRAFT_SYNC_MUTATIONS.includes(mutation.type)) {
    saveSession(ts, store.state.workouts.activeWorkout, store.state.workouts.cycleContext, store.state.workouts.planContext)
  }
})

export default store
