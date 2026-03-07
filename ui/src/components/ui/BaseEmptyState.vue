<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="text-5xl mb-4">{{ icon }}</div>
    <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500 max-w-xs">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>
