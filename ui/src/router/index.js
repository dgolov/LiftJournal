import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store/index.js'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { public: true }
  },
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
  },
  {
    path: '/cycles',
    name: 'cycles',
    component: () => import('@/views/CyclesView.vue')
  },
  {
    path: '/cycles/new',
    name: 'cycle-create',
    component: () => import('@/views/CycleEditView.vue')
  },
  {
    path: '/cycles/:id',
    name: 'cycle-detail',
    component: () => import('@/views/CycleDetailView.vue')
  },
  {
    path: '/cycles/:id/edit',
    name: 'cycle-edit',
    component: () => import('@/views/CycleEditView.vue')
  },
  {
    path: '/cycle-runs/:runId/workouts/:cycleWorkoutId',
    name: 'cycle-workout-execute',
    component: () => import('@/views/CycleWorkoutExecuteView.vue')
  },
  {
    path: '/planning',
    name: 'planning',
    component: () => import('@/views/PlanningView.vue')
  },
  {
    path: '/planning/new',
    name: 'plan-create',
    component: () => import('@/views/PlanWorkoutView.vue')
  },
  {
    path: '/planning/:id/edit',
    name: 'plan-edit',
    component: () => import('@/views/PlanWorkoutView.vue')
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, _from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  if (!to.meta.public && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.public && isAuthenticated) {
    next({ name: 'history' })
  } else {
    next()
  }
})

export default router
