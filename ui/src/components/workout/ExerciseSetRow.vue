<template>
  <SwipeDeleteWrapper :bordered="false" delete-label="Удалить подход" @delete="$emit('remove')">
  <div :class="['flex items-center gap-1 py-0.5 bg-card dark:bg-steel-900 transition-opacity', set.failed ? 'opacity-50' : '']">
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
      <input
        type="text"
        inputmode="decimal"
        :value="rpeRaw"
        placeholder="РПЕ"
        title="RPE — субъективная тяжесть подхода, 1–10 (необязательно)"
        class="w-10 flex-shrink-0 rounded-lg border border-steel-100 dark:border-steel-700 bg-white dark:bg-steel-900 text-ink dark:text-white font-mono px-0.5 py-2 text-xs text-center placeholder-steel-300 focus:border-primary focus:outline-none"
        @focus="onRpeFocus"
        @blur="onRpeBlur"
        @input="rpeRaw = $event.target.value"
      />
    </template>

    <!-- 3-state toggle: none → completed → failed → none -->
    <button
      :class="['w-9 h-9 rounded-full border flex items-center justify-center transition-colors flex-shrink-0',
        set.completed ? 'bg-success border-success text-white' :
        set.failed    ? 'bg-primary border-primary text-white' :
                        'bg-card dark:bg-steel-900 border-steel-300 text-transparent hover:border-success']"
      :title="set.completed ? 'Выполнено (нажмите — провал)' : set.failed ? 'Провал (нажмите — сбросить)' : 'Отметить выполненным'"
      @click="cycleState"
    >
      <Check v-if="set.completed" class="w-4 h-4" />
      <X v-else-if="set.failed" class="w-4 h-4" />
      <Check v-else class="w-4 h-4" />
    </button>
    <button
      class="hidden lg:flex w-7 h-9 items-center justify-center text-steel-300 hover:text-primary transition-colors flex-shrink-0"
      title="Удалить подход"
      @click="$emit('remove')"
    >
      <X class="w-5 h-5" />
    </button>
  </div>
  </SwipeDeleteWrapper>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Check, X } from 'lucide-vue-next'
import StepperInput from '@/components/ui/StepperInput.vue'
import SwipeDeleteWrapper from '@/components/ui/SwipeDeleteWrapper.vue'
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

// RPE — plain text field (no +/- steppers, unlike weight/reps) since it's an
// optional, occasionally-filled value and the set row has no room to spare.
const rpeFocused = ref(false)
const rpeRaw = ref(formatRpe(props.set.rpe))

watch(() => props.set.rpe, (val) => {
  if (!rpeFocused.value) rpeRaw.value = formatRpe(val)
})

function formatRpe(val) {
  return val == null ? '' : String(val)
}

function onRpeFocus(e) {
  rpeFocused.value = true
  e.target.select()
}

function onRpeBlur() {
  rpeFocused.value = false
  const raw = rpeRaw.value.trim()
  if (!raw) { rpeRaw.value = ''; update('rpe', null); return }
  const num = parseFloat(raw.replace(',', '.'))
  if (isNaN(num)) { rpeRaw.value = formatRpe(props.set.rpe); return }
  // RPE is conventionally whole or half points (7, 7.5, 8...) — snap to it.
  const clamped = Math.min(10, Math.max(1, Math.round(num * 2) / 2))
  rpeRaw.value = String(clamped)
  update('rpe', clamped)
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
