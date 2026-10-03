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
          v-if="notification.workoutTitle && target"
          :to="target"
          class="font-medium hover:underline text-primary"
          @click.stop
        >«{{ notification.workoutTitle }}»</RouterLink>
      </p>
      <p
        v-if="['comment', 'coach_invite', 'coach_request'].includes(notification.type) && notification.commentText"
        class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate italic"
      >{{ notification.commentText }}</p>

      <!-- Answer an invite/request right here -->
      <div v-if="isCoachAsk" class="mt-2" @click.stop>
        <div v-if="notification.coachLinkStatus === 'pending'" class="flex gap-2">
          <button class="btn btn-primary text-xs px-3 py-1 min-h-0" :disabled="busy" @click="respond('accept')">Принять</button>
          <button class="btn btn-ghost text-xs px-3 py-1 min-h-0" :disabled="busy" @click="respond('decline')">Отклонить</button>
        </div>
        <p v-else-if="notification.coachLinkStatus" class="text-xs text-steel-700 dark:text-steel-300">
          {{ { active: 'Принято', declined: 'Отклонено', ended: 'Сотрудничество завершено' }[notification.coachLinkStatus] }}
        </p>
      </div>
      <p class="text-xs text-gray-400 mt-0.5">{{ timeAgo }}</p>
    </div>

    <!-- Unread dot -->
    <div v-if="!notification.isRead" class="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-2" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { notificationTarget } from './notificationTarget.js'
import { apiErrorMessage } from '@/services/workoutService.js'

const props = defineProps({
  notification: { type: Object, required: true },
})

defineEmits(['click'])

const store = useStore()
const target = computed(() => notificationTarget(props.notification, {
  coachLinks: store.state.coach.links, myId: store.state.auth.userId,
}))

const isCoachAsk = computed(() => ['coach_invite', 'coach_request'].includes(props.notification.type))
const busy = ref(false)
async function respond(action) {
  busy.value = true
  try {
    await store.dispatch(`coach/${action}`, props.notification.coachLinkId)
    if (!props.notification.isRead) store.dispatch('notifications/markRead', props.notification.id)
    if (action === 'accept' && props.notification.type === 'coach_request') {
      store.dispatch('coach/fetchAthletes').catch(() => {})
    }
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
  } finally {
    busy.value = false
  }
}

const actionText = computed(() => {
  switch (props.notification.type) {
    case 'follow': return ' подписался на вас'
    case 'like':   return ' поставил лайк тренировке '
    case 'comment': return ' прокомментировал тренировку '
    case 'coach_invite': return ' приглашает вас в подопечные'
    case 'coach_request': return ' хочет у вас тренироваться'
    case 'coach_accepted': return ' принял(а) ваше предложение о тренировках'
    case 'plan_assigned': return ' запланировал(а) вам тренировку '
    case 'athlete_completed': return ' выполнил(а) тренировку '
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
