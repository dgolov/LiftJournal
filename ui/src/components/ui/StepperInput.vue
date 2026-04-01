<template>
  <div class="flex items-stretch min-w-0">
    <button
      type="button"
      class="w-7 flex-shrink-0 flex items-center justify-center text-base text-gray-400 hover:text-primary bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-l-lg border-r-0 active:bg-gray-100 dark:active:bg-gray-600 transition-colors select-none"
      @click="adjust(-step)"
    >−</button>
    <input
      type="text"
      inputmode="decimal"
      :value="displayValue"
      :placeholder="placeholder"
      class="w-full min-w-0 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-0.5 py-2.5 text-sm text-center placeholder-gray-400 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary focus:z-10 min-h-[44px]"
      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"
    />
    <button
      type="button"
      class="w-7 flex-shrink-0 flex items-center justify-center text-base text-gray-400 hover:text-primary bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-r-lg border-l-0 active:bg-gray-100 dark:active:bg-gray-600 transition-colors select-none"
      @click="adjust(step)"
    >+</button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: null },
  step: { type: Number, default: 1 },
  min: { type: Number, default: 0 },
  placeholder: { type: String, default: '' },
  decimals: { type: Number, default: 0 }
})
const emit = defineEmits(['update:modelValue'])

const focused = ref(false)
const raw = ref(formatNum(props.modelValue))

watch(() => props.modelValue, (val) => {
  if (!focused.value) raw.value = formatNum(val)
})

function formatNum(val) {
  if (val == null || val === 0) return ''
  return props.decimals > 0 ? String(val) : String(val)
}

function parse(str) {
  return parseFloat(String(str).replace(',', '.'))
}

function onFocus(e) {
  focused.value = true
  e.target.select()
}

function onBlur() {
  focused.value = false
  const num = parse(raw.value)
  if (!isNaN(num) && num >= props.min) {
    const rounded = Math.round(num / props.step) * props.step
    const fixed = parseFloat(rounded.toFixed(10))
    raw.value = String(fixed)
    emit('update:modelValue', fixed)
  } else {
    raw.value = formatNum(props.modelValue)
  }
}

function onInput(e) {
  raw.value = e.target.value
  const num = parse(e.target.value)
  if (!isNaN(num) && num >= props.min) {
    emit('update:modelValue', num)
  }
}

function adjust(delta) {
  const current = parse(raw.value) || 0
  const next = Math.max(props.min, Math.round((current + delta) * 1000) / 1000)
  raw.value = String(next)
  emit('update:modelValue', next)
}

const displayValue = raw
</script>
