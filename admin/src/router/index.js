import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '@/services/adminService.js'

const routes = [
  { path: '/', redirect: '/users' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!authState.token
  if (!to.meta.public && !isAuthenticated) next({ name: 'login' })
  else if (to.meta.public && isAuthenticated) next({ name: 'users' })
  else next()
})

export default router
