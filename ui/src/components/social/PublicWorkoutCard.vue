<template>
  <RouterLink :to="`/workouts/${workout.id}`" class="card p-4 block hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between gap-2 mb-1">
      <p class="font-semibold text-gray-900 dark:text-white leading-tight">{{ workout.title || 'Тренировка' }}</p>
      <BaseBadge :color="typeColor">{{ workout.type }}</BaseBadge>
    </div>
    <p class="text-xs text-gray-500 mb-2">
      {{ formatDate(workout.date) }}
      <span v-if="workout.durationMinutes"> · {{ workout.durationMinutes }} мин</span>
      · {{ workout.exercises.length }} упр.
    </p>
    <div class="flex flex-wrap gap-1.5 mb-2">
      <span
        v-for="ex in workout.exercises.slice(0, 4)"
        :key="ex.exerciseId"
        class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
      >{{ ex.exerciseName }}</span>
      <span v-if="workout.exercises.length > 4" class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-400">
        +{{ workout.exercises.length - 4 }}
      </span>
    </div>
    <div class="flex items-center gap-4 text-xs text-gray-400">
      <span class="flex items-center gap-1">
        <Heart class="w-3 h-3" :class="workout.isLiked ? 'fill-red-400 text-red-400' : ''" />
        {{ workout.likesCount || 0 }}
      </span>
      <span class="flex items-center gap-1">
        <MessageCircle class="w-3 h-3" />
        {{ workout.commentsCount || 0 }}
      </span>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { Heart, MessageCircle } from 'lucide-vue-next'
import BaseBadge from '@/components/ui/BaseBadge.vue'

const props = defineProps({
  workout: { type: Object, required: true },
})

const typeColorMap = { 'Силовая': 'indigo', 'Кардио': 'green', 'Растяжка': 'purple', 'HIIT': 'orange', 'Другое': 'gray' }
const typeColor = computed(() => typeColorMap[props.workout.type] || 'gray')

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>
