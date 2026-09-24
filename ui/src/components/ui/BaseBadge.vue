<template>
  <span :class="['inline-flex items-center border px-2 py-0.5 text-xs font-medium', colorClass]">
    <slot />
  </span>
</template>

<script setup>
const props = defineProps({
  color: { type: String, default: 'gray' }
})

const colorMap = {
  gray:   'border-steel-300 text-steel-700 dark:border-steel-700 dark:text-steel-300',
  indigo: 'border-indigo-400 text-indigo-700 dark:text-indigo-300',
  green:  'border-success text-success',
  red:    'border-primary text-primary',
  yellow: 'border-hazard text-hazard',
  purple: 'border-purple-400 text-purple-700 dark:text-purple-300',
  blue:   'border-blue-400 text-blue-700 dark:text-blue-300',
  orange: 'border-orange-400 text-orange-700 dark:text-orange-300'
}

const colorClass = colorMap[props.color] || colorMap.gray
</script>
