import workoutService from '@/services/workoutService.js'
import { computeProgress, computePersonalRecord } from '@/utils/progress.js'

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

    // Cross-reference workouts state to compute progress. `range` optionally
    // narrows to { from, to } (inclusive ISO date strings) for period stats.
    progressForExercise: (state, _getters, rootState) => (exerciseId, range = {}, { source = 'fact' } = {}) =>
      computeProgress({
        exercise: state.library.find(e => e.id === exerciseId),
        exerciseId,
        workouts: rootState.workouts.workouts,
        planned: rootState.planned?.plannedWorkouts || [],
        maxes: rootState.user?.maxes || [],
        range,
        source,
      }),

    personalRecord: (state, getters) => (exerciseId, range = {}) => {
      const exercise = state.library.find(e => e.id === exerciseId)
      return computePersonalRecord(getters.progressForExercise(exerciseId, range), exercise?.muscleGroup === 'Кардио')
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
      try {
        const library = await workoutService.fetchExercises()
        commit('SET_LIBRARY', library)
        localStorage.setItem('gym_cache_exercises', JSON.stringify(library))
      } catch (e) {
        if (e?.isNetworkError) {
          const cached = localStorage.getItem('gym_cache_exercises')
          if (cached) commit('SET_LIBRARY', JSON.parse(cached))
        }
        throw e
      }
    },

    async addCustomExercise({ commit }, exercise) {
      const saved = await workoutService.addCustomExercise(exercise)
      commit('ADD_EXERCISE', saved)
      return saved
    }
  }
}
