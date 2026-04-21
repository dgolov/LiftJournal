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
    upcomingByGroup: state => (groupId, fromDate) =>
      state.plannedWorkouts.filter(
        w => w.recurrenceGroupId === groupId && w.scheduledDate >= fromDate && w.status === 'planned'
      ),
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

    // Create a recurring series: generates `weeks` occurrences every 7 days
    async createRecurringPlan({ dispatch }, { payload, weeks }) {
      const groupId = `rg-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
      const base = new Date(payload.scheduledDate + 'T00:00:00')
      const created = []
      for (let i = 0; i < weeks; i++) {
        const d = new Date(base)
        d.setDate(base.getDate() + i * 7)
        const dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        const item = await dispatch('createPlannedWorkout', {
          ...payload,
          scheduledDate: dateStr,
          recurrenceGroupId: groupId,
        })
        created.push(item)
      }
      return created
    },

    // Cancel this occurrence and all future ones in the same group
    async deleteUpcomingRecurring({ getters, dispatch }, plan) {
      const toDelete = getters.upcomingByGroup(plan.recurrenceGroupId, plan.scheduledDate)
      await Promise.all(toDelete.map(p => dispatch('deletePlannedWorkout', p.id)))
    },

    async skipUpcomingRecurring({ getters, dispatch }, plan) {
      const toSkip = getters.upcomingByGroup(plan.recurrenceGroupId, plan.scheduledDate)
      await Promise.all(toSkip.map(p => dispatch('skipPlannedWorkout', p.id)))
    },
  }
}
