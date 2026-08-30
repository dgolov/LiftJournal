<template>
  <BaseModal v-model="show" title="Шаблоны тренировок" max-width="md" :fullscreen="true">
    <div v-if="templates.length" class="mb-4">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Веса и повторы</p>
      <div class="flex gap-2">
        <button
          :class="['flex-1 py-2 rounded-lg text-sm font-medium border transition-colors',
            source === 'history' ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400']"
          @click="source = 'history'"
        >Из последней тренировки</button>
        <button
          :class="['flex-1 py-2 rounded-lg text-sm font-medium border transition-colors',
            source === 'template' ? 'bg-primary text-white border-primary' : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400']"
          @click="source = 'template'"
        >Из шаблона</button>
      </div>
      <p class="text-xs text-gray-400 mt-2">
        <template v-if="source === 'history'">Подставит веса/повторы из последней тренировки с этим упражнением, если она есть — иначе из шаблона.</template>
        <template v-else>Подставит веса/повторы, сохранённые в самом шаблоне.</template>
        История подходов всё равно останется доступна для переключения.
      </p>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-400 text-sm">Загрузка...</div>

    <div v-else-if="!templates.length" class="text-center py-8 text-gray-400 text-sm">
      Нет сохранённых шаблонов
    </div>

    <div v-else class="space-y-1 -mx-2 px-2">
      <div
        v-for="t in templates"
        :key="t.id"
        class="w-full px-3 py-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-3"
      >
        <button class="flex-1 min-w-0 text-left" @click="apply(t)">
          <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ t.title }}</p>
          <p class="text-xs text-gray-400">{{ t.type }} · {{ t.exercises.length }} упр.</p>
        </button>
        <button
          class="w-9 h-9 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
          title="Удалить шаблон"
          @click="remove(t)"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="ghost" @click="show = false">Закрыть</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { Trash2 } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'apply'])

const store = useStore()
const loading = ref(false)
const source = ref('history')

const show = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const templates = computed(() => store.getters['templates/all'])

watch(() => props.modelValue, async (open) => {
  if (open && !templates.value.length) {
    loading.value = true
    try {
      await store.dispatch('templates/fetchTemplates')
    } finally {
      loading.value = false
    }
  }
})

function apply(template) {
  emit('apply', template, source.value)
  show.value = false
}

async function remove(template) {
  await store.dispatch('templates/deleteTemplate', template.id)
  store.dispatch('ui/showToast', { message: 'Шаблон удалён', type: 'info' })
}
</script>
