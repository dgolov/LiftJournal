<template>
  <BaseModal :model-value="modelValue" :title="lockPeriod ? 'Экспорт тренировки' : 'Экспорт истории'" max-width="sm" @update:model-value="$emit('update:modelValue', $event)">
    <div class="space-y-5">

      <!-- Format -->
      <div>
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Формат</p>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="fmt in formats" :key="fmt.id"
            :class="['flex items-center gap-2.5 px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium',
              format === fmt.id
                ? 'border-primary bg-primary/5 text-primary'
                : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600']"
            @click="format = fmt.id"
          >
            <component :is="fmt.icon" :class="['w-4 h-4', fmt.color]" />
            {{ fmt.label }}
          </button>
        </div>
      </div>

      <!-- Single workout info -->
      <div v-if="lockPeriod && workouts.length" class="rounded-xl bg-gray-50 dark:bg-gray-800/60 px-4 py-3">
        <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{{ workouts[0].title }}</p>
        <p class="text-xs text-gray-400 mt-0.5">{{ formattedSingleDate }} · {{ workouts[0].exercises.length }} упр.</p>
      </div>

      <!-- Period selection -->
      <template v-if="!lockPeriod">
        <div>
          <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Период</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="p in presets" :key="p.id"
              :class="['text-sm px-3 py-1.5 rounded-full border transition-colors font-medium',
                preset === p.id
                  ? 'bg-primary text-white border-primary'
                  : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary']"
              @click="applyPreset(p.id)"
            >{{ p.label }}</button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label">С</label>
            <input type="date" v-model="dateFrom" class="input" @change="preset = 'custom'" />
          </div>
          <div>
            <label class="label">По</label>
            <input type="date" v-model="dateTo" class="input" @change="preset = 'custom'" />
          </div>
        </div>

        <p class="text-sm text-gray-400 text-center">
          <span class="font-semibold text-gray-700 dark:text-gray-200">{{ count }}</span> тренировок в выбранном периоде
        </p>
      </template>

    </div>

    <template #footer>
      <button class="btn" @click="$emit('update:modelValue', false)">Отмена</button>
      <button class="btn btn-primary" :disabled="count === 0" @click="doExport">
        Скачать {{ format.toUpperCase() }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { FileSpreadsheet, FileText } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import { exportCSV, exportPDF } from '@/services/exportService.js'

const store = useStore()

const props = defineProps({
  modelValue: Boolean,
  workouts: { type: Array, default: () => [] },
  initialFormat: { type: String, default: 'csv' },
  lockPeriod: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const formats = [
  { id: 'csv', label: 'CSV', icon: FileSpreadsheet, color: 'text-green-500' },
  { id: 'pdf', label: 'PDF', icon: FileText, color: 'text-red-500' },
]

const format = ref(props.initialFormat)
const preset = ref('month')
const dateFrom = ref('')
const dateTo = ref('')

function isoDate(d) {
  return d.toISOString().split('T')[0]
}

function applyPreset(id) {
  preset.value = id
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()

  if (id === 'all') { dateFrom.value = ''; dateTo.value = '' }
  else if (id === 'month') {
    dateFrom.value = isoDate(new Date(y, m, 1))
    dateTo.value = isoDate(new Date(y, m + 1, 0))
  } else if (id === 'prev_month') {
    dateFrom.value = isoDate(new Date(y, m - 1, 1))
    dateTo.value = isoDate(new Date(y, m, 0))
  } else if (id === '3months') {
    dateFrom.value = isoDate(new Date(y, m - 2, 1))
    dateTo.value = isoDate(new Date(y, m + 1, 0))
  } else if (id === 'year') {
    dateFrom.value = isoDate(new Date(y, 0, 1))
    dateTo.value = isoDate(new Date(y, 11, 31))
  }
}

const presets = [
  { id: 'all', label: 'Всё время' },
  { id: 'month', label: 'Этот месяц' },
  { id: 'prev_month', label: 'Прошлый месяц' },
  { id: '3months', label: '3 месяца' },
  { id: 'year', label: 'Этот год' },
  { id: 'custom', label: 'Свой диапазон' },
]

const filtered = computed(() => {
  if (props.lockPeriod) return props.workouts
  let list = props.workouts
  if (dateFrom.value) list = list.filter(w => w.date >= dateFrom.value)
  if (dateTo.value) list = list.filter(w => w.date <= dateTo.value)
  return list
})

const count = computed(() => filtered.value.length)

const formattedSingleDate = computed(() => {
  const w = props.workouts[0]
  if (!w) return ''
  return new Date(w.date + 'T00:00:00').toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
})

function doExport() {
  if (format.value === 'csv') {
    exportCSV(filtered.value)
  } else {
    exportPDF(filtered.value).catch(() => {
      store.dispatch('ui/showToast', { message: 'Не удалось создать PDF', type: 'error' })
    })
  }
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (open) => {
  if (open) {
    format.value = props.initialFormat
    if (!props.lockPeriod) applyPreset('month')
  }
})
</script>
