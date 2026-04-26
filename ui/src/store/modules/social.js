import workoutService from '@/services/workoutService.js'

export default {
  namespaced: true,

  state: () => ({
    feed: [],
    feedLoaded: false,
    searchResults: [],
    searching: false,
    profiles: {},
    followers: [],
    following: [],
    comments: {},
    workoutMeta: {},
  }),

  mutations: {
    SET_FEED(state, items) { state.feed = items; state.feedLoaded = true },
    PREPEND_FEED(state, items) { state.feed = [...items, ...state.feed] },
    SET_SEARCH(state, results) { state.searchResults = results },
    SET_SEARCHING(state, v) { state.searching = v },
    SET_PROFILE(state, profile) { state.profiles = { ...state.profiles, [profile.id]: profile } },
    SET_FOLLOWERS(state, list) { state.followers = list },
    SET_FOLLOWING(state, list) { state.following = list },
    UPDATE_FOLLOW(state, { userId, isFollowing, followersCount }) {
      const sr = state.searchResults.find(u => u.id === userId)
      if (sr) sr.isFollowing = isFollowing
      if (state.profiles[userId]) {
        state.profiles[userId].isFollowing = isFollowing
        state.profiles[userId].followersCount = followersCount
      }
      // remove from following list if unfollowed
      if (!isFollowing) state.following = state.following.filter(u => u.id !== userId)
      const fw = state.following.find(u => u.id === userId)
      if (fw) fw.isFollowing = isFollowing
    },
    SET_WORKOUT_META(state, items) {
      const map = { ...state.workoutMeta }
      for (const m of items) map[m.workoutId] = { isLiked: m.isLiked, likesCount: m.likesCount, commentsCount: m.commentsCount }
      state.workoutMeta = map
    },
    UPDATE_LIKE(state, { workoutId, isLiked, likesCount }) {
      const item = state.feed.find(w => w.id === workoutId)
      if (item) { item.isLiked = isLiked; item.likesCount = likesCount }
      if (state.workoutMeta[workoutId]) {
        state.workoutMeta = { ...state.workoutMeta, [workoutId]: { ...state.workoutMeta[workoutId], isLiked, likesCount } }
      }
    },
    SET_COMMENTS(state, { workoutId, comments }) {
      state.comments = { ...state.comments, [workoutId]: comments }
    },
    ADD_COMMENT(state, { workoutId, comment }) {
      if (!state.comments[workoutId]) state.comments[workoutId] = []
      state.comments[workoutId].push(comment)
      const item = state.feed.find(w => w.id === workoutId)
      if (item) item.commentsCount = (item.commentsCount || 0) + 1
    },
    REMOVE_COMMENT(state, { workoutId, commentId }) {
      if (state.comments[workoutId]) {
        state.comments[workoutId] = state.comments[workoutId].filter(c => c.id !== commentId)
      }
      const item = state.feed.find(w => w.id === workoutId)
      if (item && item.commentsCount > 0) item.commentsCount--
    },
    RESET(state) {
      state.feed = []; state.feedLoaded = false; state.searchResults = []
      state.profiles = {}; state.followers = []; state.following = []; state.comments = {}; state.workoutMeta = {}
    },
  },

  actions: {
    async fetchFeed({ commit }, { append = false, offset = 0 } = {}) {
      const items = await workoutService.fetchFeed(30, offset)
      if (append) commit('PREPEND_FEED', items)
      else commit('SET_FEED', items)
      return items
    },

    async searchUsers({ commit }, query) {
      if (!query || query.trim().length < 2) { commit('SET_SEARCH', []); return }
      commit('SET_SEARCHING', true)
      try {
        const results = await workoutService.searchUsers(query)
        commit('SET_SEARCH', results)
      } finally {
        commit('SET_SEARCHING', false)
      }
    },

    async getProfile({ commit }, userId) {
      const profile = await workoutService.getPublicProfile(userId)
      commit('SET_PROFILE', profile)
      return profile
    },

    async fetchFollowers({ commit }) {
      const list = await workoutService.fetchMyFollowers()
      commit('SET_FOLLOWERS', list)
      return list
    },

    async fetchFollowing({ commit }) {
      const list = await workoutService.fetchMyFollowing()
      commit('SET_FOLLOWING', list)
      return list
    },

    async follow({ commit }, userId) {
      const status = await workoutService.followUser(userId)
      commit('UPDATE_FOLLOW', { userId, ...status })
      return status
    },

    async unfollow({ commit }, userId) {
      const status = await workoutService.unfollowUser(userId)
      commit('UPDATE_FOLLOW', { userId, ...status })
      return status
    },

    async fetchWorkoutsMeta({ commit }, ids) {
      if (!ids?.length) return
      const items = await workoutService.fetchWorkoutsMeta(ids)
      commit('SET_WORKOUT_META', items)
    },

    async toggleLike({ commit }, workoutId) {
      const status = await workoutService.toggleLike(workoutId)
      commit('UPDATE_LIKE', { workoutId, ...status })
      return status
    },

    async fetchComments({ commit }, workoutId) {
      const comments = await workoutService.getComments(workoutId)
      commit('SET_COMMENTS', { workoutId, comments })
      return comments
    },

    async addComment({ commit }, { workoutId, text }) {
      const comment = await workoutService.addComment(workoutId, text)
      commit('ADD_COMMENT', { workoutId, comment })
      return comment
    },

    async deleteComment({ commit }, { workoutId, commentId }) {
      await workoutService.deleteComment(workoutId, commentId)
      commit('REMOVE_COMMENT', { workoutId, commentId })
    },

    reset({ commit }) { commit('RESET') },
  },
}
