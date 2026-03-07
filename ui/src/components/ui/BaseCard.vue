<template>
  <div :class="['card p-4', $attrs.class]" v-bind="omitClass($attrs)">
    <slot />
  </div>
</template>

<script setup>
function omitClass(attrs) {
  const { class: _, ...rest } = attrs
  return rest
}
</script>
