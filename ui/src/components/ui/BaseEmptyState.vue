<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="mb-4 text-gray-300 dark:text-gray-600">
      <slot name="icon" />
    </div>
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500 max-w-xs">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>
