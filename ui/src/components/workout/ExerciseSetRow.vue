<template>
  <div :class="['flex items-center gap-1 transition-opacity', set.failed ? 'opacity-50' : '']">
    <span class="text-xs font-mono text-steel-700 dark:text-steel-300 w-5 text-center flex-shrink-0">{{ index + 1 }}</span>

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
        :class="['flex-1', set.failed ? 'line-through' : '']"
        :model-value="set.weight"
        :step="0.5"
        :decimals="1"
        placeholder="кг"
        @update:model-value="update('weight', $event)"
      />
      <span class="text-steel-300 text-sm flex-shrink-0">×</span>
      <StepperInput
        :class="['flex-1', set.failed ? 'line-through' : '']"
        :model-value="set.reps"
        :step="1"
        placeholder="повт"
        @update:model-value="update('reps', $event)"
      />
    </template>

    <!-- 3-state toggle: none → completed → failed → none -->
    <button
      :class="['w-9 h-9 rounded-full border-2 flex items-center justify-center transition-colors flex-shrink-0',
        set.completed ? 'bg-success border-success text-white' :
        set.failed    ? 'bg-primary border-primary text-white' :
                        'border-steel-300 text-transparent hover:border-success']"
      :title="set.completed ? 'Выполнено (нажмите — провал)' : set.failed ? 'Провал (нажмите — сбросить)' : 'Отметить выполненным'"
      @click="cycleState"
    >
      <Check v-if="set.completed" class="w-4 h-4" />
      <X v-else-if="set.failed" class="w-4 h-4" />
      <Check v-else class="w-4 h-4" />
    </button>
    <button
      class="w-7 h-9 flex items-center justify-center text-steel-300 hover:text-primary transition-colors flex-shrink-0"
      @click="$emit('remove')"
    >
      <X class="w-5 h-5" />
    </button>
  </div>
</template>

<script setup>
import { Check, X } from 'lucide-vue-next'
import StepperInput from '@/components/ui/StepperInput.vue'
import { useStore } from 'vuex'
import { useRestTimer } from '@/composables/useRestTimer.js'

const props = defineProps({
  set: { type: Object, required: true },
  instanceId: { type: String, required: true },
  index: { type: Number, required: true },
  isCardio: { type: Boolean, default: false }
})
const emit = defineEmits(['remove'])

const store = useStore()
const { start: startTimer } = useRestTimer()

function update(field, value) {
  store.commit('workouts/UPDATE_SET', { instanceId: props.instanceId, setId: props.set.id, field, value })
}

function cycleState() {
  if (!props.set.completed && !props.set.failed) {
    // none → completed
    update('completed', true)
    update('failed', false)
    startTimer()
  } else if (props.set.completed) {
    // completed → failed
    update('completed', false)
    update('failed', true)
  } else {
    // failed → none
    update('failed', false)
  }
}
</script>
