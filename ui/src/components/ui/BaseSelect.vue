<template>
  <div>
    <label v-if="label" class="label">{{ label }}</label>
    <select
      :value="modelValue"
      class="input"
      @change="$emit('update:modelValue', $event.target.value || null)"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value ?? opt" :value="opt.value ?? opt">
        {{ opt.label ?? opt }}
      </option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, null], default: null },
  label: String,
  placeholder: String,
  options: { type: Array, default: () => [] }
})
defineEmits(['update:modelValue'])
</script>
