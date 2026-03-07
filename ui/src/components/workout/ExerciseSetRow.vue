<template>
  <div class="flex items-center gap-2">
    <span class="text-xs text-gray-400 w-6 text-center flex-shrink-0">{{ index + 1 }}</span>
    <input
      type="number"
      :value="set.weight"
      min="0"
      step="0.5"
      placeholder="кг"
      class="input w-20 text-center text-sm"
      @input="update('weight', +$event.target.value)"
    />
    <span class="text-gray-300 text-sm">×</span>
    <input
      type="number"
      :value="set.reps"
      min="0"
      placeholder="повт"
      class="input w-20 text-center text-sm"
      @input="update('reps', +$event.target.value)"
    />
    <button
      :class="['w-8 h-8 rounded-full border-2 flex items-center justify-center transition-colors flex-shrink-0',
        set.completed ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 text-transparent hover:border-green-400']"
      @click="update('completed', !set.completed)"
    >✓</button>
    <button
      class="p-1 text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
      @click="$emit('remove')"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  set: { type: Object, required: true },
  exerciseId: { type: String, required: true },
  index: { type: Number, required: true }
})
const emit = defineEmits(['remove'])

import { useStore } from 'vuex'
const store = useStore()

function update(field, value) {
  store.commit('workouts/UPDATE_SET', { exerciseId: props.exerciseId, setId: props.set.id, field, value })
}
</script>
