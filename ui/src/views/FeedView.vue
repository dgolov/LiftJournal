<template>
  <div class="space-y-4">
    <!-- Search bar -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      <input
        v-model="searchQuery"
        class="input pl-9 w-full"
        placeholder="Найти пользователей…"
        @input="onSearch"
      />
      <button v-if="searchQuery" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" @click="clearSearch">
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Search results -->
    <div v-if="searchQuery" class="card divide-y divide-gray-100 dark:divide-gray-800">
      <div v-if="searching" class="p-4 text-center text-sm text-gray-400">Поиск…</div>
      <div v-else-if="!searchResults.length" class="p-4 text-center text-sm text-gray-400">Никого не найдено</div>
      <div
        v-for="user in searchResults"
        :key="user.id"
        class="flex items-center gap-3 p-3"
      >
        <RouterLink :to="`/users/${user.id}`" class="flex items-center gap-3 flex-1 min-w-0" @click="clearSearch">
          <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold flex-shrink-0">
            {{ user.name.charAt(0).toUpperCase() }}
          </div>
          <span class="font-medium text-gray-900 dark:text-white truncate">{{ user.name }}</span>
        </RouterLink>
        <BaseButton
          :variant="user.isFollowing ? 'outline' : 'primary'"
          size="sm"
          @click="toggleFollow(user)"
        >{{ user.isFollowing ? 'Отписаться' : 'Подписаться' }}</BaseButton>
      </div>
    </div>

    <!-- Feed -->
    <template v-else>
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="card p-4 animate-pulse">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-9 h-9 rounded-full bg-gray-200 dark:bg-gray-700" />
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32" />
          </div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
          <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
        </div>
      </div>

      <BaseEmptyState
        v-else-if="!feed.length"
        title="Лента пуста"
        description="Найдите и добавьте других пользователей, чтобы видеть их тренировки"
      >
        <template #icon><Users class="w-12 h-12" /></template>
      </BaseEmptyState>

      <div v-else>
        <div v-for="item in feed" :key="item.id" class="card overflow-hidden">
          <!-- User row -->
          <RouterLink :to="`/users/${item.userId}`" class="flex items-center gap-3 px-4 pt-4 pb-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div class="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0">
              {{ item.userName.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ item.userName }}</p>
              <p class="text-xs text-gray-400">{{ formatDate(item.date) }}</p>
            </div>
            <BaseBadge :color="typeColor(item.type)">{{ item.type }}</BaseBadge>
          </RouterLink>

          <!-- Workout info -->
          <RouterLink :to="`/workouts/${item.id}`" class="block px-4 pb-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <p class="font-semibold text-gray-900 dark:text-white mb-1">{{ item.title || 'Тренировка' }}</p>
            <p class="text-xs text-gray-500 mb-2">
              <span v-if="item.durationMinutes">{{ item.durationMinutes }} мин · </span>
              {{ item.exercises.length }} упр. ·
              {{ totalSets(item) }} подх.
              <span v-if="totalVolume(item)"> · {{ totalVolume(item) }} кг</span>
            </p>
            <div v-if="item.exercises.length" class="flex flex-wrap gap-1.5">
              <span
                v-for="ex in item.exercises.slice(0, 4)"
                :key="ex.exerciseId"
                class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
              >{{ ex.exerciseName }}</span>
              <span v-if="item.exercises.length > 4" class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-400">
                +{{ item.exercises.length - 4 }}
              </span>
            </div>
          </RouterLink>

          <!-- Like & Comment row -->
          <div class="flex items-center gap-5 px-4 py-2.5 border-t border-gray-100 dark:border-gray-800">
            <button
              class="flex items-center gap-1.5 text-sm transition-colors"
              :class="item.isLiked ? 'text-red-500' : 'text-gray-400 hover:text-red-400'"
              @click.prevent="toggleLike(item)"
            >
              <Heart :class="['w-4 h-4 transition-all', item.isLiked ? 'fill-current scale-110' : '']" />
              <span>{{ item.likesCount || 0 }}</span>
            </button>
            <RouterLink
              :to="`/workouts/${item.id}`"
              class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary transition-colors"
            >
              <MessageCircle class="w-4 h-4" />
              <span>{{ item.commentsCount || 0 }}</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Search, X, Users, Heart, MessageCircle } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'

const store = useStore()
const loading = ref(false)
const searchQuery = ref('')
let searchTimer = null

const feed = computed(() => store.state.social.feed)
const searchResults = computed(() => store.state.social.searchResults)
const searching = computed(() => store.state.social.searching)

onMounted(async () => {
  if (!store.state.social.feedLoaded) {
    loading.value = true
    try { await store.dispatch('social/fetchFeed') }
    finally { loading.value = false }
  }
})

function onSearch() {
  clearTimeout(searchTimer)
  if (!searchQuery.value.trim()) { store.commit('social/SET_SEARCH', []); return }
  searchTimer = setTimeout(() => store.dispatch('social/searchUsers', searchQuery.value), 350)
}

function clearSearch() {
  searchQuery.value = ''
  store.commit('social/SET_SEARCH', [])
}

async function toggleLike(item) {
  await store.dispatch('social/toggleLike', item.id)
}

async function toggleFollow(user) {
  if (user.isFollowing) {
    await store.dispatch('social/unfollow', user.id)
  } else {
    await store.dispatch('social/follow', user.id)
  }
}

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
function typeColor(t) { return typeColorMap[t] || 'gray' }

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

function totalSets(item) {
  return item.exercises.reduce((s, ex) => s + ex.sets.length, 0)
}

function totalVolume(item) {
  const v = item.exercises.reduce((s, ex) =>
    s + ex.sets.filter(s => !s.failed).reduce((a, set) => a + set.weight * set.reps, 0), 0)
  return v > 0 ? v : null
}
</script>
