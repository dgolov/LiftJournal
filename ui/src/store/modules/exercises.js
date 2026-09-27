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
    // `source: 'plan'` builds the same series from planned workouts instead —
    // what the plan asks for, measured against the 1RM known on that date.
    progressForExercise: (state, _getters, rootState) => (exerciseId, range = {}, { source = 'fact' } = {}) => {
      const exercise = state.library.find(e => e.id === exerciseId)
      const isCardio = exercise?.muscleGroup === 'Кардио'
      // Relative intensity is measured against the best 1RM known *at that
      // session*: the profile max recorded on/before it, or the best estimate
      // from actual sessions up to then — so the baseline is walked over full
      // history and the period filter is applied only at the end.
      const declaredMax = exercise && rootState.user?.maxes?.find(m => m.exercise_name === exercise.name)
      const declaredOn = date => declaredMax && declaredMax.recorded_at.slice(0, 10) <= date ? declaredMax.weight_kg : 0
      const factSessions = [...rootState.workouts.workouts]
        .sort((a, b) => a.date.localeCompare(b.date))
        .map(w => ({ id: w.id, date: w.date, title: w.title, ex: w.exercises.find(e => e.exerciseId === exerciseId) }))
      const planSessions = (rootState.planned?.plannedWorkouts || [])
        .filter(p => p.status !== 'skipped')
        .sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
        .map(p => ({ id: p.id, date: p.scheduledDate, title: p.title, ex: p.exercises?.find(e => e.exerciseId === exerciseId) }))

      // Best actual e1RM per date, for plan baselines.
      const actualBest = []
      let running = 0
      factSessions.forEach(({ date, ex }) => {
        if (!ex) return
        running = Math.max(running, sessionE1RM(ex.sets.filter(s => !s.failed)))
        actualBest.push({ date, best: running })
      })
      const actualBestOn = date => {
        let best = 0
        for (const a of actualBest) { if (a.date > date) break; best = a.best }
        return best
      }

      const isPlan = source === 'plan'
      const sessions = []
      running = 0
      ;(isPlan ? planSessions : factSessions).forEach(({ id, date, title, ex }) => {
        if (!ex || !ex.sets?.length) return
        const sets = ex.sets.filter(s => !s.failed)
        if (!sets.length) return
        const setsCount = sets.length
        const totalSetsCount = ex.sets.length
        const base = {
          date, setsCount, totalSetsCount, workoutId: id, workoutTitle: title,
          link: isPlan ? `/planning/${id}` : `/workouts/${id}`,
        }
        if (isCardio) {
          const totalMinutes = sets.reduce((sum, s) => sum + (s.reps || 0), 0)
          sessions.push({ ...base, totalMinutes })
          return
        }
        const bestSet = sets.reduce((a, b) => b.weight > a.weight ? b : a, sets[0])
        const e1RM = sessionE1RM(sets)
        let baseline1RM
        if (isPlan) {
          // Only fall back to the plan's own implied 1RM when nothing real is
          // known yet — otherwise a plan above the current max should read >100%.
          baseline1RM = Math.max(actualBestOn(date), declaredOn(date)) || e1RM
        } else {
          running = Math.max(running, e1RM)
          baseline1RM = Math.max(running, declaredOn(date))
        }
        const { lifts, tonnage, workingTonnage, avgWeight } = sessionLoad(sets, baseline1RM)
        sessions.push({
          ...base,
          maxWeight: bestSet.weight,
          maxWeightReps: bestSet.reps,
          maxReps: Math.max(...sets.map(s => s.reps)),
          totalVolume: tonnage,
          workingTonnage,
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
