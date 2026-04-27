<template>
  <header class="fixed top-0 left-0 right-0 lg:left-64 z-30 h-16 bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800 flex items-center px-4 gap-4">
    <!-- Mobile hamburger -->
    <button class="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400" @click="toggleSidebar">
      <Menu class="w-5 h-5" />
    </button>

    <h1 class="flex-1 text-lg font-semibold text-gray-900 dark:text-gray-100">{{ pageTitle }}</h1>

    <!-- Quick add button (desktop) -->
    <RouterLink to="/workouts/new" class="hidden sm:flex btn-primary btn text-sm">
      + Тренировка
    </RouterLink>

    <!-- Theme toggle -->
    <button
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
      :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
      @click="toggleTheme"
    >
      <Sun v-if="isDark" class="w-5 h-5" />
      <Moon v-else class="w-5 h-5" />
    </button>

    <!-- Notification bell -->
    <button
      class="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
      @click="togglePanel"
    >
      <Bell class="w-5 h-5" />
      <span
        v-if="unreadCount > 0"
        class="absolute top-1 right-1 min-w-[16px] h-4 px-0.5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center leading-none"
      >{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <!-- Avatar → Profile (mobile only) -->
    <RouterLink to="/profile" class="lg:hidden w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary">
      {{ initial }}
    </RouterLink>

    <!-- Avatar dropdown (desktop) -->
    <div class="hidden lg:block relative" ref="dropdownRef">
      <button
        class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary hover:bg-primary/30 transition-colors"
        @click="dropdownOpen = !dropdownOpen"
      >
        {{ initial }}
      </button>
      <transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="dropdownOpen"
          class="absolute right-0 mt-2 w-44 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-lg py-1 z-50 origin-top-right"
        >
          <RouterLink
            to="/profile"
            class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            @click="dropdownOpen = false"
          >
            <User class="w-4 h-4" />
            Профиль
          </RouterLink>
          <hr class="my-1 border-gray-100 dark:border-gray-800" />
          <button
            class="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
            @click="logout"
          >
            <LogOut class="w-4 h-4" />
            Выйти
          </button>
        </div>
      </transition>
    </div>
  </header>

  <!-- Notification panel (teleported outside header stacking context) -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-150"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <NotificationPanel v-if="panelOpen" />
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Sun, Moon, User, LogOut, Bell } from 'lucide-vue-next'
import NotificationPanel from '@/components/notifications/NotificationPanel.vue'

const store = useStore()
const route = useRoute()
const router = useRouter()

const initial = computed(() => store.state.user.profile.name?.charAt(0) || 'A')
const isDark = computed(() => store.state.user.theme === 'dark')
const unreadCount = computed(() => store.state.notifications.unreadCount)
const panelOpen = computed(() => store.state.notifications.panelOpen)

// ── Profile dropdown ────────────────────────────────────────────────────────
const dropdownOpen = ref(false)
const dropdownRef = ref(null)

function onClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
  // Fetch initial count (WS will push incremental updates)
  if (store.state.auth.token) store.dispatch('notifications/fetchUnreadCount')
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onClickOutside)
})

function togglePanel() {
  if (panelOpen.value) {
    store.dispatch('notifications/closePanel')
  } else {
    store.dispatch('notifications/openPanel')
  }
}

// ── Nav ─────────────────────────────────────────────────────────────────────
const titleMap = {
  history: 'История тренировок',
  'workout-create': 'Новая тренировка',
  'workout-detail': 'Тренировка',
  exercises: 'Упражнения',
  'exercise-detail': 'Упражнение',
  profile: 'Профиль',
}

const pageTitle = computed(() => titleMap[route.name] || 'LiftJournal')

function toggleSidebar() { store.commit('ui/TOGGLE_SIDEBAR') }

async function logout() {
  dropdownOpen.value = false
  await store.dispatch('auth/logout')
  router.push('/login')
}

function toggleTheme() {
  store.dispatch('user/setTheme', isDark.value ? 'light' : 'dark')
}
</script>
