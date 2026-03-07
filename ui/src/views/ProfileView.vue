<template>
  <div class="space-y-6">
    <!-- Profile header -->
    <div class="card p-5 flex items-center gap-4">
      <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary">
        {{ profile.name?.charAt(0) || '?' }}
      </div>
      <div class="flex-1">
        <h2 class="text-xl font-bold text-gray-900">{{ profile.name }}</h2>
        <p class="text-sm text-gray-500">{{ profile.age }} лет</p>
      </div>
      <BaseButton variant="outline" size="sm" @click="showEditProfile = true">Изменить</BaseButton>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <StatCard label="Всего тренировок" :value="totalWorkouts" />
      <StatCard label="На этой неделе" :value="thisWeek" />
      <StatCard label="Серия (дней)" :value="streak" />
      <StatCard label="Общий объём" :value="formattedVolume" sub="тонн" />
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Weight -->
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900">Вес</h3>
          <span v-if="currentWeight" class="text-sm font-bold text-primary">{{ currentWeight.kg }} кг</span>
        </div>
        <WeightChart :data="weightHistory" />
        <div class="mt-4 border-t border-gray-100 pt-4">
          <p class="text-sm font-medium text-gray-700 mb-2">Записать вес</p>
          <div class="flex gap-2">
            <input type="date" v-model="weightForm.date" class="input flex-1" />
            <input type="number" v-model.number="weightForm.kg" step="0.1" min="20" max="300" placeholder="кг" class="input w-24" />
            <BaseButton :disabled="!weightForm.kg" @click="logWeight">Сохранить</BaseButton>
          </div>
        </div>
      </div>

      <!-- Goals -->
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900">Цели</h3>
          <BaseButton variant="outline" size="sm" @click="showAddGoal = true">+ Цель</BaseButton>
        </div>

        <div v-if="goals.length" class="space-y-2">
          <div v-for="goal in goals" :key="goal.id"
            class="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50">
            <button
              :class="['w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 transition-colors flex items-center justify-center text-xs font-bold',
                goal.done ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 hover:border-green-400']"
              @click="toggleGoal(goal.id)"
            >{{ goal.done ? '✓' : '' }}</button>
            <div class="flex-1 min-w-0">
              <p :class="['text-sm font-medium', goal.done ? 'line-through text-gray-400' : 'text-gray-900']">
                {{ goal.text }}
              </p>
              <p class="text-xs text-gray-400">до {{ formatDate(goal.targetDate) }}</p>
            </div>
            <button class="text-gray-200 hover:text-red-400 transition-colors text-xs" @click="deleteGoal(goal.id)">✕</button>
          </div>
        </div>

        <BaseEmptyState v-else icon="🎯" title="Нет целей" description="Поставьте себе цель!" />
      </div>
    </div>

    <!-- Edit profile modal -->
    <BaseModal v-model="showEditProfile" title="Редактировать профиль">
      <div class="space-y-4">
        <BaseInput v-model="editForm.name" label="Имя" />
        <BaseInput v-model.number="editForm.age" type="number" label="Возраст" min="10" max="100" />
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showEditProfile = false">Отмена</BaseButton>
        <BaseButton @click="saveProfile">Сохранить</BaseButton>
      </template>
    </BaseModal>

    <!-- Add goal modal -->
    <BaseModal v-model="showAddGoal" title="Новая цель">
      <div class="space-y-4">
        <BaseInput v-model="goalForm.text" label="Цель" placeholder="Например: Жим лёжа 100 кг" />
        <BaseInput v-model="goalForm.targetDate" type="date" label="Дата дедлайна" />
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showAddGoal = false">Отмена</BaseButton>
        <BaseButton :disabled="!goalForm.text" @click="addGoal">Добавить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useStore } from 'vuex'
import StatCard from '@/components/profile/StatCard.vue'
import WeightChart from '@/components/profile/WeightChart.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'

const store = useStore()

const profile = computed(() => store.state.user.profile)
const currentWeight = computed(() => store.getters['user/currentWeight'])
const weightHistory = computed(() => store.getters['user/weightHistory'])
const goals = computed(() => store.state.user.goals)

const totalWorkouts = computed(() => store.state.workouts.workouts.length)
const thisWeek = computed(() => store.getters['workouts/workoutsThisWeek'])
const streak = computed(() => store.getters['workouts/longestStreak'])
const formattedVolume = computed(() => {
  const v = store.getters['workouts/totalVolume']
  return (v / 1000).toFixed(1)
})

// Modals
const showEditProfile = ref(false)
const showAddGoal = ref(false)

const editForm = reactive({ name: profile.value.name, age: profile.value.age })
const goalForm = reactive({ text: '', targetDate: new Date().toISOString().split('T')[0] })
const weightForm = reactive({ date: new Date().toISOString().split('T')[0], kg: null })

function formatDate(date) {
  return new Date(date + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

async function saveProfile() {
  await store.dispatch('user/updateProfile', { ...editForm })
  store.dispatch('ui/showToast', { message: 'Профиль обновлён', type: 'success' })
  showEditProfile.value = false
}

async function logWeight() {
  await store.dispatch('user/logWeight', { date: weightForm.date, kg: weightForm.kg })
  store.dispatch('ui/showToast', { message: 'Вес записан!', type: 'success' })
  weightForm.kg = null
}

async function addGoal() {
  await store.dispatch('user/saveGoal', { ...goalForm, done: false })
  store.dispatch('ui/showToast', { message: 'Цель добавлена!', type: 'success' })
  goalForm.text = ''
  showAddGoal.value = false
}

async function toggleGoal(id) { await store.dispatch('user/toggleGoal', id) }
async function deleteGoal(id) { await store.dispatch('user/deleteGoal', id) }
</script>
