<template>
  <div class="min-h-screen bg-surface">
    <AppSidebar />
    <AppTopbar />
    <main class="pt-16 lg:pl-64 pb-16 lg:pb-0">
      <div class="p-4 md:p-6 max-w-5xl mx-auto">
        <slot />
      </div>
    </main>
    <AppBottomNav />
    <ToastContainer />
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import AppBottomNav from './AppBottomNav.vue'
import ToastContainer from '@/components/ui/ToastContainer.vue'
</script>
