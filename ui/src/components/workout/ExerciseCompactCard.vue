<template>
  <div class="card flex items-center gap-2 p-3">
    <span class="drag-handle flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 cursor-grab active:cursor-grabbing touch-none p-1 -ml-1">
      <GripVertical class="w-4 h-4" />
    </span>
    <div class="min-w-0 flex-1">
      <h4 class="font-semibold text-gray-900 dark:text-white truncate">{{ exerciseName }}</h4>
      <p class="text-xs text-gray-400">{{ setsCount }} {{ unitLabel }}</p>
    </div>
    <button
      v-if="historyLabel"
      class="flex items-center gap-1 px-2 h-8 rounded-lg text-xs font-medium text-primary hover:bg-primary/10 transition-colors flex-shrink-0"
      title="Показать подходы из другой тренировки"
      @click="$emit('cycle-history')"
    >
      <RotateCw class="w-3.5 h-3.5" />
      {{ historyLabel }}
    </button>
    <button
      class="w-10 h-10 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
      @click="$emit('remove')"
    >
      <Trash2 class="w-5 h-5" />
    </button>
  </div>
</template>

<script setup>
import { Trash2, GripVertical, RotateCw } from 'lucide-vue-next'

defineProps({
  exerciseName: { type: String, required: true },
  setsCount: { type: Number, default: 0 },
  unitLabel: { type: String, default: 'подход(ов)' },
  historyLabel: { type: String, default: null },
})

defineEmits(['remove', 'cycle-history'])
</script>
