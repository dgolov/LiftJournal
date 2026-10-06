<template>
  <div class="space-y-4">
    <!-- Like -->
    <div class="flex items-center gap-4">
      <button
        class="flex items-center gap-2 px-4 py-2 rounded-xl border transition-colors text-sm font-medium"
        :class="isLiked
          ? 'border-red-300 text-red-500 bg-red-50 dark:bg-red-950/30 dark:border-red-800'
          : 'border-gray-200 dark:border-gray-700 text-gray-500 hover:border-red-300 hover:text-red-400'"
        :aria-pressed="isLiked"
        :disabled="liking"
        @click="toggleLike"
      >
        <Heart :class="['w-4 h-4 transition-all', isLiked ? 'fill-current scale-110' : '']" />
        <span>{{ likesCount }}</span>
      </button>
    </div>

    <!-- Comments -->
    <div class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-800 font-semibold text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <MessageCircle class="w-4 h-4" />
        Комментарии
        <span class="text-gray-400 font-normal">({{ comments.length }})</span>
      </div>

      <div v-if="commentsLoading" class="p-4 text-center text-sm text-gray-400">Загрузка…</div>
      <div v-else-if="!comments.length" class="p-4 text-center text-sm text-gray-400">Пока нет комментариев</div>
      <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
        <div v-for="c in comments" :key="c.id" class="flex items-start gap-3 px-4 py-3">
          <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs flex-shrink-0">
            {{ c.userName.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2 flex-wrap">
              <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ c.userName }}</span>
              <span v-if="coachIds.includes(c.userId)" class="text-xs rounded-full bg-primary/10 text-primary px-2 py-0.5 font-medium">тренер</span>
              <span class="text-xs text-gray-400">{{ formatCommentDate(c.createdAt) }}</span>
            </div>
            <p class="text-sm text-gray-700 dark:text-gray-300 mt-0.5 break-words whitespace-pre-line">{{ c.text }}</p>
          </div>
          <button
            v-if="c.isOwn"
            class="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 mt-0.5"
            aria-label="Удалить комментарий"
            @click="deleteComment(c.id)"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div class="px-4 py-3 border-t border-gray-100 dark:border-gray-800 flex gap-2">
        <input
          v-model="newComment"
          class="input flex-1 text-sm"
          :placeholder="placeholder"
          @keydown.enter.prevent="submitComment"
        />
        <button
          class="btn btn-primary text-sm px-3 py-1.5"
          :disabled="!newComment.trim() || submitting"
          aria-label="Отправить комментарий"
          @click="submitComment"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { Heart, MessageCircle, Send, Trash2 } from 'lucide-vue-next'
import workoutService, { apiErrorMessage } from '@/services/workoutService.js'

const props = defineProps({
  workoutId: { type: String, required: true },
  // User ids to mark as "тренер" next to their comments.
  coachIds: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Написать комментарий…' },
})

const store = useStore()

const isLiked = ref(false)
const likesCount = ref(0)
const liking = ref(false)
const commentsLoading = ref(false)
const comments = computed(() => store.state.social.comments[props.workoutId] || [])
const newComment = ref('')
const submitting = ref(false)

function toastError(e) {
  store.dispatch('ui/showToast', { message: apiErrorMessage(e), type: 'error' })
}

async function load() {
  commentsLoading.value = true
  try {
    const [meta] = await workoutService.fetchWorkoutsMeta([props.workoutId])
    if (meta) {
      isLiked.value = meta.isLiked
      likesCount.value = meta.likesCount
    }
    await store.dispatch('social/fetchComments', props.workoutId)
  } catch { /* no access — panel stays empty */ } finally {
    commentsLoading.value = false
  }
}
onMounted(load)
watch(() => props.workoutId, load)

async function toggleLike() {
  liking.value = true
  try {
    const status = await store.dispatch('social/toggleLike', props.workoutId)
    isLiked.value = status.isLiked
    likesCount.value = status.likesCount
  } catch (e) {
    toastError(e)
  } finally {
    liking.value = false
  }
}

async function submitComment() {
  const text = newComment.value.trim()
  if (!text || submitting.value) return
  submitting.value = true
  try {
    await store.dispatch('social/addComment', { workoutId: props.workoutId, text })
    newComment.value = ''
  } catch (e) {
    toastError(e)
  } finally {
    submitting.value = false
  }
}

async function deleteComment(commentId) {
  try {
    await store.dispatch('social/deleteComment', { workoutId: props.workoutId, commentId })
  } catch (e) {
    toastError(e)
  }
}

function formatCommentDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>
