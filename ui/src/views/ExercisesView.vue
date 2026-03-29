<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Упражнения</h2>
      <BaseButton variant="outline" size="sm" @click="showAddModal = true">+ Своё упражнение</BaseButton>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-6">
      <div class="flex flex-col sm:flex-row flex-wrap gap-3">
        <input
          :value="filter.search"
          placeholder="Поиск..."
          class="input sm:flex-1"
          @input="setFilter('search', $event.target.value)"
        />
        <select :value="filter.muscleGroup || ''" class="input sm:w-44"
          @change="setFilter('muscleGroup', $event.target.value || null)">
          <option value="">Все группы мышц</option>
          <option v-for="g in muscleGroups" :key="g" :value="g">{{ g }}</option>
        </select>
        <select :value="filter.equipment || ''" class="input sm:w-36"
          @change="setFilter('equipment', $event.target.value || null)">
          <option value="">Всё оборудование</option>
          <option v-for="e in equipmentTypes" :key="e" :value="e">{{ e }}</option>
        </select>
        <button v-if="hasFilter" class="btn-ghost btn text-sm" @click="resetFilter">Сбросить</button>
      </div>
    </div>

    <!-- Grid -->
    <div v-if="exercises.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      <ExerciseCard v-for="ex in exercises" :key="ex.id" :exercise="ex" />
    </div>
    <BaseEmptyState v-else title="Ничего не найдено" description="Попробуйте изменить фильтры">
      <template #icon><Search class="w-12 h-12" /></template>
    </BaseEmptyState>

    <!-- Add custom exercise modal -->
    <BaseModal v-model="showAddModal" title="Добавить своё упражнение">
      <div class="space-y-4">
        <BaseInput v-model="newEx.name" label="Название" placeholder="Например: Болгарские сплит-приседания" />
        <BaseSelect v-model="newEx.muscleGroup" label="Группа мышц" :options="MUSCLE_GROUPS" placeholder="Выберите..." />
        <BaseSelect v-model="newEx.equipment" label="Оборудование" :options="EQUIPMENT_TYPES" placeholder="Выберите..." />
        <div>
          <label class="label">Описание</label>
          <textarea v-model="newEx.description" rows="2" class="input resize-none" placeholder="Как выполнять упражнение..." />
        </div>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showAddModal = false">Отмена</BaseButton>
        <BaseButton :disabled="!newEx.name || !newEx.muscleGroup" @click="addExercise">Добавить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Search } from 'lucide-vue-next'
import ExerciseCard from '@/components/exercises/ExerciseCard.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import { MUSCLE_GROUPS, EQUIPMENT_TYPES } from '@/services/mockData.js'

const store = useStore()
const showAddModal = ref(false)

onMounted(() => {
  if (!store.state.exercises.library.length) {
    store.dispatch('exercises/initExercises')
  }
})

const exercises = computed(() => store.getters['exercises/filteredExercises'])
const muscleGroups = computed(() => store.getters['exercises/muscleGroups'])
const equipmentTypes = computed(() => store.getters['exercises/equipmentTypes'])
const filter = computed(() => store.state.exercises.filter)
const hasFilter = computed(() => filter.value.search || filter.value.muscleGroup || filter.value.equipment)

const newEx = reactive({ name: '', muscleGroup: '', equipment: '', description: '' })

function setFilter(key, value) { store.commit('exercises/SET_FILTER', { key, value }) }
function resetFilter() { store.commit('exercises/RESET_FILTER') }

async function addExercise() {
  await store.dispatch('exercises/addCustomExercise', { ...newEx })
  store.dispatch('ui/showToast', { message: 'Упражнение добавлено!', type: 'success' })
  Object.assign(newEx, { name: '', muscleGroup: '', equipment: '', description: '' })
  showAddModal.value = false
}
</script>
