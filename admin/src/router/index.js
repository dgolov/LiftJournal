import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '@/services/adminService.js'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('@/views/UsersView.vue'),
  },
  {
    path: '/exercises',
    name: 'exercises',
    component: () => import('@/views/ExercisesView.vue'),
  },
  {
    path: '/cycles',
    name: 'cycles',
    component: () => import('@/views/CyclesView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!authState.token
  if (!to.meta.public && !isAuthenticated) next({ name: 'login' })
  else if (to.meta.public && isAuthenticated) next({ name: 'dashboard' })
  else next()
})

export default router
