import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store/index.js'

const routes = [
  { path: '/', redirect: '/history' },
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
