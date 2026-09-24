<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" :class="['fixed inset-0 z-50 flex', fullscreen ? 'items-end sm:items-center sm:p-4' : 'items-center justify-center p-4']">
        <div class="absolute inset-0 bg-ink/60" @click="$emit('update:modelValue', false)" />
        <div :class="[
          'relative bg-card dark:bg-steel-900 border-2 border-ink dark:border-steel-100 shadow-[6px_6px_0_theme(colors.ink)] dark:shadow-[6px_6px_0_black] w-full flex flex-col',
          fullscreen
            ? 'h-full sm:h-auto sm:max-h-[90vh] ' + maxWidthClass
            : 'max-h-[90vh] ' + maxWidthClass
        ]">
          <div v-if="title" class="flex items-center justify-between px-6 pt-5 pb-3 border-b-2 border-steel-100 dark:border-steel-700 flex-shrink-0">
            <h3 class="text-lg font-display font-semibold text-ink dark:text-white">{{ title }}</h3>
            <button class="w-8 h-8 flex items-center justify-center text-steel-300 hover:text-ink dark:text-steel-700 dark:hover:text-steel-100 transition-colors" @click="$emit('update:modelValue', false)">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-6 overflow-y-auto flex-1">
            <slot />
          </div>
          <div v-if="$slots.footer" class="px-6 pb-5 pt-3 flex justify-end gap-3 flex-shrink-0 border-t-2 border-steel-100 dark:border-steel-700">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { X } from 'lucide-vue-next'

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
