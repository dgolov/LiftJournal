<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Циклы</h2>
      <RouterLink to="/cycles/new" class="btn btn-primary text-sm px-4 py-2">+ Новый цикл</RouterLink>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">Загрузка...</div>

    <div v-else-if="cycles.length" class="space-y-3">
      <div
        v-for="cycle in cycles"
        :key="cycle.id"
        class="card p-4 hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/cycles/${cycle.id}`)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', cycle.is_public ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400']">
                {{ cycle.is_public ? 'Публичный' : 'Приватный' }}
              </span>
              <span v-if="cycle.author_name" class="text-xs text-gray-400">{{ cycle.author_name }}</span>
              <span v-if="cycle.created_by === currentUserId" class="text-xs text-primary font-medium">Мой</span>
            </div>
            <h3 class="font-semibold text-gray-900 dark:text-white">{{ cycle.title }}</h3>
            <p v-if="cycle.description" class="text-sm text-gray-500 mt-0.5 line-clamp-1">{{ cycle.description }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ cycle.workout_count }} тренировок</p>
          </div>
          <button
            v-if="cycle.created_by === currentUserId"
            class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
            @click.stop="confirmDelete(cycle)"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <BaseEmptyState v-else title="Нет циклов" description="Создайте свой первый цикл или дождитесь публичных">
      <template #icon><ClipboardList class="w-12 h-12" /></template>
      <RouterLink to="/cycles/new" class="mt-4 btn btn-primary">Создать цикл</RouterLink>
    </BaseEmptyState>

    <BaseModal v-model="showConfirm" title="Удалить цикл?" max-width="sm">
      <p class="text-sm text-gray-600">«{{ toDelete?.title }}» будет удалён безвозвратно.</p>
      <template #footer>
        <BaseButton variant="ghost" @click="showConfirm = false">Отмена</BaseButton>
        <BaseButton variant="danger" @click="doDelete">Удалить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { onBeforeRouteLeave } from 'vue-router'
import { Trash2, ClipboardList } from 'lucide-vue-next'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const store = useStore()
const loading = ref(false)
const showConfirm = ref(false)
const toDelete = ref(null)
let leaving = false
onBeforeRouteLeave(() => { leaving = true })

const cycles = computed(() => store.state.cycles.cycles)
const currentUserId = computed(() => store.state.auth.userId)

onMounted(async () => {
  loading.value = true
  try { await store.dispatch('cycles/fetchCycles') } finally { if (!leaving) loading.value = false }
})

function confirmDelete(cycle) {
  toDelete.value = cycle
  showConfirm.value = true
}

async function doDelete() {
  await store.dispatch('cycles/deleteCycle', toDelete.value.id)
  showConfirm.value = false
}
</script>
