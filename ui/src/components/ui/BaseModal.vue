<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" :class="['fixed inset-0 z-50 flex', fullscreen ? 'items-end sm:items-center sm:p-4' : 'items-center justify-center p-4']">
        <div class="absolute inset-0 bg-black/50" @click="$emit('update:modelValue', false)" />
        <div :class="[
          'relative bg-white shadow-xl w-full flex flex-col',
          fullscreen
            ? 'h-full sm:h-auto sm:rounded-2xl sm:max-h-[90vh] ' + maxWidthClass
            : 'rounded-2xl max-h-[90vh] ' + maxWidthClass
        ]">
          <div v-if="title" class="flex items-center justify-between px-6 pt-5 pb-3 border-b border-gray-100 flex-shrink-0">
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
            <button class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600" @click="$emit('update:modelValue', false)">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="p-6 overflow-y-auto flex-1">
            <slot />
          </div>
          <div v-if="$slots.footer" class="px-6 pb-5 pt-3 flex justify-end gap-3 flex-shrink-0 border-t border-gray-100">
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
  maxWidth: { type: String, default: 'lg' },
  fullscreen: { type: Boolean, default: false }
})
defineEmits(['update:modelValue'])

const maxWidthMap = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-lg', xl: 'max-w-xl', '2xl': 'max-w-2xl' }
const maxWidthClass = maxWidthMap[props.maxWidth] || 'max-w-lg'
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
