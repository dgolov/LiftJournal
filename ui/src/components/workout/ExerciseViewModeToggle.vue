<template>
  <div class="inline-flex items-center border-2 border-ink dark:border-steel-700 p-0.5 flex-shrink-0">
    <button
      :class="['p-1.5 transition-colors', mode === 'standard' ? 'bg-primary text-white' : 'text-steel-700 dark:text-steel-300 hover:text-primary']"
      title="Стандартный режим"
      @click="mode = 'standard'"
    >
      <Rows3 class="w-4 h-4" />
    </button>
    <button
      :class="['p-1.5 transition-colors', mode === 'cards' ? 'bg-primary text-white' : 'text-steel-700 dark:text-steel-300 hover:text-primary']"
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
