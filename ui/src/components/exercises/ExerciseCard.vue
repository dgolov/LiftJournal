<template>
  <div
    class="card p-4 hover:shadow-md transition-shadow cursor-pointer"
    @click="$router.push(`/exercises/${exercise.id}`)"
  >
    <div class="flex items-start justify-between gap-2 mb-2">
      <h3 class="font-semibold text-gray-900 dark:text-white text-sm leading-tight">{{ exercise.name }}</h3>
      <BaseBadge v-if="exercise.isCustom" color="purple" class="flex-shrink-0">Своё</BaseBadge>
    </div>
    <div class="flex flex-wrap gap-1 mb-3">
      <BaseBadge color="indigo">{{ exercise.muscleGroup }}</BaseBadge>
      <BaseBadge color="gray">{{ exercise.equipment }}</BaseBadge>
    </div>
    <div v-if="pr" class="text-xs text-gray-500 dark:text-gray-400">
      <span class="font-medium text-yellow-600">PR: </span>
      <template v-if="isCardio">{{ pr.bestDuration }} мин.</template>
      <template v-else>{{ pr.bestWeight > 0 ? pr.bestWeight + ' кг × ' + pr.bestWeightReps + ' повт.' : pr.bestWeightReps + ' повт.' }}</template>
    </div>
    <div v-else class="text-xs text-gray-300">Нет записей</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import BaseBadge from '@/components/ui/BaseBadge.vue'

const props = defineProps({
  exercise: { type: Object, required: true }
})

const store = useStore()
const pr = computed(() => store.getters['exercises/personalRecord'](props.exercise.id))
const isCardio = computed(() => props.exercise.muscleGroup === 'Кардио')
</script>
