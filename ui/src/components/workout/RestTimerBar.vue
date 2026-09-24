<template>
  <Transition name="timer-slide">
    <div
      v-if="active"
      class="fixed bottom-16 lg:bottom-4 left-0 right-0 z-40 flex justify-center px-4 pointer-events-none"
    >
      <div class="w-full max-w-sm pointer-events-auto">
        <div class="bg-ink/95 backdrop-blur-sm border-2 border-primary px-4 py-3">

          <!-- Top row: label + presets -->
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-display font-semibold uppercase tracking-wide text-steel-300">Отдых</span>
            <div class="flex gap-1">
              <button
                v-for="s in presets"
                :key="s"
                :class="['text-xs px-2 py-0.5 font-mono transition-colors',
                  total === s
                    ? 'bg-primary text-white'
                    : 'text-steel-300 hover:text-white hover:bg-white/10']"
                @click="start(s)"
              >{{ s >= 60 ? (s / 60) + 'мин' : s + 'с' }}</button>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="h-1.5 bg-white/10 mb-3 overflow-hidden">
            <div
              class="h-full bg-primary transition-all duration-1000 ease-linear"
              :style="{ width: (progress * 100) + '%' }"
            />
          </div>

          <!-- Main row: -15 | time | +15 | skip -->
          <div class="flex items-center gap-2">
            <button
              class="w-9 h-9 border-2 border-white/20 hover:border-white/40 text-white text-xs font-display font-bold transition-colors flex-shrink-0"
              @click="adjust(-15)"
            >−15</button>

            <div class="flex-1 text-center">
              <span class="text-3xl font-mono font-bold text-white tabular-nums">{{ formatted }}</span>
            </div>

            <button
              class="w-9 h-9 border-2 border-white/20 hover:border-white/40 text-white text-xs font-display font-bold transition-colors flex-shrink-0"
              @click="adjust(+15)"
            >+15</button>

            <button
              class="px-3 h-9 border-2 border-transparent hover:border-white/20 text-steel-300 hover:text-white text-xs font-medium transition-colors flex-shrink-0"
              @click="stop"
            >Пропустить</button>
          </div>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useRestTimer } from '@/composables/useRestTimer.js'

const { active, total, progress, formatted, start, stop, adjust } = useRestTimer()

const presets = [60, 90, 120, 180]
</script>

<style scoped>
.timer-slide-enter-active,
.timer-slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.timer-slide-enter-from,
.timer-slide-leave-to {
  transform: translateY(1rem);
  opacity: 0;
}
</style>
