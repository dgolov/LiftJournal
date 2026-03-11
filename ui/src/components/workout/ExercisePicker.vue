<template>
  <BaseModal v-model="show" title="Добавить упражнение" max-width="xl">
    <!-- Search -->
    <div class="flex flex-col sm:flex-row gap-2 mb-3">
      <input
        v-model="search"
        placeholder="Поиск упражнения..."
        class="input flex-1"
      />
      <select v-model="selectedGroup" class="input sm:w-40">
        <option value="">Все группы</option>
        <option v-for="g in muscleGroups" :key="g" :value="g">{{ g }}</option>
      </select>
    </div>

    <!-- List -->
    <div class="space-y-1 max-h-[50vh] overflow-y-auto -mx-2 px-2">
      <button
        v-for="ex in filtered"
        :key="ex.id"
        :class="['w-full text-left px-3 py-2 rounded-xl hover:bg-gray-50 transition-colors flex items-center gap-3',
          isAdded(ex.id) ? 'opacity-50 cursor-not-allowed' : '']"
        :disabled="isAdded(ex.id)"
        @click="pick(ex)"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900">{{ ex.name }}</p>
          <p class="text-xs text-gray-400">{{ ex.muscleGroup }} · {{ ex.equipment }}</p>
        </div>
        <span v-if="isAdded(ex.id)" class="text-xs text-green-500 font-medium flex-shrink-0">Добавлено</span>
      </button>
      <div v-if="!filtered.length" class="text-center py-8 text-gray-400 text-sm">
        Ничего не найдено
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import BaseModal from '@/components/ui/BaseModal.vue'

const props = defineProps({
  modelValue: Boolean
})
const emit = defineEmits(['update:modelValue'])

const store = useStore()
const search = ref('')
const selectedGroup = ref('')

const show = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const allExercises = computed(() => store.getters['exercises/allExercises'])
const muscleGroups = computed(() => store.getters['exercises/muscleGroups'])
const addedIds = computed(() =>
  new Set(store.state.workouts.activeWorkout.exercises.map(e => e.exerciseId))
)

const filtered = computed(() => {
  let list = allExercises.value
  if (selectedGroup.value) list = list.filter(e => e.muscleGroup === selectedGroup.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.name.toLowerCase().includes(q))
  }
  return list
})

function isAdded(id) { return addedIds.value.has(id) }

function pick(exercise) {
  if (isAdded(exercise.id)) return
  store.commit('workouts/ADD_EXERCISE_TO_ACTIVE', exercise)
}
</script>
