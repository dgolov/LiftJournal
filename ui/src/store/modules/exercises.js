import workoutService from '@/services/workoutService.js'
import { sessionE1RM, sessionLoad, round1 } from '@/utils/strength.js'

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
    progressForExercise: (state, _getters, rootState) => (exerciseId, range = {}) => {
      const exercise = state.library.find(e => e.id === exerciseId)
      const isCardio = exercise?.muscleGroup === 'Кардио'
      // Relative intensity is measured against the best 1RM known *at that
      // session*: the profile max recorded on/before it, or the best estimate
      // from earlier sessions — so the baseline is walked over full history
      // and the period filter is applied only at the end.
      const declaredMax = exercise && rootState.user?.maxes?.find(m => m.exercise_name === exercise.name)
      const workouts = [...rootState.workouts.workouts].sort((a, b) => a.date.localeCompare(b.date))
      const sessions = []
      let runningBest1RM = 0
      workouts.forEach(workout => {
        const ex = workout.exercises.find(e => e.exerciseId === exerciseId)
        if (!ex || !ex.sets.length) return
        const sets = ex.sets.filter(s => !s.failed)
        if (!sets.length) return
        const setsCount = sets.length
        const totalSetsCount = ex.sets.length
        const base = { date: workout.date, setsCount, totalSetsCount, workoutId: workout.id, workoutTitle: workout.title }
        if (isCardio) {
          const totalMinutes = sets.reduce((sum, s) => sum + (s.reps || 0), 0)
          sessions.push({ ...base, totalMinutes })
          return
        }
        const bestSet = sets.reduce((a, b) => b.weight > a.weight ? b : a, sets[0])
        const { lifts, tonnage, avgWeight } = sessionLoad(sets)
        const e1RM = sessionE1RM(sets)
        runningBest1RM = Math.max(runningBest1RM, e1RM)
        const declared = declaredMax && declaredMax.recorded_at.slice(0, 10) <= workout.date ? declaredMax.weight_kg : 0
        const baseline1RM = Math.max(runningBest1RM, declared)
        sessions.push({
          ...base,
          maxWeight: bestSet.weight,
          maxWeightReps: bestSet.reps,
          maxReps: Math.max(...sets.map(s => s.reps)),
          totalVolume: tonnage,
          lifts,
          best1RM: Math.round(e1RM),
          baseline1RM: Math.round(baseline1RM),
          avgWeight: round1(avgWeight),
          relIntensity: baseline1RM ? Math.round(avgWeight / baseline1RM * 100) : null,
          topSetIntensity: baseline1RM ? Math.round(bestSet.weight / baseline1RM * 100) : null,
        })
      })
      return sessions.filter(s => (!range.from || s.date >= range.from) && (!range.to || s.date <= range.to))
    },

    personalRecord: (state, getters) => (exerciseId, range = {}) => {
      const exercise = state.library.find(e => e.id === exerciseId)
      const isCardio = exercise?.muscleGroup === 'Кардио'
      const progress = getters.progressForExercise(exerciseId, range)
      if (!progress.length) return null
      if (isCardio) {
        let bestDuration = 0, bestDurationDate = null
        progress.forEach(session => {
          if (session.totalMinutes > bestDuration) {
            bestDuration = session.totalMinutes
            bestDurationDate = session.date
          }
        })
        return { bestDuration, bestDurationDate }
      }
      let bestWeight = 0, bestWeightReps = 0, bestWeightDate = null
      let best1RM = 0, best1RMDate = null
      let bestVolume = 0, bestVolumeDate = null
      progress.forEach(session => {
        if (session.maxWeight > bestWeight) {
          bestWeight = session.maxWeight
          bestWeightReps = session.maxWeightReps
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
      return { bestWeight, bestWeightReps, bestWeightDate, best1RM, best1RMDate, bestVolume, bestVolumeDate }
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
