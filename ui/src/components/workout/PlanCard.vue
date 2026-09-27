<template>
  <SwipeDeleteWrapper delete-label="Удалить план" @delete="onSwipeDelete">
    <div
      class="bg-card dark:bg-steel-900 p-4 border-l-[3px] border-dashed border-primary/50 cursor-pointer"
      @click="$router.push(`/planning/${plan.id}`)"
    >
      <div class="flex items-start gap-2">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap mb-0.5">
            <span :class="`text-xs px-2 py-0.5 font-medium ${status.cls}`">{{ status.label }}</span>
            <span class="text-xs text-steel-700 dark:text-steel-300">{{ plan.type }}</span>
            <span class="text-xs text-steel-700 dark:text-steel-300">{{ dateLabel }}</span>
          </div>
          <p class="font-display font-semibold text-ink dark:text-white text-sm line-clamp-2">{{ plan.title }}</p>
          <p v-if="exCount" class="text-xs text-steel-700 dark:text-steel-300 mt-0.5 whitespace-nowrap">
            {{ exCount }} упр. · {{ setCount }} подходов
          </p>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          <button
            class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary hover:bg-primary/10 transition-colors"
            title="Редактировать"
            @click.stop="$router.push(`/planning/${plan.id}/edit`)"
          >
            <Pencil class="w-3.5 h-3.5" />
          </button>
          <button
            v-if="plan.status === 'planned'"
            class="px-3 py-1.5 bg-primary text-white text-xs font-display font-semibold uppercase tracking-wide hover:bg-primary-dark transition-colors"
            @click.stop="startPlan"
          >Начать</button>
          <button
            v-if="plan.status === 'planned'"
            class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-primary hover:bg-primary/10 transition-colors"
            title="Отменить / перенести"
            @click.stop="showSkipConfirm = true"
          >
            <Ban class="w-3.5 h-3.5" />
          </button>
          <button
            v-if="plan.status === 'skipped'"
            class="px-3 py-1.5 bg-primary text-white text-xs font-display font-semibold uppercase tracking-wide hover:bg-primary-dark transition-colors"
            @click.stop="showMarkCompleted = true"
          >Всё-таки выполнил</button>
        </div>
      </div>
    </div>
  </SwipeDeleteWrapper>

  <BaseModal v-model="showConfirm" title="Удалить план?" max-width="sm">
    <p class="text-sm text-steel-700 dark:text-steel-300">«{{ plan.title }}» будет удалён безвозвратно.</p>
    <template #footer>
      <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
      <BaseButton variant="danger" :disabled="deleting" @click="doDelete">
        {{ deleting ? 'Удаление...' : 'Удалить' }}
      </BaseButton>
    </template>
  </BaseModal>

  <SkipOrRescheduleModal v-model="showSkipConfirm" :plan="plan" />
  <MarkCompletedModal v-model="showMarkCompleted" :plan="plan" />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Pencil, Ban } from 'lucide-vue-next'
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import SkipOrRescheduleModal from '@/components/workout/SkipOrRescheduleModal.vue'
import MarkCompletedModal from '@/components/workout/MarkCompletedModal.vue'

const props = defineProps({ plan: { type: Object, required: true } })

const store = useStore()
const router = useRouter()
const showConfirm = ref(false)
const showSkipConfirm = ref(false)
const showMarkCompleted = ref(false)
const deleting = ref(false)

const statusMap = {
  planned:   { label: 'Запланировано', cls: 'bg-hazard/20 text-hazard dark:bg-hazard/25' },
  completed: { label: 'Выполнено',     cls: 'bg-success/15 text-success dark:bg-success/25' },
  skipped:   { label: 'Пропущено',     cls: 'bg-steel-100 text-steel-300 dark:bg-steel-700' },
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
