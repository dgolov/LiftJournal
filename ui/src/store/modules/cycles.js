import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    cycles: [],
    currentCycle: null,
  }),

  getters: {
    cycleById: state => id => state.cycles.find(c => c.id === id),
  },

  mutations: {
    SET_CYCLES(state, cycles) { state.cycles = cycles },
    SET_CURRENT(state, cycle) { state.currentCycle = cycle },
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
    RESET(state) { state.cycles = []; state.currentCycle = null },
  },

  actions: {
    async fetchCycles({ commit }) {
      const cycles = await workoutService.fetchCycles()
      commit('SET_CYCLES', cycles)
    },

    async fetchCycle({ commit }, id) {
      const cycle = await workoutService.fetchCycle(id)
      commit('SET_CURRENT', cycle)
      return cycle
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
