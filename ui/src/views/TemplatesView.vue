<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Шаблоны</h2>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">Загрузка...</div>

    <BaseEmptyState
      v-else-if="!templates.length"
      title="Нет шаблонов"
      description="Сохраните тренировку или план как шаблон — он появится здесь"
    >
      <template #icon><LayoutTemplate class="w-12 h-12" /></template>
    </BaseEmptyState>

    <div v-else class="space-y-3">
      <SwipeDeleteWrapper
        v-for="t in templates"
        :key="t.id"
        delete-label="Удалить шаблон"
        @delete="confirmDelete(t)"
      >
        <div class="bg-white dark:bg-gray-900 p-4">
          <div class="flex items-start gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-0.5">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-primary/10 text-primary">{{ t.type }}</span>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white line-clamp-2">{{ t.title }}</h3>
              <p v-if="t.exercises.length" class="text-xs text-gray-400 mt-0.5">
                {{ t.exercises.length }} упр. · {{ totalSets(t) }} подходов
              </p>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0">
              <button
                class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-gray-500 transition-colors"
                title="Редактировать"
                @click="$router.push(`/templates/${t.id}/edit`)"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button
                class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
                title="Удалить"
                @click="confirmDelete(t)"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div v-if="t.exercises.length" class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex flex-wrap gap-x-3 gap-y-1">
            <span v-for="ex in t.exercises" :key="ex.exerciseId" class="text-xs text-gray-500 dark:text-gray-400">
              · {{ ex.exerciseName }}
            </span>
          </div>
        </div>
      </SwipeDeleteWrapper>
    </div>

    <BaseModal v-model="showDeleteConfirm" title="Удалить шаблон?" max-width="sm">
      <p class="text-sm text-gray-600 dark:text-gray-400">«{{ toDelete?.title }}» будет удалён безвозвратно.</p>
      <template #footer>
        <BaseButton variant="ghost" @click="showDeleteConfirm = false">Отмена</BaseButton>
        <BaseButton variant="danger" @click="doDelete">Удалить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { LayoutTemplate, Pencil, Trash2 } from 'lucide-vue-next'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'

const store = useStore()

const loading = ref(false)
const showDeleteConfirm = ref(false)
const toDelete = ref(null)

const templates = computed(() => store.getters['templates/all'])

function totalSets(t) {
  return t.exercises.reduce((n, ex) => n + ex.sets.length, 0)
}

function confirmDelete(t) {
  toDelete.value = t
  showDeleteConfirm.value = true
}

async function doDelete() {
  try {
    await store.dispatch('templates/deleteTemplate', toDelete.value.id)
    store.dispatch('ui/showToast', { message: 'Шаблон удалён', type: 'success' })
  } catch (e) {
    store.dispatch('ui/showToast', { message: 'Ошибка: ' + e.message, type: 'error' })
  } finally {
    showDeleteConfirm.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await store.dispatch('templates/fetchTemplates')
  } finally {
    loading.value = false
  }
})
</script>
