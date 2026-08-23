import { reactive } from 'vue'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const TOKEN_KEY = 'gym_admin_token'
const NAME_KEY = 'gym_admin_name'
const USER_ID_KEY = 'gym_admin_user_id'

export const authState = reactive({
  token: localStorage.getItem(TOKEN_KEY) || null,
  name: localStorage.getItem(NAME_KEY) || null,
  userId: localStorage.getItem(USER_ID_KEY) ? Number(localStorage.getItem(USER_ID_KEY)) : null,
})

function setAuth(token, name, userId) {
  authState.token = token
  authState.name = name
  authState.userId = userId
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(NAME_KEY, name)
  localStorage.setItem(USER_ID_KEY, String(userId))
}

export function logout() {
  authState.token = null
  authState.name = null
  authState.userId = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(NAME_KEY)
  localStorage.removeItem(USER_ID_KEY)
}

async function parseErrorMessage(res) {
  const text = await res.text()
  try {
    const data = JSON.parse(text)
    if (typeof data.detail === 'string') return data.detail
  } catch {
    // not JSON — fall through to raw text
  }
  return text || `Ошибка запроса (${res.status})`
}

async function request(method, path, body) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  if (authState.token) headers['Authorization'] = `Bearer ${authState.token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  // A 401 on the login call itself means "wrong credentials", not "session
  // expired" — there's no session yet, so it must not trigger a logout/redirect.
  if (res.status === 401 && path !== '/auth/login') {
    logout()
    throw new Error('Сессия истекла, войдите снова')
  }
  if (res.status === 404 && path.startsWith('/admin')) {
    throw new Error('Доступ запрещён — аккаунт не является администратором')
  }
  if (!res.ok) {
    throw new Error(await parseErrorMessage(res))
  }
  if (res.status === 204) return undefined
  return res.json()
}

const adminService = {
  async login(email, password) {
    const data = await request('POST', '/auth/login', { email, password })
    if (!data.isAdmin) {
      throw new Error('Этот аккаунт не является администратором')
    }
    setAuth(data.access_token, data.name, data.user_id)
    return data
  },

  fetchUsers() {
    return request('GET', '/admin/users')
  },

  setUserAdmin(id, isAdmin) {
    return request('PATCH', `/admin/users/${id}`, { isAdmin })
  },

  fetchExercises({ status = 'pending', search = '', muscleGroup = '' } = {}) {
    const params = new URLSearchParams({ status })
    if (search) params.set('search', search)
    if (muscleGroup) params.set('muscleGroup', muscleGroup)
    return request('GET', `/admin/exercises?${params.toString()}`)
  },

  approveExercise(id) {
    return request('POST', `/admin/exercises/${id}/approve`)
  },

  revokeExercise(id) {
    return request('POST', `/admin/exercises/${id}/revoke`)
  },

  renameExercise(id, name) {
    return request('PATCH', `/admin/exercises/${id}`, { name })
  },

  rejectExercise(id) {
    return request('DELETE', `/admin/exercises/${id}`)
  },

  fetchCycles(status = 'pending') {
    return request('GET', `/admin/cycles?status=${status}`)
  },

  approveCycle(id) {
    return request('POST', `/admin/cycles/${id}/approve`)
  },

  revokeCycle(id) {
    return request('POST', `/admin/cycles/${id}/revoke`)
  },

  rejectCycle(id) {
    return request('DELETE', `/admin/cycles/${id}`)
  },

  fetchStats() {
    return request('GET', '/admin/stats')
  },
}

export default adminService
