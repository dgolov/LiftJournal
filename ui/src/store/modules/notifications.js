import workoutService from '@/services/workoutService.js'
import { wsClient } from '@/services/wsClient.js'

export default {
  namespaced: true,

  state: () => ({
    unreadCount: 0,
    unread: [],
    all: [],
    allPage: 1,
    allHasMore: false,
    allTotal: 0,
    panelOpen: false,
  }),

  mutations: {
    SET_UNREAD_COUNT(state, n) { state.unreadCount = n },
    SET_UNREAD(state, items) { state.unread = items },
    SET_ALL(state, { items, hasMore, total }) {
      state.all = items; state.allHasMore = hasMore; state.allTotal = total
    },
    APPEND_ALL(state, { items, hasMore, total }) {
      state.all = [...state.all, ...items]; state.allHasMore = hasMore; state.allTotal = total
    },
    SET_ALL_PAGE(state, p) { state.allPage = p },
    MARK_READ(state, id) {
      const fix = (list) => list.map(n => n.id === id ? { ...n, isRead: true } : n)
      state.unread = state.unread.filter(n => n.id !== id)
      state.all = fix(state.all)
      if (state.unreadCount > 0) state.unreadCount--
    },
    MARK_ALL_READ(state) {
      state.unread = []
      state.all = state.all.map(n => ({ ...n, isRead: true }))
      state.unreadCount = 0
    },
    PUSH_NOTIFICATION(state, n) {
      state.unreadCount++
      state.unread = [n, ...state.unread]
      if (state.all.length) state.all = [n, ...state.all]
    },
    SET_PANEL(state, v) { state.panelOpen = v },
    RESET(state) {
      state.unreadCount = 0; state.unread = []; state.all = []
      state.allPage = 1; state.allHasMore = false; state.panelOpen = false
    },
  },

  actions: {
    async fetchUnreadCount({ commit }) {
      try {
        const { count } = await workoutService.fetchUnreadCount()
        commit('SET_UNREAD_COUNT', count)
      } catch { /* unauthenticated or offline */ }
    },

    async fetchUnread({ commit }) {
      const { items } = await workoutService.fetchNotifications({ unreadOnly: true, perPage: 50 })
      commit('SET_UNREAD', items)
    },

    async fetchAll({ commit, state }, reset = false) {
      const page = reset ? 1 : state.allPage
      const { items, hasMore, total } = await workoutService.fetchNotifications({ page, perPage: 20 })
      if (reset || page === 1) {
        commit('SET_ALL', { items, hasMore, total })
        commit('SET_ALL_PAGE', 2)
      } else {
        commit('APPEND_ALL', { items, hasMore, total })
        commit('SET_ALL_PAGE', page + 1)
      }
    },

    async markRead({ commit }, id) {
      await workoutService.markNotificationRead(id)
      commit('MARK_READ', id)
    },

    async markAllRead({ commit, dispatch }) {
      await workoutService.markAllNotificationsRead()
      commit('MARK_ALL_READ')
      dispatch('fetchAll', true)
    },

    openPanel({ commit, dispatch }) {
      commit('SET_PANEL', true)
      dispatch('fetchUnread')
      dispatch('fetchAll', true)
    },

    closePanel({ commit }) {
      commit('SET_PANEL', false)
    },

    startWs({ commit }) {
      wsClient.onNotification((n) => commit('PUSH_NOTIFICATION', n))
      wsClient.connect()
    },

    stopWs() {
      wsClient.disconnect()
    },

    reset({ commit }) {
      wsClient.disconnect()
      commit('RESET')
    },
  },
}
