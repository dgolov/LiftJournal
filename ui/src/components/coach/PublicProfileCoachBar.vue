<template>
  <div v-if="visible" class="mt-4 pt-4 border-t border-steel-100 dark:border-steel-700">
    <div v-if="profile.isCoach" class="mb-3">
      <span class="inline-flex items-center gap-1.5 rounded-full bg-primary/10 text-primary text-xs font-semibold px-2.5 py-1">
        <Megaphone class="w-3.5 h-3.5" /> Тренер<template v-if="profile.coachAccepting"> · набор открыт</template>
      </span>
      <p v-if="profile.coachBio" class="text-sm text-steel-700 dark:text-steel-300 mt-2 whitespace-pre-line">{{ profile.coachBio }}</p>
    </div>

    <!-- Existing link -->
    <template v-if="link">
      <template v-if="link.status === 'active'">
        <p v-if="link.myRole === 'athlete'" class="text-sm text-ink dark:text-white">Это ваш тренер</p>
        <RouterLink v-else :to="`/coach/athletes/${profile.id}`" class="btn btn-outline">
          Открыть подопечного
        </RouterLink>
      </template>
      <div v-else-if="link.initiatedByMe" class="flex items-center gap-3 flex-wrap">
        <p class="text-sm text-steel-700 dark:text-steel-300">
          {{ link.myRole === 'coach' ? 'Приглашение отправлено — ждём ответа' : 'Заявка отправлена — тренер ещё не ответил' }}
        </p>
        <BaseButton size="sm" variant="ghost" :loading="busy" @click="run('cancel')">Отозвать</BaseButton>
      </div>
      <div v-else>
        <p class="text-sm text-ink dark:text-white mb-2">
          {{ link.myRole === 'athlete' ? `${profile.name} приглашает вас в подопечные` : `${profile.name} хочет у вас тренироваться` }}
        </p>
        <div class="flex gap-2">
          <BaseButton size="sm" :loading="busy" @click="run('accept')">Принять</BaseButton>
          <BaseButton size="sm" variant="ghost" :disabled="busy" @click="run('decline')">Отклонить</BaseButton>
        </div>
      </div>
    </template>

    <!-- No link yet -->
    <div v-else class="flex gap-2 flex-wrap">
      <BaseButton v-if="canRequest" size="sm" @click="openModal('request')">Хочу тренироваться</BaseButton>
      <BaseButton v-if="canInvite" size="sm" variant="outline" @click="openModal('invite')">Пригласить в подопечные</BaseButton>
    </div>

    <BaseModal v-model="showModal" :title="mode === 'invite' ? 'Пригласить в подопечные' : 'Заявка тренеру'" max-width="md">
      <p class="text-sm text-steel-700 dark:text-steel-300 mb-3">
        <template v-if="mode === 'invite'">
          Если {{ profile.name }} примет приглашение, вы будете видеть тренировки, графики и 1ПМ и сможете планировать тренировки. Доступ можно в любой момент отозвать.
        </template>
        <template v-else>
          Если {{ profile.name }} примет заявку, тренер будет видеть ваши тренировки, графики и 1ПМ и сможет планировать вам тренировки. Права можно сузить в профиле, а сотрудничество — завершить в любой момент.
        </template>
      </p>
      <label class="label">Сообщение (необязательно)</label>
      <textarea
        v-model="message" rows="3" maxlength="500" class="input resize-none"
        :placeholder="mode === 'invite' ? 'Например: готовимся к старту в декабре' : 'Цель, опыт, текущие максимумы, сколько раз в неделю можете тренироваться'"
      />
      <template #footer>
        <BaseButton variant="ghost" @click="showModal = false">Отмена</BaseButton>
        <BaseButton :loading="busy" @click="submit">{{ mode === 'invite' ? 'Отправить приглашение' : 'Отправить заявку' }}</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { Megaphone } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { apiErrorMessage } from '@/services/workoutService.js'

const props = defineProps({
  profile: { type: Object, required: true },
})
const emit = defineEmits(['changed'])

const store = useStore()
const link = computed(() => props.profile.coachLink)
const iAmCoach = computed(() => store.state.user.coach.isCoach)
const canRequest = computed(() => props.profile.isCoach && props.profile.coachAccepting)
const canInvite = computed(() => iAmCoach.value && props.profile.followsMe)
const visible = computed(() => props.profile.isCoach || link.value || canRequest.value || canInvite.value)

const busy = ref(false)
const showModal = ref(false)
const mode = ref('request')
const message = ref('')

function openModal(m) {
  mode.value = m
  message.value = ''
  showModal.value = true
}

async function withBusy(fn, successMessage) {
  busy.value = true
  try {
    await fn()
    if (successMessage) store.dispatch('ui/showToast', { message: successMessage, type: 'success' })
    emit('changed')
  } catch (e) {
    store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
  } finally {
    busy.value = false
  }
}

function submit() {
  const action = mode.value === 'invite'
    ? () => store.dispatch('coach/invite', { athleteId: props.profile.id, message: message.value })
    : () => store.dispatch('coach/request', { coachId: props.profile.id, message: message.value })
  return withBusy(async () => {
    await action()
    showModal.value = false
  }, mode.value === 'invite' ? 'Приглашение отправлено' : 'Заявка отправлена')
}

function run(action) {
  const success = { accept: 'Готово — сотрудничество началось', decline: null, cancel: null }[action]
  return withBusy(() => store.dispatch(`coach/${action}`, link.value.id), success)
}
</script>
