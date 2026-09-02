<template>
  <div class="inline-flex items-center rounded-lg border border-gray-200 dark:border-gray-700 p-0.5 flex-shrink-0">
    <button
      :class="['p-1.5 rounded-md transition-colors', mode === 'standard' ? 'bg-primary text-white' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
      title="Стандартный режим"
      @click="mode = 'standard'"
    >
      <Rows3 class="w-4 h-4" />
    </button>
    <button
      :class="['p-1.5 rounded-md transition-colors', mode === 'cards' ? 'bg-primary text-white' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300']"
      title="Режим карточек — быстрое перетаскивание"
      @click="mode = 'cards'"
    >
      <LayoutGrid class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup>
import { Rows3, LayoutGrid } from 'lucide-vue-next'
import { useExerciseViewMode } from '@/composables/useExerciseViewMode.js'

const mode = useExerciseViewMode()
</script>
