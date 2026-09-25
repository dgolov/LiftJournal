<template>
  <div class="flex items-stretch min-w-0">
    <button
      type="button"
      class="w-7 flex-shrink-0 flex items-center justify-center text-base font-display font-bold text-steel-700 dark:text-steel-300 hover:text-primary bg-steel-50 dark:bg-steel-700 border border-steel-100 dark:border-steel-700 border-r-0 rounded-l-xl active:bg-steel-300 dark:active:bg-steel-950 transition-colors select-none"
      @click="adjust(-step)"
    >−</button>
    <input
      type="text"
      inputmode="decimal"
      :value="displayValue"
      :placeholder="placeholder"
      class="w-full min-w-0 border border-steel-100 dark:border-steel-700 bg-white dark:bg-steel-900 text-ink dark:text-white font-mono px-0.5 py-2.5 text-sm text-center placeholder-steel-300 focus:border-primary focus:outline-none focus:z-10 min-h-[44px]"
      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"
    />
    <button
      type="button"
      class="w-7 flex-shrink-0 flex items-center justify-center text-base font-display font-bold text-steel-700 dark:text-steel-300 hover:text-primary bg-steel-50 dark:bg-steel-700 border border-steel-100 dark:border-steel-700 border-l-0 rounded-r-xl active:bg-steel-300 dark:active:bg-steel-950 transition-colors select-none"
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
  max: { type: Number, default: Infinity },
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
  if (!isNaN(num) && num >= props.min && num <= props.max) {
    raw.value = String(num)
    emit('update:modelValue', num)
  } else if (!isNaN(num)) {
    // Out of range — clamp rather than silently reject, so a typo like
    // "15" for an RPE field lands on the nearest valid value instead of
    // just reverting with no feedback.
    const clamped = Math.min(props.max, Math.max(props.min, num))
    raw.value = String(clamped)
    emit('update:modelValue', clamped)
  } else {
    raw.value = formatNum(props.modelValue)
  }
}

function onInput(e) {
  raw.value = e.target.value
  const num = parse(e.target.value)
  if (!isNaN(num) && num >= props.min && num <= props.max) {
    emit('update:modelValue', num)
  }
}

function adjust(delta) {
  const current = parse(raw.value) || 0
  const next = Math.min(props.max, Math.max(props.min, Math.round((current + delta) * 1000) / 1000))
  raw.value = String(next)
  emit('update:modelValue', next)
}

const displayValue = raw
</script>
