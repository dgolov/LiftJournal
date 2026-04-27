<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 z-40 bg-black/20 dark:bg-black/40" @click="close" />

  <!-- Panel -->
  <div class="fixed top-16 right-0 lg:right-4 z-50 w-full lg:w-96 max-h-[calc(100vh-5rem)] flex flex-col bg-white dark:bg-gray-900 lg:rounded-2xl shadow-2xl border border-gray-100 dark:border-gray-800 overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
      <h2 class="font-semibold text-gray-900 dark:text-white">Уведомления</h2>
      <div class="flex items-center gap-2">
        <button
          v-if="activeTab === 'unread' && unread.length"
          class="text-xs text-primary hover:underline"
          @click="markAll"
        >Прочитать все</button>
        <button class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="close">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="flex-1 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === tab.id
          ? 'border-primary text-primary'
          : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
        <span
          v-if="tab.id === 'unread' && unreadCount"
          class="ml-1.5 px-1.5 py-0.5 rounded-full text-xs bg-primary text-white leading-none"
        >{{ unreadCount }}</span>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- UNREAD TAB -->
      <div v-if="activeTab === 'unread'">
        <div v-if="!unread.length" class="flex flex-col items-center justify-center py-12 text-gray-400">
          <Bell class="w-10 h-10 mb-2 opacity-30" />
          <p class="text-sm">Новых уведомлений нет</p>
        </div>
        <NotificationItem
          v-for="n in unread"
          :key="n.id"
          :notification="n"
          @click="onItemClick(n)"
        />
      </div>

      <!-- ALL TAB -->
      <div v-else>
        <div v-if="!all.length && !loadingAll" class="flex flex-col items-center justify-center py-12 text-gray-400">
          <Bell class="w-10 h-10 mb-2 opacity-30" />
          <p class="text-sm">Уведомлений пока нет</p>
        </div>
        <NotificationItem
          v-for="n in all"
          :key="n.id"
          :notification="n"
          @click="onItemClick(n)"
        />
        <div v-if="loadingAll" class="py-4 text-center text-sm text-gray-400">Загрузка…</div>
        <button
          v-else-if="allHasMore"
          class="w-full py-3 text-sm text-primary hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          @click="loadMore"
        >Загрузить ещё</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { X, Bell } from 'lucide-vue-next'
import NotificationItem from './NotificationItem.vue'

const store = useStore()
const router = useRouter()

const activeTab = ref('unread')
const loadingAll = ref(false)

const tabs = [
  { id: 'unread', label: 'Новые' },
  { id: 'all', label: 'Все' },
]

const unread = computed(() => store.state.notifications.unread)
const unreadCount = computed(() => store.state.notifications.unreadCount)
const all = computed(() => store.state.notifications.all)
const allHasMore = computed(() => store.state.notifications.allHasMore)

function close() {
  store.dispatch('notifications/closePanel')
}

async function markAll() {
  await store.dispatch('notifications/markAllRead')
}

async function loadMore() {
  loadingAll.value = true
  try {
    await store.dispatch('notifications/fetchAll')
  } finally {
    loadingAll.value = false
  }
}

async function onItemClick(n) {
  if (!n.isRead) await store.dispatch('notifications/markRead', n.id)
  close()
  if (n.workoutId) {
    router.push(`/workouts/${n.workoutId}`)
  } else if (n.type === 'follow') {
    router.push(`/users/${n.actorId}`)
  }
}
</script>
