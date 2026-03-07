import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    profile: { name: '', age: 0, avatarUrl: null },
    weightLog: [],
    goals: []
  }),

  getters: {
    currentWeight: state => {
      if (!state.weightLog.length) return null
      return [...state.weightLog].sort((a, b) => b.date.localeCompare(a.date))[0]
    },
    weightHistory: state => [...state.weightLog].sort((a, b) => a.date.localeCompare(b.date)),
    activeGoals: state => state.goals.filter(g => !g.done),
    completedGoals: state => state.goals.filter(g => g.done)
  },

  mutations: {
    SET_USER(state, user) {
      state.profile = { name: user.name, age: user.age, avatarUrl: user.avatarUrl }
      state.weightLog = user.weightLog
      state.goals = user.goals
    },
    UPDATE_PROFILE(state, profile) {
      state.profile = { ...state.profile, ...profile }
    },
    ADD_WEIGHT_ENTRY(state, entry) {
      state.weightLog = state.weightLog.filter(e => e.date !== entry.date)
      state.weightLog = [...state.weightLog, entry].sort((a, b) => a.date.localeCompare(b.date))
    },
    DELETE_WEIGHT_ENTRY(state, date) {
      state.weightLog = state.weightLog.filter(e => e.date !== date)
    },
    ADD_GOAL(state, goal) { state.goals.push(goal) },
    TOGGLE_GOAL(state, id) {
      const g = state.goals.find(g => g.id === id)
      if (g) g.done = !g.done
    },
    DELETE_GOAL(state, id) { state.goals = state.goals.filter(g => g.id !== id) }
  },

  actions: {
    async initUser({ commit }) {
      const user = await workoutService.fetchUser()
      commit('SET_USER', user)
    },

    async updateProfile({ commit }, profile) {
      await workoutService.updateProfile(profile)
      commit('UPDATE_PROFILE', profile)
    },

    async logWeight({ commit }, entry) {
      await workoutService.logWeight(entry)
      commit('ADD_WEIGHT_ENTRY', entry)
    },

    async deleteWeightEntry({ commit }, date) {
      await workoutService.deleteWeightEntry(date)
      commit('DELETE_WEIGHT_ENTRY', date)
    },

    async saveGoal({ commit }, goalData) {
      const saved = await workoutService.saveGoal(goalData)
      commit('ADD_GOAL', saved)
    },

    async toggleGoal({ commit }, id) {
      await workoutService.toggleGoal(id)
      commit('TOGGLE_GOAL', id)
    },

    async deleteGoal({ commit }, id) {
      await workoutService.deleteGoal(id)
      commit('DELETE_GOAL', id)
    },

    reset({ commit }) {
      commit('SET_USER', { name: '', age: 0, avatarUrl: null, weightLog: [], goals: [] })
    }
  }
}
