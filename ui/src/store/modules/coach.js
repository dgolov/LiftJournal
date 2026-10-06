import workoutService from '@/services/workoutService.js'

// A link is "pending" until the side that did NOT start it answers — so for
// the current user a pending link is either waiting on them (incoming) or on
// the other person (outgoing).
function isIncoming(link, userId) {
  const initiatorId = link.initiatedBy === 'coach' ? link.coachId : link.athleteId
  return initiatorId !== userId
}

export default {
  namespaced: true,

  state: () => ({
    links: [],          // every link I'm on, either side
    athletes: [],       // active athletes with weekly summary (coach side)
    athleteData: {},    // athleteId → { summary, workouts, planned, maxes, maxesHidden }
  }),

  getters: {
    incomingRequests: (state, _g, rootState) =>
      state.links.filter(l => l.status === 'pending' && isIncoming(l, rootState.auth.userId)),
    outgoingRequests: (state, _g, rootState) =>
      state.links.filter(l => l.status === 'pending' && !isIncoming(l, rootState.auth.userId)),
    // Coaches currently coaching me.
    myCoaches: (state, _g, rootState) =>
      state.links.filter(l => l.status === 'active' && l.athleteId === rootState.auth.userId),
    athleteById: state => id => state.athleteData[id] || null,
  },

  mutations: {
    SET_LINKS(state, links) { state.links = links },
    UPSERT_LINK(state, link) {
      const i = state.links.findIndex(l => l.id === link.id)
      if (i !== -1) state.links.splice(i, 1, link)
      else state.links.unshift(link)
    },
    REMOVE_LINK(state, id) { state.links = state.links.filter(l => l.id !== id) },
    SET_ATHLETES(state, athletes) { state.athletes = athletes },
    SET_ATHLETE_DATA(state, { id, data }) {
      state.athleteData = { ...state.athleteData, [id]: data }
    },
    UPSERT_ATHLETE_PLAN(state, { athleteId, plan }) {
      const data = state.athleteData[athleteId]
      if (!data) return
      const planned = data.planned.filter(p => p.id !== plan.id)
      planned.push(plan)
      planned.sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
      state.athleteData = { ...state.athleteData, [athleteId]: { ...data, planned } }
    },
    REMOVE_ATHLETE_PLAN(state, { athleteId, planId }) {
      const data = state.athleteData[athleteId]
      if (!data) return
      state.athleteData = {
        ...state.athleteData,
        [athleteId]: { ...data, planned: data.planned.filter(p => p.id !== planId) },
      }
    },
    RESET(state) {
      state.links = []
      state.athletes = []
      state.athleteData = {}
    },
  },

  actions: {
    async fetchLinks({ commit }) {
      commit('SET_LINKS', await workoutService.fetchCoachLinks({ status: ['pending', 'active'] }))
    },

    async fetchAthletes({ commit }) {
      commit('SET_ATHLETES', await workoutService.fetchAthletes())
    },

    async invite({ commit }, { athleteId, message }) {
      const link = await workoutService.inviteAthlete(athleteId, message)
      commit('UPSERT_LINK', link)
      return link
    },

    async request({ commit }, { coachId, message }) {
      const link = await workoutService.requestCoach(coachId, message)
      commit('UPSERT_LINK', link)
      return link
    },

    async accept({ commit, dispatch }, linkId) {
      const link = await workoutService.acceptCoachLink(linkId)
      commit('UPSERT_LINK', link)
      dispatch('notifications/setCoachLinkStatus', { linkId, status: link.status }, { root: true })
      return link
    },

    async decline({ commit, dispatch }, linkId) {
      const link = await workoutService.declineCoachLink(linkId)
      commit('REMOVE_LINK', linkId)
      dispatch('notifications/setCoachLinkStatus', { linkId, status: link.status }, { root: true })
      return link
    },

    async cancel({ commit }, linkId) {
      await workoutService.cancelCoachLink(linkId)
      commit('REMOVE_LINK', linkId)
    },

    async end({ commit, state }, linkId) {
      const link = await workoutService.endCoachLink(linkId)
      commit('REMOVE_LINK', linkId)
      commit('SET_ATHLETES', state.athletes.filter(a => a.linkId !== linkId))
      return link
    },

    async updatePermissions({ commit }, { linkId, ...perms }) {
      const link = await workoutService.updateCoachLinkPermissions(linkId, perms)
      commit('UPSERT_LINK', link)
      return link
    },

    // Everything the coach screens need for one athlete, loaded in one go:
    // full history is required anyway for the 1RM baseline behind relative
    // intensity. Maxes are optional — the athlete may have hidden them.
    async loadAthlete({ commit, state }, { id, force = false }) {
      if (state.athleteData[id] && !force) return state.athleteData[id]
      const [summary, workouts, planned, maxesResult] = await Promise.all([
        workoutService.fetchAthlete(id),
        workoutService.fetchAthleteWorkouts(id),
        workoutService.fetchAthletePlanned(id),
        workoutService.fetchAthleteMaxes(id).then(m => ({ maxes: m }), e => {
          if (e?.status === 403) return { maxes: [], hidden: true }
          throw e
        }),
      ])
      const data = { summary, workouts, planned, maxes: maxesResult.maxes, maxesHidden: !!maxesResult.hidden }
      commit('SET_ATHLETE_DATA', { id, data })
      return data
    },

    async createPlan({ commit }, { athleteId, payload }) {
      const plan = await workoutService.createAthletePlan(athleteId, payload)
      commit('UPSERT_ATHLETE_PLAN', { athleteId, plan })
      return plan
    },

    async createRecurringPlan({ dispatch }, { athleteId, payload, weeks }) {
      const base = new Date(payload.scheduledDate + 'T00:00:00')
      const created = []
      for (let i = 0; i < weeks; i++) {
        const d = new Date(base)
        d.setDate(base.getDate() + i * 7)
        const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
        created.push(await dispatch('createPlan', { athleteId, payload: { ...payload, scheduledDate: dateStr } }))
      }
      return created
    },

    async updatePlan({ commit }, { athleteId, planId, payload }) {
      const plan = await workoutService.updateAthletePlan(athleteId, planId, payload)
      commit('UPSERT_ATHLETE_PLAN', { athleteId, plan })
      return plan
    },

    async deletePlan({ commit }, { athleteId, planId }) {
      await workoutService.deleteAthletePlan(athleteId, planId)
      commit('REMOVE_ATHLETE_PLAN', { athleteId, planId })
    },

    reset({ commit }) {
      commit('RESET')
    },
  },
}
