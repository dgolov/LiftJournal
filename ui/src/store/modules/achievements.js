import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    list: [],      // AchievementOut[]
    loaded: false,
  }),

  getters: {
    all: state => state.list,
    unlocked: state => state.list.filter(a => a.unlocked),
    byCategory: state => category => state.list.filter(a => a.category === category),
    unlockedCount: state => state.list.filter(a => a.unlocked).length,
  },

  mutations: {
    SET_LIST(state, list) { state.list = list; state.loaded = true },
    MERGE_NEWLY_UNLOCKED(state, newly) {
      for (const a of newly) {
        const idx = state.list.findIndex(x => x.id === a.id)
        if (idx !== -1) state.list.splice(idx, 1, a)
      }
    },
  },

  actions: {
    async init({ commit, state }) {
      if (state.loaded) return
      try {
        const list = await workoutService.fetchAchievements()
        commit('SET_LIST', list)
      } catch {
        commit('SET_LIST', [])
      }
    },

    async evaluate({ commit, dispatch, state }) {
      if (!state.loaded) await dispatch('init')
      const newly = await workoutService.evaluateAchievements()
      if (newly.length) {
        commit('MERGE_NEWLY_UNLOCKED', newly)
        for (const a of newly) {
          dispatch('ui/showToast', {
            message: `🏅 Достижение разблокировано: ${a.icon} ${a.title}`,
            type: 'success',
          }, { root: true })
        }
      }
      return newly
    },

    reset({ commit }) {
      commit('SET_LIST', [])
    },
  },
}
