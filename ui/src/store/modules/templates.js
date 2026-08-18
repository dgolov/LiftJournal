import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    templates: [],
  }),

  getters: {
    all: state => state.templates,
  },

  mutations: {
    SET_TEMPLATES(state, list) { state.templates = list },
    ADD_TEMPLATE(state, t) { state.templates.unshift(t) },
    UPDATE_TEMPLATE(state, t) {
      const i = state.templates.findIndex(x => x.id === t.id)
      if (i !== -1) state.templates.splice(i, 1, t)
    },
    DELETE_TEMPLATE(state, id) {
      state.templates = state.templates.filter(t => t.id !== id)
    },
  },

  actions: {
    async fetchTemplates({ commit }) {
      const list = await workoutService.fetchTemplates()
      commit('SET_TEMPLATES', list)
    },

    async createTemplate({ commit }, data) {
      const created = await workoutService.createTemplate(data)
      commit('ADD_TEMPLATE', created)
      return created
    },

    async updateTemplate({ commit }, { id, ...data }) {
      const updated = await workoutService.updateTemplate(id, data)
      commit('UPDATE_TEMPLATE', updated)
      return updated
    },

    async deleteTemplate({ commit }, id) {
      await workoutService.deleteTemplate(id)
      commit('DELETE_TEMPLATE', id)
    },
  }
}
