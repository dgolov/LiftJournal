<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="mb-4 text-steel-300 dark:text-steel-700">
      <slot name="icon" />
    </div>
    <h3 class="text-lg font-display font-semibold text-ink dark:text-white mb-1">{{ title }}</h3>
    <p class="text-sm text-steel-700 dark:text-steel-300 max-w-xs">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>
