<template>
  <div>
    <label v-if="label" :for="id" class="label">{{ label }}</label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :min="min"
      :max="max"
      :step="step"
      :disabled="disabled"
      class="input"
      @input="$emit('update:modelValue', type === 'number' ? +$event.target.value : $event.target.value)"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  id: String,
  min: [String, Number],
  max: [String, Number],
  step: [String, Number],
  disabled: Boolean
})
defineEmits(['update:modelValue'])
</script>
