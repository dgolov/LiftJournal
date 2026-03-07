<template>
  <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', colorClass]">
    <slot />
  </span>
</template>

<script setup>
const props = defineProps({
  color: { type: String, default: 'gray' }
})

const colorMap = {
  gray:   'bg-gray-100 text-gray-700',
  indigo: 'bg-indigo-100 text-indigo-700',
  green:  'bg-green-100 text-green-700',
  red:    'bg-red-100 text-red-700',
  yellow: 'bg-yellow-100 text-yellow-700',
  purple: 'bg-purple-100 text-purple-700',
  blue:   'bg-blue-100 text-blue-700',
  orange: 'bg-orange-100 text-orange-700'
}

const colorClass = colorMap[props.color] || colorMap.gray
</script>
