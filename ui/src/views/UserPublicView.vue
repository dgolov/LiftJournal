<template>
  <div>
    <button class="flex items-center gap-1 text-sm text-gray-500 hover:text-primary mb-4 transition-colors" @click="$router.back()">
      <ChevronLeft class="w-4 h-4" /> Назад
    </button>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card p-6 animate-pulse flex items-center gap-4 mb-4">
      <div class="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
      <div class="flex-1 space-y-2">
        <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-40" />
        <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-56" />
      </div>
    </div>

    <template v-else-if="profile">
      <!-- Profile header -->
      <div class="card p-5 flex items-start gap-4 mb-4">
        <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary flex-shrink-0">
          {{ profile.name.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ profile.name }}</h2>
              <p v-if="profile.age" class="text-sm text-gray-500 mt-0.5">{{ profile.age }} лет</p>
            </div>
            <BaseButton
              v-if="!isSelf"
              :variant="profile.isFollowing ? 'outline' : 'primary'"
              size="sm"
              :loading="followLoading"
              class="flex-shrink-0"
              @click="toggleFollow"
            >{{ profile.isFollowing ? 'Отписаться' : 'Подписаться' }}</BaseButton>
          </div>
          <div class="flex gap-4 mt-3 text-sm text-gray-500">
            <span><strong class="text-gray-900 dark:text-white">{{ profile.workoutsCount }}</strong> тренировок</span>
            <span><strong class="text-gray-900 dark:text-white">{{ profile.followersCount }}</strong> подписчиков</span>
            <span><strong class="text-gray-900 dark:text-white">{{ profile.followingCount }}</strong> подписок</span>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200 dark:border-gray-800 mb-5">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
          :class="activeTab === tab.id
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          @click="activeTab = tab.id"
        >{{ tab.label }}</button>
      </div>

      <!-- TAB: Profile -->
      <div v-if="activeTab === 'profile'" class="space-y-5">
        <!-- Activity heatmap -->
        <div class="card p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Flame class="w-4 h-4 text-orange-400" />
            Активность за год
          </h3>
          <div v-if="activityLoading" class="h-20 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
          <ActivityHeatmap v-else :activity="activity" />
        </div>

        <!-- Achievements & Maxes row -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Achievements -->
          <div class="card p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Medal class="w-4 h-4 text-yellow-400" />
              Достижения
              <span v-if="achievements.length" class="text-xs text-gray-400 font-normal">({{ achievements.length }})</span>
            </h3>
            <div v-if="achievementsLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
            <div v-else-if="!achievements.length" class="text-sm text-gray-400 py-2">Пока нет достижений</div>
            <div v-else class="grid grid-cols-3 gap-2">
              <div
                v-for="a in achievements"
                :key="a.id"
                class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 dark:bg-gray-800/50 text-center"
                :title="a.title"
              >
                <span class="text-2xl leading-none">{{ a.icon }}</span>
                <span class="text-xs text-gray-600 dark:text-gray-400 leading-tight line-clamp-2">{{ a.title }}</span>
              </div>
            </div>
          </div>

          <!-- Personal maxes -->
          <div class="card p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Dumbbell class="w-4 h-4 text-primary" />
              Личные максимумы
            </h3>
            <div v-if="maxesLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
            <div v-else-if="!maxes.length" class="text-sm text-gray-400 py-2">Нет данных</div>
            <div v-else class="space-y-2">
              <div
                v-for="m in maxes"
                :key="m.exerciseName"
                class="flex items-center justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
              >
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ m.exerciseName }}</span>
                <span class="text-sm font-semibold text-primary">{{ m.weightKg }} кг</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Goals -->
        <div class="card p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Target class="w-4 h-4 text-green-500" />
            Активные цели
          </h3>
          <div v-if="goalsLoading" class="space-y-2">
            <div v-for="i in 2" :key="i" class="h-8 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
          </div>
          <div v-else-if="!goals.length" class="text-sm text-gray-400 py-2">Нет активных целей</div>
          <div v-else class="space-y-2">
            <div
              v-for="g in goals"
              :key="g.text"
              class="flex items-start gap-2 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
            >
              <div class="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ g.text }}</p>
                <p v-if="g.targetDate" class="text-xs text-gray-400 mt-0.5">до {{ formatDate(g.targetDate) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: Workouts -->
      <div v-else-if="activeTab === 'workouts'" class="space-y-3">
        <div v-if="workoutsLoading" class="space-y-3">
          <div v-for="i in 4" :key="i" class="card p-4 animate-pulse">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
            <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
          </div>
        </div>

        <BaseEmptyState
          v-else-if="!workouts.length"
          title="Нет тренировок"
          description="У этого пользователя пока нет записей"
        >
          <template #icon><Dumbbell class="w-10 h-10" /></template>
        </BaseEmptyState>

        <RouterLink
          v-else
          v-for="w in workouts"
          :key="w.id"
          :to="`/workouts/${w.id}`"
          class="card p-4 block hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-2 mb-1">
            <p class="font-semibold text-gray-900 dark:text-white leading-tight">{{ w.title || 'Тренировка' }}</p>
            <BaseBadge :color="typeColor(w.type)" class="flex-shrink-0">{{ w.type }}</BaseBadge>
          </div>
          <p class="text-xs text-gray-500 mb-2">
            {{ formatDate(w.date) }}
            <span v-if="w.durationMinutes"> · {{ w.durationMinutes }} мин</span>
            · {{ w.exercises.length }} упр.
          </p>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span
              v-for="ex in w.exercises.slice(0, 4)"
              :key="ex.exerciseId"
              class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
            >{{ ex.exerciseName }}</span>
            <span v-if="w.exercises.length > 4" class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-400">
              +{{ w.exercises.length - 4 }}
            </span>
          </div>
          <div class="flex items-center gap-4 text-xs text-gray-400">
            <span class="flex items-center gap-1">
              <Heart class="w-3 h-3" :class="w.isLiked ? 'fill-red-400 text-red-400' : ''" />
              {{ w.likesCount || 0 }}
            </span>
            <span class="flex items-center gap-1">
              <MessageCircle class="w-3 h-3" />
              {{ w.commentsCount || 0 }}
            </span>
          </div>
        </RouterLink>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-400">Пользователь не найден</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { ChevronLeft, Dumbbell, Flame, Medal, Target, Heart, MessageCircle } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import ActivityHeatmap from '@/components/social/ActivityHeatmap.vue'
import workoutService from '@/services/workoutService.js'

const store = useStore()
const route = useRoute()

const loading = ref(false)
const workoutsLoading = ref(false)
const followLoading = ref(false)
const activityLoading = ref(false)
const maxesLoading = ref(false)
const goalsLoading = ref(false)
const achievementsLoading = ref(false)

const workouts = ref([])
const activity = ref([])
const maxes = ref([])
const goals = ref([])
const achievements = ref([])

const activeTab = ref('profile')
const tabs = [
  { id: 'profile', label: 'Профиль' },
  { id: 'workouts', label: 'Тренировки' },
]

const userId = computed(() => Number(route.params.id))
const currentUserId = computed(() => store.state.auth.userId)
const isSelf = computed(() => userId.value === currentUserId.value)
const profile = computed(() => store.state.social.profiles[userId.value] ?? null)

onMounted(async () => {
  loading.value = true
  try {
    await store.dispatch('social/getProfile', userId.value)
  } finally {
    loading.value = false
  }

  // Load all tabs data in parallel
  const uid = userId.value
  activityLoading.value = true
  maxesLoading.value = true
  goalsLoading.value = true
  achievementsLoading.value = true
  workoutsLoading.value = true

  await Promise.allSettled([
    workoutService.fetchUserActivity(uid).then(d => { activity.value = d }).finally(() => { activityLoading.value = false }),
    workoutService.fetchUserMaxes(uid).then(d => { maxes.value = d }).finally(() => { maxesLoading.value = false }),
    workoutService.fetchUserGoals(uid).then(d => { goals.value = d }).finally(() => { goalsLoading.value = false }),
    workoutService.fetchUserAchievements(uid).then(d => { achievements.value = d }).finally(() => { achievementsLoading.value = false }),
    workoutService.fetchUserWorkouts(uid).then(d => { workouts.value = d }).catch(() => { workouts.value = [] }).finally(() => { workoutsLoading.value = false }),
  ])
})

async function toggleFollow() {
  if (!profile.value) return
  followLoading.value = true
  try {
    if (profile.value.isFollowing) {
      await store.dispatch('social/unfollow', userId.value)
    } else {
      await store.dispatch('social/follow', userId.value)
    }
    await store.dispatch('social/getProfile', userId.value)
  } finally {
    followLoading.value = false
  }
}

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
function typeColor(t) { return typeColorMap[t] || 'gray' }

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>
