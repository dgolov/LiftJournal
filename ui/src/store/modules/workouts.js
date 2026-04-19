import workoutService from '@/services/workoutService.js'

// ── Session persistence ───────────────────────────────────────────────────────
const SESSION_KEY = 'gym_workout_session'

export function loadSession() {
  try { return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null') } catch { return null }
}
export function saveSession(startedAt, draft, cycleContext = null, planContext = null) {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ startedAt, draft, cycleContext, planContext }))
}
export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}
// ─────────────────────────────────────────────────────────────────────────────

function calcVolume(workout) {
  return workout.exercises.reduce((total, ex) => {
    return total + ex.sets.reduce((s, set) => s + (set.failed ? 0 : set.weight * set.reps), 0)
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
    durationMinutes: 0,
    notes: '',
    exercises: []
  }
}

export default {
  namespaced: true,

  state: () => {
    const session = loadSession()
    return {
      workouts: [],
      activeWorkout: session?.draft || emptyWorkout(),
      workoutStartedAt: session?.startedAt || null,
      cycleContext: session?.cycleContext || null,
      planContext: session?.planContext || null,
      filters: {
        dateFrom: null,
        dateTo: null,
        type: null,
        search: ''
      }
    }
  },

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

    SET_WORKOUT_STARTED_AT(state, ts) { state.workoutStartedAt = ts },

    RESET_ACTIVE_WORKOUT(state) {
      state.activeWorkout = emptyWorkout()
      state.workoutStartedAt = null
      state.cycleContext = null
      state.planContext = null
      clearSession()
    },
    SET_CYCLE_CONTEXT(state, ctx) { state.cycleContext = ctx },
    SET_PLAN_CONTEXT(state, ctx) { state.planContext = ctx },
    SET_ACTIVE_WORKOUT_EXERCISES(state, exercises) { state.activeWorkout.exercises = exercises },
    REORDER_EXERCISES(state, exercises) { state.activeWorkout.exercises = exercises },
    SET_ACTIVE_WORKOUT_FIELD(state, { field, value }) {
      state.activeWorkout[field] = value
    },
    ADD_EXERCISE_TO_ACTIVE(state, { exercise, sets }) {
      state.activeWorkout.exercises.push({
        exerciseId: exercise.id,
        exerciseName: exercise.name,
        sets
      })
    },
    REMOVE_EXERCISE_FROM_ACTIVE(state, exerciseId) {
      state.activeWorkout.exercises = state.activeWorkout.exercises.filter(e => e.exerciseId !== exerciseId)
    },
    ADD_SET_TO_EXERCISE(state, exerciseId) {
      const ex = state.activeWorkout.exercises.find(e => e.exerciseId === exerciseId)
      if (!ex) return
      const last = ex.sets[ex.sets.length - 1] || { weight: 0, reps: 0 }
      ex.sets.push({ id: uid(), weight: last.weight, reps: last.reps, completed: false, failed: false })
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
    addExerciseToActive({ commit, state }, exercise) {
      const sorted = [...state.workouts].sort((a, b) => b.date.localeCompare(a.date))
      let lastSets = null
      for (const w of sorted) {
        const ex = w.exercises.find(e => e.exerciseId === exercise.id)
        const validSets = ex?.sets?.filter(s => !s.failed)
        if (validSets?.length) { lastSets = validSets; break }
      }
      const sets = lastSets
        ? lastSets.map(s => ({ id: uid(), weight: s.weight, reps: s.reps, completed: false, failed: false }))
        : [{ id: uid(), weight: 0, reps: 0, completed: false, failed: false }]
      commit('ADD_EXERCISE_TO_ACTIVE', { exercise, sets })
    },

    async initWorkouts({ commit }) {
      const workouts = await workoutService.fetchWorkouts()
      commit('SET_WORKOUTS', workouts)
    },

    startWorkout({ commit, state }) {
      const ts = Date.now()
      commit('SET_WORKOUT_STARTED_AT', ts)
      saveSession(ts, state.activeWorkout, state.cycleContext, state.planContext)
    },

    startWorkoutFromHistory({ commit }, workout) {
      commit('RESET_ACTIVE_WORKOUT')
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'title', value: workout.title })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'type', value: workout.type })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'date', value: new Date().toISOString().split('T')[0] })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'notes', value: workout.notes || '' })
      commit('SET_ACTIVE_WORKOUT_EXERCISES', workout.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({ id: s.id, weight: s.weight, reps: s.reps, completed: false, failed: false })),
      })))
      // startWorkout не вызываем — пользователь попадёт на шаг 0 и сможет
      // отредактировать название и заметки перед началом
    },

    startWorkoutFromPlan({ commit, dispatch }, plannedWorkout) {
      commit('RESET_ACTIVE_WORKOUT')
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'title', value: plannedWorkout.title })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'type', value: plannedWorkout.type })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'date', value: new Date().toISOString().split('T')[0] })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'notes', value: plannedWorkout.notes || '' })
      commit('SET_ACTIVE_WORKOUT_EXERCISES', plannedWorkout.exercises.map(ex => ({
        exerciseId: ex.exerciseId,
        exerciseName: ex.exerciseName,
        sets: ex.sets.map(s => ({ ...s, completed: false })),
      })))
      commit('SET_PLAN_CONTEXT', { planId: plannedWorkout.id })
      dispatch('startWorkout')
    },

    startWorkoutFromCycle({ commit, dispatch, rootState }, { cycleWorkout, cycleTitle, runId, cycleWorkoutId, cycleId }) {
      const maxes = rootState.user.maxes
      const exercises = cycleWorkout.exercises.map(ex => {
        const maxKg = maxes.find(m => m.exercise_name === ex.exercise_name)?.weight_kg ?? null
        const exerciseId = ex.exercise_id
          ?? rootState.exercises.library.find(e => e.name === ex.exercise_name)?.id
          ?? `cycle-${ex.id}`
        return {
          exerciseId,
          exerciseName: ex.exercise_name,
          sets: ex.sets.map(s => ({
            id: uid(),
            weight: maxKg ? Math.round(maxKg * s.percent_1rm / 100 / 2.5) * 2.5 : 0,
            reps: s.reps,
            completed: false,
          })),
        }
      })
      commit('RESET_ACTIVE_WORKOUT')
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'title', value: `Тренировка ${cycleWorkout.workout_number} — ${cycleTitle}` })
      commit('SET_ACTIVE_WORKOUT_FIELD', { field: 'type', value: 'Силовая' })
      commit('SET_ACTIVE_WORKOUT_EXERCISES', exercises)
      commit('SET_CYCLE_CONTEXT', { runId, cycleWorkoutId, cycleId })
      dispatch('startWorkout')
    },

    async saveWorkout({ commit, state, dispatch }) {
      const durationMinutes = state.workoutStartedAt
        ? Math.max(1, Math.round((Date.now() - state.workoutStartedAt) / 60000))
        : state.activeWorkout.durationMinutes
      const saved = await workoutService.saveWorkout({ ...state.activeWorkout, durationMinutes })
      commit('ADD_WORKOUT', saved)
      const cycleId = state.cycleContext?.cycleId ?? null
      if (state.cycleContext) {
        await dispatch('cycles/completeCycleWorkout', {
          runId: state.cycleContext.runId,
          cycleWorkoutId: state.cycleContext.cycleWorkoutId,
          workoutId: saved.id,
        }, { root: true })
      }
      if (state.planContext) {
        try {
          await dispatch('planned/completePlannedWorkout', {
            id: state.planContext.planId,
            completedWorkoutId: saved.id,
          }, { root: true })
        } catch (e) {
          console.warn('Could not mark plan as completed:', e.message)
        }
      }
      commit('RESET_ACTIVE_WORKOUT')
      return { workout: saved, cycleId }
    },

    async autoSaveMidnight({ commit, dispatch }, { draft, startedAt }) {
      const start = new Date(startedAt)
      const midnight = new Date(start)
      midnight.setDate(midnight.getDate() + 1)
      midnight.setHours(0, 0, 0, 0)
      const durationMinutes = Math.max(1, Math.round((midnight - start) / 60000))
      try {
        const saved = await workoutService.saveWorkout({ ...draft, durationMinutes })
        commit('ADD_WORKOUT', saved)
      } catch (e) {
        console.error('Midnight auto-save failed', e)
      }
      commit('RESET_ACTIVE_WORKOUT')
      dispatch('ui/showToast', { message: 'Тренировка автоматически завершена в 00:00', type: 'info' }, { root: true })
    },

    async updateWorkout({ commit }, workout) {
      const updated = await workoutService.updateWorkout(workout)
      commit('UPDATE_WORKOUT', updated)
    },

    async deleteWorkout({ commit }, id) {
      await workoutService.deleteWorkout(id)
      commit('DELETE_WORKOUT', id)
    },

    reset({ commit }) {
      commit('SET_WORKOUTS', [])
      commit('RESET_ACTIVE_WORKOUT')
    }
  }
}
