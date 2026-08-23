import { reactive } from 'vue'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const TOKEN_KEY = 'gym_admin_token'
const NAME_KEY = 'gym_admin_name'

export const authState = reactive({
  token: localStorage.getItem(TOKEN_KEY) || null,
  name: localStorage.getItem(NAME_KEY) || null,
})

function setAuth(token, name) {
  authState.token = token
  authState.name = name
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(NAME_KEY, name)
}

export function logout() {
  authState.token = null
  authState.name = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(NAME_KEY)
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
    setAuth(data.access_token, data.name)
    return data
  },

  fetchUsers() {
    return request('GET', '/admin/users')
  },

  fetchPendingExercises() {
    return request('GET', '/admin/exercises/pending')
  },

  approveExercise(id) {
    return request('POST', `/admin/exercises/${id}/approve`)
  },

  rejectExercise(id) {
    return request('DELETE', `/admin/exercises/${id}`)
  },
}

export default adminService
