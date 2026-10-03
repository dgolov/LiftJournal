<template>
  <!-- My coach(es): what they can see/change, and a way out -->
  <div v-for="link in myCoaches" :key="link.id" class="card p-4">
    <div class="flex items-center gap-3 mb-3">
      <PersonAvatar :name="link.coachName" :url="link.coachAvatarUrl" />
      <div class="flex-1 min-w-0">
        <p class="text-xs text-steel-700 dark:text-steel-300">Мой тренер</p>
        <RouterLink :to="`/users/${link.coachId}`" class="font-semibold text-ink dark:text-white hover:text-primary truncate block">{{ link.coachName }}</RouterLink>
      </div>
    </div>
    <div class="space-y-3">
      <label class="flex items-start gap-3 cursor-pointer">
        <input
          type="checkbox" class="mt-0.5 w-4 h-4 rounded text-primary"
          :checked="link.canEditPlan" :disabled="busy === link.id"
          @change="setPermission(link, 'canEditPlan', $event.target.checked)"
        />
        <span class="text-sm">
          <span class="text-ink dark:text-white">Тренер может планировать мне тренировки</span>
          <span class="block text-xs text-steel-700 dark:text-steel-300">Создавать, менять и удалять ещё не выполненные тренировки в вашем плане</span>
        </span>
      </label>
      <label class="flex items-start gap-3 cursor-pointer">
        <input
          type="checkbox" class="mt-0.5 w-4 h-4 rounded text-primary"
          :checked="link.canSeePrivate" :disabled="busy === link.id"
          @change="setPermission(link, 'canSeePrivate', $event.target.checked)"
        />
        <span class="text-sm">
          <span class="text-ink dark:text-white">Тренер видит мои 1ПМ и вес тела</span>
          <span class="block text-xs text-steel-700 dark:text-steel-300">Нужно, чтобы считать интенсивность от ваших максимумов</span>
        </span>
      </label>
    </div>
    <button class="text-sm text-steel-700 dark:text-steel-300 hover:text-primary mt-4" @click="linkToEnd = link">
      Завершить сотрудничество
    </button>
  </div>

  <!-- Coach role -->
  <div id="coach" class="card p-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="font-semibold text-ink dark:text-white">Роль тренера</h3>
        <p class="text-sm text-steel-700 dark:text-steel-300 mt-0.5">
          Приглашайте подписчиков в подопечные, планируйте им тренировки и следите за нагрузкой.
        </p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer flex-shrink-0 mt-1">
        <input type="checkbox" class="sr-only peer" :checked="coach.isCoach" :disabled="saving" @change="toggleRole($event)" />
        <span class="w-11 h-6 rounded-full bg-steel-100 dark:bg-steel-700 peer-checked:bg-primary transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-primary/60" />
        <span class="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow-soft transition-transform peer-checked:translate-x-5" />
        <span class="sr-only">Роль тренера</span>
      </label>
    </div>

    <div v-if="coach.isCoach" class="mt-4 space-y-4">
      <label class="flex items-start gap-3 cursor-pointer">
        <input type="checkbox" class="mt-0.5 w-4 h-4 rounded text-primary" v-model="form.accepting" />
        <span class="text-sm">
          <span class="text-ink dark:text-white">Набор открыт</span>
          <span class="block text-xs text-steel-700 dark:text-steel-300">В вашем профиле появится кнопка «Хочу тренироваться», и спортсмены смогут прислать заявку</span>
        </span>
      </label>
      <div>
        <label class="label">О себе как о тренере</label>
        <textarea
          v-model="form.bio" rows="3" maxlength="2000" class="input resize-none"
          placeholder="Опыт, специализация, с кем работаете: RAW, жим, подготовка к первым соревнованиям…"
        />
      </div>
      <div class="flex items-center gap-3">
        <BaseButton size="sm" :disabled="!dirty" :loading="saving" @click="save">Сохранить</BaseButton>
        <RouterLink to="/coach" class="text-sm text-primary hover:underline">Мои подопечные</RouterLink>
      </div>
    </div>
  </div>

  <BaseModal :model-value="!!linkToEnd" title="Завершить сотрудничество?" max-width="sm" @update:model-value="linkToEnd = null">
    <p class="text-sm text-steel-700 dark:text-steel-300">
      {{ linkToEnd?.coachName }} больше не будет видеть ваши тренировки и менять ваш план. Тренировки, которые он уже запланировал, останутся у вас.
    </p>
    <template #footer>
      <BaseButton variant="ghost" @click="linkToEnd = null">Отмена</BaseButton>
      <BaseButton variant="danger" :loading="busy === linkToEnd?.id" @click="endLink">Завершить</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useStore } from 'vuex'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import PersonAvatar from '@/components/coach/PersonAvatar.vue'
import { apiErrorMessage } from '@/services/workoutService.js'

const store = useStore()
const coach = computed(() => store.state.user.coach)
const myCoaches = computed(() => store.getters['coach/myCoaches'])

const form = reactive({ bio: '', accepting: false })
watch(coach, c => { form.bio = c.bio; form.accepting = c.accepting }, { immediate: true })
const dirty = computed(() => form.bio !== coach.value.bio || form.accepting !== coach.value.accepting)

const saving = ref(false)
const busy = ref(null)
const linkToEnd = ref(null)

function toastError(e) {
  store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
}

async function toggleRole(event) {
  const isCoach = event.target.checked
  saving.value = true
  try {
    await store.dispatch('user/updateCoachSettings', { isCoach })
  } catch (e) {
    event.target.checked = !isCoach
    toastError(e)
  } finally {
    saving.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await store.dispatch('user/updateCoachSettings', { bio: form.bio, accepting: form.accepting })
    store.dispatch('ui/showToast', { message: 'Настройки тренера сохранены', type: 'success' })
  } catch (e) {
    toastError(e)
  } finally {
    saving.value = false
  }
}

async function setPermission(link, key, value) {
  busy.value = link.id
  try {
    await store.dispatch('coach/updatePermissions', { linkId: link.id, [key]: value })
  } catch (e) {
    toastError(e)
  } finally {
    busy.value = null
  }
}

async function endLink() {
  const link = linkToEnd.value
  busy.value = link.id
  try {
    await store.dispatch('coach/end', link.id)
    store.dispatch('ui/showToast', { message: 'Сотрудничество завершено', type: 'success' })
    linkToEnd.value = null
  } catch (e) {
    toastError(e)
  } finally {
    busy.value = null
  }
}
</script>
