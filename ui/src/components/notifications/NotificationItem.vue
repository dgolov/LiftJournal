<template>
  <div
    class="flex items-start gap-3 px-4 py-3 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/60"
    :class="!notification.isRead ? 'bg-primary/5 dark:bg-primary/10' : ''"
    @click="$emit('click')"
  >
    <!-- Actor avatar -->
    <RouterLink
      :to="`/users/${notification.actorId}`"
      class="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0 mt-0.5"
      @click.stop
    >
      {{ notification.actorName.charAt(0).toUpperCase() }}
    </RouterLink>

    <div class="flex-1 min-w-0">
      <p class="text-sm text-gray-800 dark:text-gray-200 leading-snug">
        <RouterLink
          :to="`/users/${notification.actorId}`"
          class="font-semibold hover:underline"
          @click.stop
        >{{ notification.actorName }}</RouterLink>
        {{ actionText }}
        <RouterLink
          v-if="notification.workoutId && notification.workoutTitle"
          :to="`/workouts/${notification.workoutId}`"
          class="font-medium hover:underline text-primary"
          @click.stop
        >«{{ notification.workoutTitle }}»</RouterLink>
      </p>
      <p
        v-if="notification.type === 'comment' && notification.commentText"
        class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate italic"
      >{{ notification.commentText }}</p>
      <p class="text-xs text-gray-400 mt-0.5">{{ timeAgo }}</p>
    </div>

    <!-- Unread dot -->
    <div v-if="!notification.isRead" class="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-2" />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  notification: { type: Object, required: true },
})

defineEmits(['click'])

const actionText = computed(() => {
  switch (props.notification.type) {
    case 'follow': return ' подписался на вас'
    case 'like':   return ' поставил лайк тренировке '
    case 'comment': return ' прокомментировал тренировку '
    default: return ''
  }
})

const timeAgo = computed(() => {
  const diff = Date.now() - new Date(props.notification.createdAt).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'только что'
  if (m < 60) return `${m} мин. назад`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} ч. назад`
  const d = Math.floor(h / 24)
  if (d < 7) return `${d} д. назад`
  return new Date(props.notification.createdAt).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
})
</script>
