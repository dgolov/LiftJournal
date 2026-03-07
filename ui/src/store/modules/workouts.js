import workoutService from '@/services/workoutService.js'

function calcVolume(workout) {
  return workout.exercises.reduce((total, ex) => {
    return total + ex.sets.reduce((s, set) => s + set.weight * set.reps, 0)
  }, 0)
}

function uid() {
  return `s-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function emptyWorkout() {
  return {
    id: null,
    date: new Date().toISOString().split('T')[0],
    type: 'Силовая',
    title: '',
    durationMinutes: 60,
    notes: '',
    exercises: []
  }
}

export default {
  namespaced: true,

  state: () => ({
    workouts: [],
    activeWorkout: emptyWorkout(),
    filters: {
      dateFrom: null,
      dateTo: null,
      type: null,
      search: ''
    }
  }),

  getters: {
    allWorkouts: state => [...state.workouts].sort((a, b) => b.date.localeCompare(a.date)),

    filteredWorkouts: (state, getters) => {
      let list = getters.allWorkouts
      const { dateFrom, dateTo, type, search } = state.filters
      if (dateFrom) list = list.filter(w => w.date >= dateFrom)
      if (dateTo) list = list.filter(w => w.date <= dateTo)
      if (type) list = list.filter(w => w.type === type)
      if (search) {
        const q = search.toLowerCase()
        list = list.filter(w =>
          w.title.toLowerCase().includes(q) ||
          w.exercises.some(e => e.exerciseName.toLowerCase().includes(q))
        )
      }
      return list
    },

    workoutById: state => id => state.workouts.find(w => w.id === id),

    workoutsByMonth: (state, getters) => {
      const map = {}
      getters.allWorkouts.forEach(w => {
        const key = w.date.slice(0, 7)
        if (!map[key]) map[key] = []
        map[key].push(w)
      })
      return map
    },

    totalVolume: state => state.workouts.reduce((sum, w) => sum + calcVolume(w), 0),

    workoutsThisWeek: state => {
      const now = new Date()
      const startOfWeek = new Date(now)
      startOfWeek.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1))
      const startStr = startOfWeek.toISOString().split('T')[0]
      return state.workouts.filter(w => w.date >= startStr).length
    },

    longestStreak: state => {
      const dates = [...new Set(state.workouts.map(w => w.date))].sort()
      if (!dates.length) return 0
      let max = 1, cur = 1
      for (let i = 1; i < dates.length; i++) {
        const diff = (new Date(dates[i]) - new Date(dates[i - 1])) / 86400000
        if (diff === 1) { cur++; max = Math.max(max, cur) }
        else cur = 1
      }
      return max
    },

    workoutDates: state => new Set(state.workouts.map(w => w.date))
  },

  mutations: {
    SET_WORKOUTS(state, workouts) { state.workouts = workouts },
    ADD_WORKOUT(state, workout) { state.workouts.unshift(workout) },
    UPDATE_WORKOUT(state, workout) {
      const i = state.workouts.findIndex(w => w.id === workout.id)
      if (i !== -1) state.workouts.splice(i, 1, workout)
    },
    DELETE_WORKOUT(state, id) {
      state.workouts = state.workouts.filter(w => w.id !== id)
    },

    RESET_ACTIVE_WORKOUT(state) { state.activeWorkout = emptyWorkout() },
    SET_ACTIVE_WORKOUT_FIELD(state, { field, value }) {
      state.activeWorkout[field] = value
    },
    ADD_EXERCISE_TO_ACTIVE(state, exercise) {
      state.activeWorkout.exercises.push({
        exerciseId: exercise.id,
        exerciseName: exercise.name,
        sets: [{ id: uid(), weight: 0, reps: 0, completed: false }]
      })
    },
    REMOVE_EXERCISE_FROM_ACTIVE(state, exerciseId) {
      state.activeWorkout.exercises = state.activeWorkout.exercises.filter(e => e.exerciseId !== exerciseId)
    },
    ADD_SET_TO_EXERCISE(state, exerciseId) {
      const ex = state.activeWorkout.exercises.find(e => e.exerciseId === exerciseId)
      if (!ex) return
      const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
      ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps, completed: false })
    },
    UPDATE_SET(state, { exerciseId, setId, field, value }) {
      const ex = state.activeWorkout.exercises.find(e => e.exerciseId === exerciseId)
      if (!ex) return
      const set = ex.sets.find(s => s.id === setId)
      if (set) set[field] = value
    },
    REMOVE_SET(state, { exerciseId, setId }) {
      const ex = state.activeWorkout.exercises.find(e => e.exerciseId === exerciseId)
      if (!ex) return
      ex.sets = ex.sets.filter(s => s.id !== setId)
    },

    SET_FILTER(state, { key, value }) { state.filters[key] = value },
    RESET_FILTERS(state) {
      state.filters = { dateFrom: null, dateTo: null, type: null, search: '' }
    }
  },

  actions: {
    async initWorkouts({ commit }) {
      const workouts = await workoutService.fetchWorkouts()
      commit('SET_WORKOUTS', workouts)
    },

    async saveWorkout({ commit, state }) {
      const saved = await workoutService.saveWorkout({ ...state.activeWorkout })
      commit('ADD_WORKOUT', saved)
      commit('RESET_ACTIVE_WORKOUT')
      return saved
    },

    async updateWorkout({ commit }, workout) {
      const updated = await workoutService.updateWorkout(workout)
      commit('UPDATE_WORKOUT', updated)
    },

    async deleteWorkout({ commit }, id) {
      await workoutService.deleteWorkout(id)
      commit('DELETE_WORKOUT', id)
    }
  }
}
