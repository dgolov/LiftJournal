import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    plannedWorkouts: [],
  }),

  getters: {
    all: state => [...state.plannedWorkouts].sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate)),
    upcoming: (state, getters) => getters.all.filter(w => w.status === 'planned'),
    byId: state => id => state.plannedWorkouts.find(w => w.id === id),
  },

  mutations: {
    SET_PLANNED(state, list) { state.plannedWorkouts = list },
    ADD_PLANNED(state, w) { state.plannedWorkouts.push(w) },
    UPDATE_PLANNED(state, w) {
      const i = state.plannedWorkouts.findIndex(p => p.id === w.id)
      if (i !== -1) state.plannedWorkouts.splice(i, 1, w)
    },
    DELETE_PLANNED(state, id) {
      state.plannedWorkouts = state.plannedWorkouts.filter(w => w.id !== id)
    },
  },

  actions: {
    async fetchPlannedWorkouts({ commit }) {
      try {
        const list = await workoutService.fetchPlannedWorkouts()
        commit('SET_PLANNED', list)
      } catch (e) {
        console.warn('Planned workouts API not available:', e.message)
      }
    },

    async createPlannedWorkout({ commit }, data) {
      const created = await workoutService.createPlannedWorkout(data)
      commit('ADD_PLANNED', created)
      return created
    },

    async updatePlannedWorkout({ commit }, { id, ...data }) {
      const updated = await workoutService.updatePlannedWorkout(id, data)
      commit('UPDATE_PLANNED', updated)
      return updated
    },

    async deletePlannedWorkout({ commit }, id) {
      await workoutService.deletePlannedWorkout(id)
      commit('DELETE_PLANNED', id)
    },

    async skipPlannedWorkout({ dispatch }, id) {
      return dispatch('updatePlannedWorkout', { id, status: 'skipped' })
    },

    async completePlannedWorkout({ dispatch }, { id, completedWorkoutId }) {
      return dispatch('updatePlannedWorkout', { id, status: 'completed', completedWorkoutId })
    },
  }
}
