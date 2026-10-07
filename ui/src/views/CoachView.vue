<template>
  <div class="max-w-3xl">
    <div class="flex items-center justify-between gap-3 mb-6 flex-wrap">
      <h2 class="text-2xl font-bold text-ink dark:text-white">Подопечные</h2>
      <BaseButton v-if="isCoach" variant="outline" size="sm" @click="openInvite">
        <UserPlus class="w-4 h-4" />
        Пригласить подписчика
      </BaseButton>
    </div>

    <!-- Not a coach yet -->
    <div v-if="!isCoach" class="card p-6">
      <BaseEmptyState
        title="Роль тренера выключена"
        description="Включите её в профиле, чтобы приглашать подписчиков, принимать заявки и планировать тренировки подопечным."
      >
        <template #icon><Users class="w-12 h-12" /></template>
        <RouterLink to="/profile#coach" class="btn btn-primary mt-4">Открыть профиль</RouterLink>
      </BaseEmptyState>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="inline-flex rounded-xl bg-steel-100/70 dark:bg-steel-950 p-0.5 mb-4">
        <button
          v-for="t in tabs" :key="t.value"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-1.5',
            tab === t.value ? 'bg-card text-primary shadow-soft dark:bg-steel-700' : 'text-steel-700 dark:text-steel-300 hover:text-ink dark:hover:text-white']"
          @click="tab = t.value"
        >
          {{ t.label }}
          <span v-if="t.count" class="min-w-[1.25rem] h-5 px-1 rounded-full bg-primary text-white text-xs flex items-center justify-center">{{ t.count }}</span>
        </button>
      </div>

      <!-- Athletes -->
      <div v-if="tab === 'athletes'">
        <div v-if="loading && !athletes.length" class="text-center py-12 text-steel-300">Загрузка…</div>
        <div v-else-if="!athletes.length" class="card p-6">
          <BaseEmptyState
            title="Подопечных пока нет"
            description="Пригласите кого-то из подписчиков или откройте набор в профиле, чтобы вам могли прислать заявку."
          >
            <template #icon><Users class="w-12 h-12" /></template>
          </BaseEmptyState>
        </div>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="a in athletes" :key="a.id"
            :to="`/coach/athletes/${a.id}`"
            class="card p-4 flex items-center gap-3 hover:border-primary/40 transition-colors"
          >
            <PersonAvatar :name="a.name" :url="a.avatarUrl" />
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-ink dark:text-white truncate">{{ a.name }}</p>
              <p class="text-xs text-steel-700 dark:text-steel-300">
                {{ a.lastWorkoutDate ? `Последняя тренировка ${daysAgo(a.lastWorkoutDate)}` : 'Ещё не тренировался' }}
              </p>
            </div>
            <div class="text-right flex-shrink-0">
              <p :class="['text-sm font-semibold', weekTone(a)]">{{ a.weekCompleted }} из {{ a.weekPlanned }}</p>
              <p class="text-xs text-steel-300">на этой неделе</p>
            </div>
            <ChevronRight class="w-4 h-4 text-steel-300 flex-shrink-0" />
          </RouterLink>
        </div>
      </div>

      <!-- Requests & invites -->
      <div v-else class="space-y-6">
        <section>
          <h3 class="font-semibold text-ink dark:text-white mb-2">Заявки от спортсменов</h3>
          <p v-if="!incoming.length" class="text-sm text-steel-300">
            {{ accepting ? 'Новых заявок нет.' : 'Набор закрыт — включите «Набор открыт» в профиле, чтобы получать заявки.' }}
          </p>
          <div v-else class="space-y-2">
            <div v-for="l in incoming" :key="l.id" class="card p-4">
              <div class="flex items-center gap-3">
                <PersonAvatar :name="l.athleteName" :url="l.athleteAvatarUrl" />
                <div class="flex-1 min-w-0">
                  <RouterLink :to="`/users/${l.athleteId}`" class="font-semibold text-ink dark:text-white hover:text-primary truncate block">{{ l.athleteName }}</RouterLink>
                  <p class="text-xs text-steel-300">{{ formatDate(l.createdAt) }}</p>
                </div>
              </div>
              <p v-if="l.message" class="text-sm text-steel-700 dark:text-steel-300 mt-3 whitespace-pre-line">{{ l.message }}</p>
              <div class="flex gap-2 mt-3">
                <BaseButton size="sm" :loading="busy === l.id + 'accept'" @click="respond(l, 'accept')">Принять</BaseButton>
                <BaseButton size="sm" variant="ghost" :disabled="!!busy" @click="respond(l, 'decline')">Отклонить</BaseButton>
              </div>
            </div>
          </div>
        </section>

        <section>
          <h3 class="font-semibold text-ink dark:text-white mb-2">Отправленные приглашения</h3>
          <p v-if="!outgoing.length" class="text-sm text-steel-300">Приглашений, ожидающих ответа, нет.</p>
          <div v-else class="space-y-2">
            <div v-for="l in outgoing" :key="l.id" class="card p-4 flex items-center gap-3">
              <PersonAvatar :name="l.athleteName" :url="l.athleteAvatarUrl" />
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-ink dark:text-white truncate">{{ l.athleteName }}</p>
                <p class="text-xs text-steel-300">Ждёт ответа с {{ formatDate(l.createdAt) }}</p>
              </div>
              <BaseButton size="sm" variant="ghost" :loading="busy === l.id + 'cancel'" @click="cancel(l)">Отозвать</BaseButton>
            </div>
          </div>
        </section>
      </div>
    </template>

    <!-- Invite a follower -->
    <BaseModal v-model="showInvite" title="Пригласить подписчика" max-width="md">
      <p class="text-sm text-steel-700 dark:text-steel-300 mb-3">
        Пригласить можно только того, кто на вас подписан. После согласия вы увидите его тренировки и сможете планировать ему нагрузку.
      </p>
      <input v-model="followerQuery" type="search" placeholder="Найти по имени" class="input mb-3" />
      <div v-if="followersLoading" class="text-center py-6 text-sm text-steel-300">Загрузка…</div>
      <p v-else-if="!invitable.length" class="text-center py-6 text-sm text-steel-300">
        {{ followers.length ? 'Никого не найдено' : 'У вас пока нет подписчиков' }}
      </p>
      <div v-else class="space-y-1 max-h-72 overflow-y-auto -mx-1 px-1">
        <button
          v-for="f in invitable" :key="f.id"
          :class="['w-full flex items-center gap-3 p-2 rounded-xl text-left transition-colors',
            inviteTarget?.id === f.id ? 'bg-primary/10' : 'hover:bg-steel-50 dark:hover:bg-steel-950']"
          @click="inviteTarget = f"
        >
          <PersonAvatar :name="f.name" :url="f.avatarUrl" size="sm" />
          <span class="flex-1 text-sm font-medium text-ink dark:text-white truncate">{{ f.name }}</span>
          <Check v-if="inviteTarget?.id === f.id" class="w-4 h-4 text-primary" />
        </button>
      </div>
      <div v-if="inviteTarget" class="mt-4">
        <label class="label">Сообщение для {{ inviteTarget.name }} (необязательно)</label>
        <textarea v-model="inviteMessage" rows="2" maxlength="500" class="input resize-none" placeholder="Например: готовимся к старту в декабре" />
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showInvite = false">Отмена</BaseButton>
        <BaseButton :disabled="!inviteTarget" :loading="inviting" @click="sendInvite">Отправить приглашение</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { Users, UserPlus, ChevronRight, Check } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import PersonAvatar from '@/components/coach/PersonAvatar.vue'
import workoutService, { apiErrorMessage } from '@/services/workoutService.js'

const store = useStore()

const isCoach = computed(() => store.state.user.coach.isCoach)
const accepting = computed(() => store.state.user.coach.accepting)
const athletes = computed(() => store.state.coach.athletes)
const myId = computed(() => store.state.auth.userId)
// Only links where I'm the coach belong on this screen.
const incoming = computed(() => store.getters['coach/incomingRequests'].filter(l => l.coachId === myId.value))
const outgoing = computed(() => store.getters['coach/outgoingRequests'].filter(l => l.coachId === myId.value))

const tab = ref('athletes')
const tabs = computed(() => [
  { value: 'athletes', label: 'Подопечные', count: 0 },
  { value: 'requests', label: 'Заявки и приглашения', count: incoming.value.length },
])

const loading = ref(false)
const busy = ref(null)

onMounted(async () => {
  if (!isCoach.value) return
  loading.value = true
  try {
    await Promise.all([store.dispatch('coach/fetchAthletes'), store.dispatch('coach/fetchLinks')])
    if (incoming.value.length && !athletes.value.length) tab.value = 'requests'
  } catch (e) {
    toastError(e)
  } finally {
    loading.value = false
  }
})

function toastError(e) {
  store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
}

async function respond(link, action) {
  busy.value = link.id + action
  try {
    await store.dispatch(`coach/${action}`, link.id)
    if (action === 'accept') {
      await store.dispatch('coach/fetchAthletes')
      store.dispatch('ui/showToast', { message: `${link.athleteName} теперь ваш подопечный`, type: 'success' })
    }
  } catch (e) {
    toastError(e)
  } finally {
    busy.value = null
  }
}

async function cancel(link) {
  busy.value = link.id + 'cancel'
  try {
    await store.dispatch('coach/cancel', link.id)
  } catch (e) {
    toastError(e)
  } finally {
    busy.value = null
  }
}

// ── Invite ──────────────────────────────────────────────────────────────────
const showInvite = ref(false)
const followers = ref([])
const followersLoading = ref(false)
const followerQuery = ref('')
const inviteTarget = ref(null)
const inviteMessage = ref('')
const inviting = ref(false)

// Followers already coached by me or with an invite pending are left out.
const invitable = computed(() => {
  const linked = new Set(store.state.coach.links.filter(l => l.coachId === myId.value).map(l => l.athleteId))
  const q = followerQuery.value.trim().toLowerCase()
  return followers.value.filter(f => !linked.has(f.id) && (!q || f.name.toLowerCase().includes(q)))
})

async function openInvite() {
  showInvite.value = true
  inviteTarget.value = null
  inviteMessage.value = ''
  followerQuery.value = ''
  followersLoading.value = true
  try {
    followers.value = await workoutService.fetchMyFollowers()
  } catch (e) {
    toastError(e)
  } finally {
    followersLoading.value = false
  }
}

async function sendInvite() {
  inviting.value = true
  try {
    await store.dispatch('coach/invite', { athleteId: inviteTarget.value.id, message: inviteMessage.value })
    store.dispatch('ui/showToast', { message: `Приглашение отправлено: ${inviteTarget.value.name}`, type: 'success' })
    showInvite.value = false
    tab.value = 'requests'
  } catch (e) {
    toastError(e)
  } finally {
    inviting.value = false
  }
}

// ── Formatting ──────────────────────────────────────────────────────────────
function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function daysAgo(dateStr) {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const days = Math.round((today - new Date(dateStr + 'T00:00:00')) / 86400000)
  if (days <= 0) return 'сегодня'
  if (days === 1) return 'вчера'
  const mod10 = days % 10, mod100 = days % 100
  const word = mod10 === 1 && mod100 !== 11 ? 'день' : mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20) ? 'дня' : 'дней'
  return `${days} ${word} назад`
}

// Behind plan → muted warning tone; nothing planned → neutral.
function weekTone(a) {
  if (!a.weekPlanned) return 'text-steel-700 dark:text-steel-300'
  return a.weekCompleted >= a.weekPlanned ? 'text-success' : 'text-ink dark:text-white'
}
</script>
