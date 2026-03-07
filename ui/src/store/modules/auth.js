import workoutService from '@/services/workoutService.js'

const TOKEN_KEY = 'gym_auth_token'

export default {
  namespaced: true,

  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    userId: null,
    userName: null,
  }),

  getters: {
    isAuthenticated: state => !!state.token,
    token: state => state.token,
    userName: state => state.userName,
  },

  mutations: {
    SET_AUTH(state, { token, userId, userName }) {
      state.token = token
      state.userId = userId
      state.userName = userName
      localStorage.setItem(TOKEN_KEY, token)
    },
    CLEAR_AUTH(state) {
      state.token = null
      state.userId = null
      state.userName = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },

  actions: {
    async login({ commit }, credentials) {
      const res = await workoutService.login(credentials)
      commit('SET_AUTH', { token: res.access_token, userId: res.user_id, userName: res.name })
      return res
    },

    async register({ commit }, data) {
      const res = await workoutService.register(data)
      commit('SET_AUTH', { token: res.access_token, userId: res.user_id, userName: res.name })
      return res
    },

    logout({ commit, dispatch }) {
      commit('CLEAR_AUTH')
      // Clear user data from other modules
      dispatch('workouts/reset', null, { root: true })
      dispatch('user/reset', null, { root: true })
    },
  },
}
