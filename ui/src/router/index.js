import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/history' },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/HistoryView.vue')
  },
  {
    path: '/workouts/new',
    name: 'workout-create',
    component: () => import('@/views/WorkoutCreateView.vue')
  },
  {
    path: '/workouts/:id',
    name: 'workout-detail',
    component: () => import('@/views/WorkoutDetailView.vue')
  },
  {
    path: '/exercises',
    name: 'exercises',
    component: () => import('@/views/ExercisesView.vue')
  },
  {
    path: '/exercises/:id',
    name: 'exercise-detail',
    component: () => import('@/views/ExerciseDetailView.vue')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue')
  }
]

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})
