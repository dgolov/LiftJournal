<template>
  <div class="card p-4 flex flex-col gap-1">
    <p class="text-xs text-gray-500 font-medium">{{ label }}</p>
    <p class="text-2xl font-bold text-gray-900">{{ value }}</p>
    <p v-if="sub" class="text-xs text-gray-400">{{ sub }}</p>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  sub: String
})
</script>
