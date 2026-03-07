import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    library: [],
    filter: {
      muscleGroup: null,
      equipment: null,
      search: ''
    }
  }),

  getters: {
    allExercises: state => [...state.library].sort((a, b) => a.name.localeCompare(b.name, 'ru')),

    filteredExercises: (state, getters) => {
      let list = getters.allExercises
      const { muscleGroup, equipment, search } = state.filter
      if (muscleGroup) list = list.filter(e => e.muscleGroup === muscleGroup)
      if (equipment) list = list.filter(e => e.equipment === equipment)
      if (search) {
        const q = search.toLowerCase()
        list = list.filter(e => e.name.toLowerCase().includes(q))
      }
      return list
    },

    exerciseById: state => id => state.library.find(e => e.id === id),

    muscleGroups: state => [...new Set(state.library.map(e => e.muscleGroup))].sort((a, b) => a.localeCompare(b, 'ru')),
    equipmentTypes: state => [...new Set(state.library.map(e => e.equipment))].sort((a, b) => a.localeCompare(b, 'ru')),

    // Cross-reference workouts state to compute progress
    progressForExercise: (_state, _getters, rootState) => exerciseId => {
      const sessions = []
      const workouts = rootState.workouts.workouts
      workouts.forEach(workout => {
        const ex = workout.exercises.find(e => e.exerciseId === exerciseId)
        if (!ex || !ex.sets.length) return
        const maxWeight = Math.max(...ex.sets.map(s => s.weight))
        const totalVolume = ex.sets.reduce((sum, s) => sum + s.weight * s.reps, 0)
        const maxReps = Math.max(...ex.sets.map(s => s.reps))
        // Epley estimated 1RM: weight × (1 + reps / 30); for 1 rep = weight itself
        const best1RM = Math.max(...ex.sets.map(s =>
          s.reps === 1 ? s.weight : Math.round(s.weight * (1 + s.reps / 30))
        ))
        sessions.push({ date: workout.date, maxWeight, totalVolume, maxReps, best1RM, workoutId: workout.id, workoutTitle: workout.title })
      })
      return sessions.sort((a, b) => a.date.localeCompare(b.date))
    },

    personalRecord: (_state, getters) => exerciseId => {
      const progress = getters.progressForExercise(exerciseId)
      if (!progress.length) return null
      let bestWeight = 0, bestWeightDate = null
      let best1RM = 0, best1RMDate = null
      let bestVolume = 0, bestVolumeDate = null
      progress.forEach(session => {
        if (session.maxWeight > bestWeight) {
          bestWeight = session.maxWeight
          bestWeightDate = session.date
        }
        if (session.best1RM > best1RM) {
          best1RM = session.best1RM
          best1RMDate = session.date
        }
        if (session.totalVolume > bestVolume) {
          bestVolume = session.totalVolume
          bestVolumeDate = session.date
        }
      })
      return { bestWeight, bestWeightDate, best1RM, best1RMDate, bestVolume, bestVolumeDate }
    }
  },

  mutations: {
    SET_LIBRARY(state, library) { state.library = library },
    ADD_EXERCISE(state, exercise) { state.library.push(exercise) },
    SET_FILTER(state, { key, value }) { state.filter[key] = value },
    RESET_FILTER(state) { state.filter = { muscleGroup: null, equipment: null, search: '' } }
  },

  actions: {
    async initExercises({ commit }) {
      const library = await workoutService.fetchExercises()
      commit('SET_LIBRARY', library)
    },

    async addCustomExercise({ commit }, exercise) {
      const saved = await workoutService.addCustomExercise(exercise)
      commit('ADD_EXERCISE', saved)
      return saved
    }
  }
}
