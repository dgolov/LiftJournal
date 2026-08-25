<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Дашборд</h2>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Загрузка...</div>
    <p v-else-if="error" class="text-sm text-danger">{{ error }}</p>

    <div v-else class="space-y-5">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="card p-4">
          <div class="flex items-center gap-2 text-gray-400 text-xs font-medium uppercase tracking-wide">
            <Users class="w-4 h-4" /> Пользователи
          </div>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.totalUsers }}</p>
          <p class="text-xs text-gray-400 mt-0.5">+{{ stats.newUsersLast7Days }} за 7 дней</p>
        </div>
        <div class="card p-4">
          <div class="flex items-center gap-2 text-gray-400 text-xs font-medium uppercase tracking-wide">
            <Dumbbell class="w-4 h-4" /> Тренировки
          </div>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.totalWorkouts }}</p>
          <p class="text-xs text-gray-400 mt-0.5">+{{ stats.workoutsLast7Days }} за 7 дней</p>
        </div>
        <div class="card p-4">
          <div class="flex items-center gap-2 text-gray-400 text-xs font-medium uppercase tracking-wide">
            <ListChecks class="w-4 h-4" /> Упражнения
          </div>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.totalExercises }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ stats.customExercises }} пользовательских · {{ stats.pendingExercises }} на модерации</p>
        </div>
        <div class="card p-4">
          <div class="flex items-center gap-2 text-gray-400 text-xs font-medium uppercase tracking-wide">
            <LayoutGrid class="w-4 h-4" /> Циклы
          </div>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stats.totalCycles }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ stats.publicCycles }} публичных · {{ stats.pendingCycles }} на модерации</p>
        </div>
      </div>

      <div class="card p-4">
        <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Тренировки за 14 дней</p>
        <div class="flex items-end gap-1.5 h-32">
          <div
            v-for="d in stats.dailyWorkouts"
            :key="d.date"
            class="flex-1 h-full flex flex-col items-center justify-end gap-1 group relative"
          >
            <span class="text-[10px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">{{ d.count }}</span>
            <div
              class="w-full rounded-t bg-primary/70 group-hover:bg-primary transition-colors min-h-[3px]"
              :style="{ height: barHeight(d.count) + '%' }"
            ></div>
            <span class="text-[10px] text-gray-400">{{ shortDate(d.date) }}</span>
          </div>
        </div>
      </div>

      <div class="card overflow-hidden">
        <p class="text-sm font-semibold text-gray-900 dark:text-white px-4 pt-4 pb-2">Самые активные пользователи</p>
        <table v-if="stats.topUsers.length" class="w-full text-sm">
          <tbody>
            <tr v-for="(u, i) in stats.topUsers" :key="u.id" class="border-t border-gray-50 dark:border-gray-800/60">
              <td class="px-4 py-2.5 text-gray-400 w-8">{{ i + 1 }}</td>
              <td class="px-4 py-2.5 font-medium text-gray-900 dark:text-white">{{ u.name || '—' }}</td>
              <td class="px-4 py-2.5 text-right text-gray-500">{{ u.workoutCount }} тренировок</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-center py-8 text-gray-400 text-sm">Пока нет данных</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Users, Dumbbell, ListChecks, LayoutGrid } from 'lucide-vue-next'
import adminService from '@/services/adminService.js'

const stats = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await adminService.fetchStats()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function barHeight(count) {
  const max = Math.max(...stats.value.dailyWorkouts.map(d => d.count), 1)
  return count === 0 ? 2 : Math.max((count / max) * 100, 6)
}

function shortDate(isoDate) {
  const [, month, day] = isoDate.split('-')
  return `${day}.${month}`
}
</script>
