<template>
  <div class="flex items-center gap-1">
    <span class="text-xs text-gray-400 w-5 text-center flex-shrink-0">{{ index + 1 }}</span>

    <template v-if="isCardio">
      <StepperInput
        class="flex-1"
        :model-value="set.reps"
        :step="1"
        placeholder="мин"
        @update:model-value="update('reps', $event)"
      />
    </template>
    <template v-else>
      <StepperInput
        class="flex-1"
        :model-value="set.weight"
        :step="0.5"
        :decimals="1"
        placeholder="кг"
        @update:model-value="update('weight', $event)"
      />
      <span class="text-gray-300 text-sm flex-shrink-0">×</span>
      <StepperInput
        class="flex-1"
        :model-value="set.reps"
        :step="1"
        placeholder="повт"
        @update:model-value="update('reps', $event)"
      />
    </template>

    <button
      :class="['w-9 h-9 rounded-full border-2 flex items-center justify-center transition-colors flex-shrink-0 text-sm font-bold',
        set.completed ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 text-transparent hover:border-green-400']"
      @click="update('completed', !set.completed)"
    >✓</button>
    <button
      class="w-7 h-9 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
      @click="$emit('remove')"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import StepperInput from '@/components/ui/StepperInput.vue'
import { useStore } from 'vuex'

const props = defineProps({
  set: { type: Object, required: true },
  exerciseId: { type: String, required: true },
  index: { type: Number, required: true },
  isCardio: { type: Boolean, default: false }
})
const emit = defineEmits(['remove'])

const store = useStore()

function update(field, value) {
  store.commit('workouts/UPDATE_SET', { exerciseId: props.exerciseId, setId: props.set.id, field, value })
}
</script>
