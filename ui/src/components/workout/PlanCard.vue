<template>
  <SwipeDeleteWrapper delete-label="Удалить план" @delete="onSwipeDelete">
    <div class="bg-white dark:bg-gray-900 p-4 border-l-2 border-dashed border-primary/40">
      <div class="flex items-start gap-2">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap mb-0.5">
            <span :class="`text-xs px-2 py-0.5 rounded-full font-medium ${status.cls}`">{{ status.label }}</span>
            <span class="text-xs text-gray-400">{{ plan.type }}</span>
            <span class="text-xs text-gray-400">{{ dateLabel }}</span>
          </div>
          <p class="font-semibold text-gray-900 dark:text-white text-sm line-clamp-2">{{ plan.title }}</p>
          <p v-if="exCount" class="text-xs text-gray-400 mt-0.5 whitespace-nowrap">
            {{ exCount }} упр. · {{ setCount }} подходов
          </p>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          <button
            class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-primary hover:bg-primary/10 transition-colors"
            title="Редактировать"
            @click.stop="$router.push(`/planning/${plan.id}/edit`)"
          >
            <Pencil class="w-3.5 h-3.5" />
          </button>
          <button
            v-if="plan.status === 'planned'"
            class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded-lg hover:bg-primary/90 transition-colors"
            @click.stop="startPlan"
          >Начать</button>
        </div>
      </div>
    </div>
  </SwipeDeleteWrapper>

  <BaseModal v-model="showConfirm" title="Удалить план?" max-width="sm">
    <p class="text-sm text-gray-600 dark:text-gray-400">«{{ plan.title }}» будет удалён безвозвратно.</p>
    <template #footer>
      <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
      <BaseButton variant="danger" :disabled="deleting" @click="doDelete">
        {{ deleting ? 'Удаление...' : 'Удалить' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Pencil } from 'lucide-vue-next'
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({ plan: { type: Object, required: true } })

const store = useStore()
const router = useRouter()
const showConfirm = ref(false)
const deleting = ref(false)

const statusMap = {
  planned:   { label: 'Запланировано', cls: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300' },
  completed: { label: 'Выполнено',     cls: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' },
  skipped:   { label: 'Пропущено',     cls: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400' },
}
const status = computed(() => statusMap[props.plan.status] || statusMap.planned)
const exCount = computed(() => props.plan.exercises?.length || 0)
const setCount = computed(() => props.plan.exercises?.reduce((n, e) => n + (e.sets?.length || 0), 0) || 0)
const dateLabel = computed(() => {
  const d = new Date(props.plan.scheduledDate + 'T00:00:00')
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
})

async function startPlan() {
  await store.dispatch('workouts/startWorkoutFromPlan', props.plan)
  router.push('/workouts/new')
}

function onSwipeDelete() {
  showConfirm.value = true
}

async function doDelete() {
  deleting.value = true
  try {
    await store.dispatch('planned/deletePlannedWorkout', props.plan.id)
    store.dispatch('ui/showToast', { message: 'План удалён', type: 'success' })
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    deleting.value = false
    showConfirm.value = false
  }
}
</script>
