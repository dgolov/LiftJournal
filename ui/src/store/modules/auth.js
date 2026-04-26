import workoutService from '@/services/workoutService.js'

const TOKEN_KEY = 'gym_auth_token'
const USER_ID_KEY = 'gym_auth_user_id'
const USER_NAME_KEY = 'gym_auth_user_name'

export default {
  namespaced: true,

  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    userId: localStorage.getItem(USER_ID_KEY) ? Number(localStorage.getItem(USER_ID_KEY)) : null,
    userName: localStorage.getItem(USER_NAME_KEY) || null,
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
      localStorage.setItem(USER_ID_KEY, userId)
      localStorage.setItem(USER_NAME_KEY, userName)
    },
    CLEAR_AUTH(state) {
      state.token = null
      state.userId = null
      state.userName = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_ID_KEY)
      localStorage.removeItem(USER_NAME_KEY)
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
      dispatch('social/reset', null, { root: true })
    },
  },
}
