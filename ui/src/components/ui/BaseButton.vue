<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[variantClass, sizeClass, 'btn']"
    v-bind="$attrs"
  >
    <span v-if="loading" class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
    <slot />
  </button>
</template>

<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  type: { type: String, default: 'button' },
  disabled: Boolean,
  loading: Boolean
})

const variantMap = {
  primary: 'btn-primary',
  ghost: 'btn-ghost',
  danger: 'btn-danger',
  outline: 'btn-outline'
}

const sizeMap = {
  sm: 'text-xs px-3 py-1.5',
  md: '',
  lg: 'text-base px-6 py-3'
}

const variantClass = variantMap[props.variant] || 'btn-primary'
const sizeClass = sizeMap[props.size] || ''
</script>
