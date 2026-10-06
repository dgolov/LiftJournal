<template>
  <img
    v-if="url"
    :src="url"
    :alt="name"
    :class="['rounded-full object-cover flex-shrink-0', sizeClass]"
  />
  <div
    v-else
    :class="['rounded-full bg-primary/10 text-primary flex items-center justify-center font-display font-semibold flex-shrink-0', sizeClass]"
  >{{ initial }}</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  url: { type: String, default: null },
  size: { type: String, default: 'md' },
})

const initial = computed(() => (props.name || '?').trim().charAt(0).toUpperCase())
const sizeClass = computed(() => ({ sm: 'w-8 h-8 text-sm', md: 'w-10 h-10 text-base', lg: 'w-14 h-14 text-xl' })[props.size])
</script>
