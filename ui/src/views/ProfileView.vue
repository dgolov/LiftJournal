<template>
  <div class="space-y-6">
    <!-- Profile header -->
    <div class="card p-5 flex items-center gap-4">
      <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary flex-shrink-0">
        {{ profile.name?.charAt(0) || '?' }}
      </div>
      <div class="flex-1 min-w-0">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ profile.name }}</h2>
        <p class="text-sm text-gray-500">{{ profile.age }} лет</p>
      </div>
      <BaseButton variant="outline" size="sm" @click="showEditProfile = true">Изменить</BaseButton>
    </div>

    <!-- Account -->
    <div class="card p-4 flex items-center justify-between gap-4">
      <div>
        <p class="text-sm font-medium text-gray-700 dark:text-gray-200">Аккаунт</p>
        <p class="text-xs text-gray-400 mt-0.5">{{ userName }}</p>
      </div>
      <BaseButton variant="danger" size="sm" @click="logout">Выйти</BaseButton>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <StatCard label="Всего тренировок" :value="totalWorkouts" />
      <StatCard label="На этой неделе" :value="thisWeek" />
      <StatCard label="Серия (дней)" :value="streak" />
      <StatCard label="Общий тоннаж" :value="formattedVolume" sub="тонн" />
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Weight -->
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 dark:text-white">Вес</h3>
          <span v-if="currentWeight" class="text-sm font-bold text-primary">{{ currentWeight.kg }} кг</span>
        </div>
        <WeightChart :data="weightHistory" />
        <div class="mt-4 border-t border-gray-100 dark:border-gray-800 pt-4">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Записать вес</p>
          <div class="flex flex-col sm:flex-row gap-2">
            <input type="date" v-model="weightForm.date" class="input flex-1" />
            <input type="number" v-model.number="weightForm.kg" step="0.1" min="20" max="300" placeholder="кг" class="input sm:w-24" inputmode="decimal" />
            <BaseButton :disabled="!weightForm.kg" @click="logWeight" class="w-full sm:w-auto">Сохранить</BaseButton>
          </div>
        </div>
      </div>

      <!-- Goals -->
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 dark:text-white">Цели</h3>
          <BaseButton variant="outline" size="sm" @click="showAddGoal = true">Цель</BaseButton>
        </div>

        <div v-if="goals.length" class="space-y-1">
          <div v-for="goal in goals" :key="goal.id"
            class="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            <button
              :class="['w-7 h-7 rounded-full border-2 flex-shrink-0 transition-colors flex items-center justify-center text-xs font-bold',
                goal.done ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300 hover:border-green-400']"
              @click="toggleGoal(goal.id)"
            >{{ goal.done ? '✓' : '' }}</button>
            <div class="flex-1 min-w-0">
              <p :class="['text-sm font-medium leading-snug', goal.done ? 'line-through text-gray-400' : 'text-gray-900 dark:text-white']">
                {{ goal.text }}
              </p>
              <p class="text-xs text-gray-400">до {{ formatDate(goal.targetDate) }}</p>
            </div>
            <button class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0" @click="deleteGoal(goal.id)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <BaseEmptyState v-else icon="🎯" title="Нет целей" description="Поставьте себе цель!" />
      </div>
    </div>

    <!-- 1RM maxes -->
    <div class="card p-4">
      <div class="flex flex-wrap items-start justify-between gap-3 mb-3">
        <div class="min-w-0">
          <h3 class="font-semibold text-gray-900 dark:text-white">Личные максимумы (ПМ)</h3>
          <p class="text-xs text-gray-400 mt-0.5">Используются для расчёта % в тренировочных циклах</p>
        </div>
        <BaseButton variant="outline" size="sm" @click="showAddMax = true">Добавить</BaseButton>
      </div>

      <div v-if="maxes.length" class="space-y-1">
        <div v-for="max in maxes" :key="max.exercise_name" class="flex items-center gap-3 py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">{{ max.exercise_name }}</p>
            <p class="text-xs text-gray-400">обновлён {{ formatDate(max.recorded_at) }}</p>
          </div>
          <span class="text-lg font-bold text-primary flex-shrink-0">{{ max.weight_kg }} кг</span>
          <button class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors flex-shrink-0" @click="deleteMax(max.exercise_name)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      <BaseEmptyState v-else icon="🏋️" title="Нет ПМ" description="Укажите свои максимумы для расчёта циклов" />
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

    <!-- Add max modal -->
    <BaseModal v-model="showAddMax" title="Личный максимум (ПМ)">
      <div class="space-y-4">
        <div>
          <label class="label">Упражнение</label>
          <div class="flex flex-wrap gap-2 mb-2">
            <button
              v-for="ex in commonLifts"
              :key="ex"
              :class="['text-xs px-2.5 py-1 rounded-full border transition-colors',
                maxForm.exercise_name === ex ? 'bg-primary text-white border-primary' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-primary dark:hover:border-primary']"
              @click="maxForm.exercise_name = ex"
            >{{ ex }}</button>
          </div>
          <input v-model="maxForm.exercise_name" class="input" placeholder="или введите своё упражнение" />
        </div>
        <div>
          <label class="label">Максимальный вес (кг)</label>
          <StepperInput v-model="maxForm.weight_kg" :step="2.5" :min="0" placeholder="100" :decimals="1" />
        </div>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showAddMax = false">Отмена</BaseButton>
        <BaseButton :disabled="!maxForm.exercise_name || !maxForm.weight_kg" @click="saveMax">Сохранить</BaseButton>
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
import { useRouter } from 'vue-router'
import StatCard from '@/components/profile/StatCard.vue'
import WeightChart from '@/components/profile/WeightChart.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import StepperInput from '@/components/ui/StepperInput.vue'

const store = useStore()
const router = useRouter()

const userName = computed(() => store.getters['auth/userName'])

function logout() {
  store.dispatch('auth/logout')
  router.push('/login')
}

const profile = computed(() => store.state.user.profile)
const maxes = computed(() => store.state.user.maxes)

const commonLifts = ['Приседания со штангой', 'Жим лёжа', 'Становая тяга']

const showAddMax = ref(false)
const maxForm = reactive({ exercise_name: '', weight_kg: null })

async function saveMax() {
  await store.dispatch('user/saveUserMax', { exercise_name: maxForm.exercise_name, weight_kg: maxForm.weight_kg })
  store.dispatch('ui/showToast', { message: 'ПМ сохранён!', type: 'success' })
  maxForm.exercise_name = ''
  maxForm.weight_kg = null
  showAddMax.value = false
}

async function deleteMax(exerciseName) {
  await store.dispatch('user/deleteUserMax', exerciseName)
  store.dispatch('ui/showToast', { message: 'ПМ удалён', type: 'success' })
}
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
