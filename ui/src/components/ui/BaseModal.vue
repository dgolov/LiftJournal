<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="$emit('update:modelValue', false)" />
        <div :class="['relative bg-white rounded-2xl shadow-xl w-full', maxWidthClass]">
          <div v-if="title" class="flex items-center justify-between px-6 pt-5 pb-3 border-b border-gray-100">
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
            <button class="text-gray-400 hover:text-gray-600" @click="$emit('update:modelValue', false)">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="p-6">
            <slot />
          </div>
          <div v-if="$slots.footer" class="px-6 pb-5 flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  title: String,
  maxWidth: { type: String, default: 'lg' }
})
defineEmits(['update:modelValue'])

const maxWidthMap = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-lg', xl: 'max-w-xl', '2xl': 'max-w-2xl' }
const maxWidthClass = maxWidthMap[props.maxWidth] || 'max-w-lg'
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
