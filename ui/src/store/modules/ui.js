let toastId = 0

export default {
  namespaced: true,

  state: () => ({
    sidebarOpen: false,
    activeModal: null,
    modalPayload: null,
    toasts: [],
    pendingRequests: 0
  }),

  getters: {
    isLoading: state => state.pendingRequests > 0
  },

  mutations: {
    TOGGLE_SIDEBAR(state) { state.sidebarOpen = !state.sidebarOpen },
    SET_SIDEBAR(state, val) { state.sidebarOpen = val },
    OPEN_MODAL(state, { name, payload = null }) {
      state.activeModal = name
      state.modalPayload = payload
    },
    CLOSE_MODAL(state) {
      state.activeModal = null
      state.modalPayload = null
    },
    ADD_TOAST(state, toast) { state.toasts.push(toast) },
    REMOVE_TOAST(state, id) { state.toasts = state.toasts.filter(t => t.id !== id) },
    INC_PENDING(state) { state.pendingRequests++ },
    DEC_PENDING(state) { state.pendingRequests = Math.max(0, state.pendingRequests - 1) }
  },

  actions: {
    showToast({ commit }, { message, type = 'success', duration = 3000 }) {
      const id = ++toastId
      commit('ADD_TOAST', { id, message, type })
      setTimeout(() => commit('REMOVE_TOAST', id), duration)
    }
  }
}
