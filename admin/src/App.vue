<template>
  <RouterView v-if="isPublicRoute" />
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const isPublicRoute = computed(() => !!route.meta.public)
</script>
