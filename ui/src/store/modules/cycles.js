import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    cycles: [],
    currentCycle: null,
    currentRun: null,
    anyActiveRun: null,  // active run across ALL cycles (null if none)
  }),

  getters: {
    cycleById: state => id => state.cycles.find(c => c.id === id),
    hasActiveRun: state => !!state.anyActiveRun,
    activeRunCycleId: state => state.anyActiveRun?.cycle_id ?? null,
    completedWorkoutIds: state => {
      if (!state.currentRun) return new Set()
      return new Set(state.currentRun.logs.filter(l => l.completed_at).map(l => l.cycle_workout_id))
    },
    logByCycleWorkoutId: state => id => state.currentRun?.logs.find(l => l.cycle_workout_id === id) ?? null,
  },

  mutations: {
    SET_CYCLES(state, cycles) { state.cycles = cycles },
    SET_CURRENT(state, cycle) { state.currentCycle = cycle },
    SET_RUN(state, run) { state.currentRun = run },
    SET_ANY_ACTIVE_RUN(state, run) { state.anyActiveRun = run },
    ADD_CYCLE(state, cycle) { state.cycles.unshift(cycle) },
    UPDATE_CYCLE(state, cycle) {
      const i = state.cycles.findIndex(c => c.id === cycle.id)
      if (i !== -1) state.cycles.splice(i, 1, cycle)
      if (state.currentCycle?.id === cycle.id) state.currentCycle = cycle
    },
    DELETE_CYCLE(state, id) {
      state.cycles = state.cycles.filter(c => c.id !== id)
      if (state.currentCycle?.id === id) state.currentCycle = null
    },
    RESET(state) { state.cycles = []; state.currentCycle = null; state.currentRun = null; state.anyActiveRun = null },
  },

  actions: {
    async fetchCycles({ commit }) {
      const [cycles, anyRun] = await Promise.all([
        workoutService.fetchCycles(),
        workoutService.fetchAnyActiveRun().catch(() => null),
      ])
      commit('SET_CYCLES', cycles)
      commit('SET_ANY_ACTIVE_RUN', anyRun ?? null)
    },

    async fetchCycle({ commit }, id) {
      const cycle = await workoutService.fetchCycle(id)
      commit('SET_CURRENT', cycle)
      return cycle
    },

    async fetchCycleRun({ commit }, cycleId) {
      const run = await workoutService.fetchCycleRun(cycleId)
      commit('SET_RUN', run)
      return run
    },

    async startCycleRun({ commit }, cycleId) {
      const run = await workoutService.startCycleRun(cycleId)
      commit('SET_RUN', run)
      commit('SET_ANY_ACTIVE_RUN', run)
      return run
    },

    async startCycleWorkout(_, { runId, cycleWorkoutId, notes }) {
      return workoutService.startCycleWorkout(runId, cycleWorkoutId, notes)
    },

    async completeCycleWorkout({ commit }, { runId, cycleWorkoutId, workoutId }) {
      const run = await workoutService.completeCycleWorkout(runId, cycleWorkoutId, workoutId)
      commit('SET_RUN', run)
      return run
    },

    async finishCycleRun({ commit }, runId) {
      await workoutService.finishCycleRun(runId)
      commit('SET_RUN', null)
      commit('SET_ANY_ACTIVE_RUN', null)
    },

    async createCycle({ commit }, data) {
      const cycle = await workoutService.createCycle(data)
      commit('ADD_CYCLE', { ...cycle, workout_count: cycle.workouts?.length ?? 0 })
      return cycle
    },

    async updateCycle({ commit }, { id, data }) {
      const cycle = await workoutService.updateCycle(id, data)
      commit('UPDATE_CYCLE', cycle)
      return cycle
    },

    async deleteCycle({ commit, dispatch }, id) {
      await workoutService.deleteCycle(id)
      commit('DELETE_CYCLE', id)
      dispatch('ui/showToast', { message: 'Цикл удалён', type: 'success' }, { root: true })
    },

    reset({ commit }) { commit('RESET') },
  },
}
