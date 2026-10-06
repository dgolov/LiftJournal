<template>
  <div class="overflow-x-auto -mx-1 px-1">
    <div class="min-w-[18rem] text-sm tabular-nums" role="table" :aria-label="compare ? 'Подходы: план и факт' : 'Подходы'">
      <!-- Head -->
      <div class="grid items-end gap-x-2 sm:gap-x-3 pb-1.5 border-b border-steel-100 dark:border-steel-700 text-xs text-steel-700 dark:text-steel-300"
        :style="gridStyle" role="row">
        <span role="columnheader" class="text-right">№</span>
        <span v-if="compare" role="columnheader">План</span>
        <span role="columnheader">Факт</span>
        <span v-if="hasRpe" role="columnheader" class="text-right">RPE</span>
        <span v-if="compare" role="columnheader">Отклонение</span>
        <span v-else aria-hidden="true" />
        <span v-if="wide" role="columnheader" class="text-right" title="Вес подхода в процентах от 1ПМ на дату тренировки">% 1ПМ</span>
      </div>

      <!-- Unplanned warm-up: shown for the record, never judged against the plan -->
      <div
        v-for="(set, i) in aligned.warmups" :key="'w' + i"
        class="grid items-center gap-x-2 sm:gap-x-3 py-1.5 border-b border-steel-100/70 dark:border-steel-700/60 text-steel-300"
        :style="gridStyle"
        role="row"
      >
        <span role="cell" />
        <span v-if="compare" role="cell" class="text-xs">разминка</span>
        <span role="cell"><SetValue :set="set" /></span>
        <span v-if="hasRpe" role="cell" class="text-right text-xs">{{ set.rpe ?? '' }}</span>
        <span role="cell" />
        <span v-if="wide" role="cell" class="text-right text-xs">{{ percent(set) }}</span>
      </div>

      <!-- Working sets: planned set N against the athlete's N-th working set -->
      <div
        v-for="row in rows" :key="row.n"
        class="grid items-center gap-x-2 sm:gap-x-3 py-1.5 border-b border-steel-100/70 dark:border-steel-700/60 last:border-b-0"
        :style="gridStyle"
        role="row"
      >
        <span role="cell" class="text-right text-xs text-steel-300">{{ row.n }}</span>

        <span v-if="compare" role="cell" class="text-steel-700 dark:text-steel-300">
          <SetValue v-if="row.plan" :set="row.plan" />
          <span v-else class="text-steel-300">—</span>
        </span>

        <span role="cell" :class="row.fact?.failed ? 'text-steel-300 line-through decoration-primary/60' : 'text-ink dark:text-white font-medium'">
          <SetValue v-if="row.fact" :set="row.fact" />
          <span v-else class="text-steel-300 no-underline">—</span>
        </span>

        <span v-if="hasRpe" role="cell" class="text-right text-xs text-steel-700 dark:text-steel-300">
          {{ row.fact?.rpe ?? '' }}
        </span>

        <span v-if="compare" role="cell" :class="['text-xs', row.delta.tone]">
          <Check v-if="row.delta.onPlan" class="w-3.5 h-3.5" aria-label="по плану" />
          <template v-else>{{ row.delta.text }}</template>
        </span>

        <span v-if="!compare" aria-hidden="true" />

        <span v-if="wide" role="cell" class="text-right text-xs text-steel-700 dark:text-steel-300">
          {{ percent(row.fact) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, onBeforeUnmount, ref } from 'vue'
import { Check } from 'lucide-vue-next'
import { alignSets } from '@/utils/setAlignment.js'

const props = defineProps({
  planSets: { type: Array, default: null },
  factSets: { type: Array, default: null },
  oneRepMax: { type: Number, default: 0 },
  compare: { type: Boolean, default: false },
})

// "102.5 × 5" laid out on a tiny grid so the × lines up down the column:
// weight right-aligned, reps left-aligned.
const SetValue = (p) => h('span', { class: 'inline-grid grid-cols-[3rem_1rem_1.5rem] items-baseline' }, [
  h('span', { class: 'text-right' }, p.set.weight > 0 ? `${p.set.weight}` : 'б/в'),
  h('span', { class: 'text-center text-steel-300 text-xs' }, '×'),
  h('span', null, `${p.set.reps}`),
])
SetValue.props = ['set']

// On phones the % of 1RM column is dropped (it's in the exercise's summary
// line as relative intensity) so plan, fact and deviation fit without scrolling.
const media = window.matchMedia('(min-width: 640px)')
const wide = ref(media.matches)
const onMedia = e => { wide.value = e.matches }
media.addEventListener('change', onMedia)
onBeforeUnmount(() => media.removeEventListener('change', onMedia))

const hasRpe = computed(() => (props.factSets || []).some(s => s.rpe))

// Column set depends on mode and data, so it's an inline style — Tailwind
// can't generate arbitrary grid classes assembled at runtime.
const gridStyle = computed(() => {
  // Set columns are exactly as wide as a "102.5 × 10" value so headers sit
  // over their numbers; the leftover width goes to the deviation note.
  const cols = ['1.25rem']
  if (props.compare) cols.push('5.5rem')
  cols.push('5.5rem')
  if (hasRpe.value) cols.push('2rem')
  if (props.compare) cols.push('minmax(4.5rem, 1fr)')
  else cols.push('1fr')
  if (wide.value) cols.push('2.75rem')
  return { gridTemplateColumns: cols.join(' ') }
})

function fmt(n) {
  return Number.isInteger(n) ? `${n}` : `${Math.round(n * 10) / 10}`
}

function deltaFor(plan, fact) {
  if (!fact) return { text: 'не выполнен', tone: 'text-steel-300' }
  if (!plan) return { text: 'сверх плана', tone: 'text-steel-700 dark:text-steel-300' }
  if (fact.failed) return { text: 'провал', tone: 'text-primary' }
  const dw = (fact.weight || 0) - (plan.weight || 0)
  const dr = (fact.reps || 0) - (plan.reps || 0)
  if (!dw && !dr) return { onPlan: true, tone: 'text-success' }
  const parts = []
  if (dw) parts.push(`${dw > 0 ? '+' : '−'}${fmt(Math.abs(dw))} кг`)
  if (dr) parts.push(`${dr > 0 ? '+' : '−'}${Math.abs(dr)} повт`)
  // Tone by what happened to the work done: more tonnage than asked reads as
  // "over" (hazard), less as "under" (primary).
  const dTonnage = fact.weight * fact.reps - plan.weight * plan.reps
  return { text: parts.join(', '), tone: dTonnage >= 0 ? 'text-hazard' : 'text-primary' }
}

const aligned = computed(() => alignSets(props.compare ? props.planSets : null, props.factSets))
const rows = computed(() => aligned.value.rows.map(r => ({ ...r, delta: deltaFor(r.plan, r.fact) })))

function percent(set) {
  if (!set || set.failed || !set.weight || !props.oneRepMax) return ''
  return `${Math.round(set.weight / props.oneRepMax * 100)}`
}
</script>
