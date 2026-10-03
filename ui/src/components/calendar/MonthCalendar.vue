<template>
  <div>
    <div class="grid grid-cols-7 mb-1.5">
      <div v-for="d in WEEK_DAYS" :key="d" class="text-center text-xs font-medium text-steel-700 dark:text-steel-300 py-1">{{ d }}</div>
    </div>

    <div class="grid grid-cols-7 gap-px rounded-2xl overflow-hidden bg-steel-100 dark:bg-steel-700 border border-steel-100 dark:border-steel-700">
      <button
        v-for="day in days"
        :key="day.dateStr"
        :class="cellClass(day, selected)"
        class="min-h-[74px] sm:min-h-[92px] p-1 sm:p-1.5 flex flex-col items-stretch text-left"
        @click="$emit('select', day)"
      >
        <span :class="dayNumberClass(day, todayStr)">{{ day.date.getDate() }}</span>
        <div class="flex-1 flex flex-col gap-0.5 mt-1 overflow-hidden">
          <span
            v-for="(item, i) in itemsFor(day.dateStr).slice(0, 2)" :key="i"
            :class="['text-[9px] leading-tight px-1 py-0.5 rounded truncate', chipClass(item)]"
          >{{ item.label }}</span>
          <span v-if="itemsFor(day.dateStr).length > 2" class="text-[9px] text-steel-700 dark:text-steel-300 px-1">
            +{{ itemsFor(day.dateStr).length - 2 }} ещё
          </span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { WEEK_DAYS, monthDays, cellClass, dayNumberClass, chipClass, toDateStr } from './calendarStyles.js'

const props = defineProps({
  year: { type: Number, required: true },
  month: { type: Number, required: true },          // 0-based
  // dateStr → [{ label, kind: 'workout', type } | { label, kind: 'plan', status }]
  itemsFor: { type: Function, required: true },
  selected: { type: String, default: null },
})
defineEmits(['select'])

const days = computed(() => monthDays(props.year, props.month))
const todayStr = toDateStr(new Date())
</script>
