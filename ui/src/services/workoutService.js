const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function serializeExercises(exercises) {
  return (exercises || []).map(ex => ({
    exerciseId: ex.exerciseId,
    exerciseName: ex.exerciseName,
    sets: (ex.sets || []).map(s => ({
      id: s.id,
      weight: s.weight ?? 0,
      reps: s.reps ?? 0,
      completed: s.completed ?? false,
      failed: s.failed ?? false,
    })),
  }))
}
const TOKEN_KEY = 'gym_auth_token'

async function request(method, path, body, requiresAuth = true) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  if (requiresAuth) {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY)
    window.location.href = '/login'
    return
  }
  if (!res.ok) {
    const text = await res.text()
    console.error(`API error ${method} ${path} → ${res.status}:`, text)
    throw new Error(`${method} ${path} → ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined
  return res.json()
}

const workoutService = {
  // Auth
  login(credentials) {
    return request('POST', '/auth/login', credentials, false)
  },
  register(data) {
    return request('POST', '/auth/register', data, false)
  },

  // Workouts
  fetchWorkouts() {
    return request('GET', '/workouts')
  },

  saveWorkout(workout) {
    return request('POST', '/workouts', {
      date: workout.date,
      type: workout.type,
      title: workout.title,
      durationMinutes: workout.durationMinutes,
      notes: workout.notes,
      exercises: serializeExercises(workout.exercises),
    })
  },

  updateWorkout(workout) {
    return request('PATCH', `/workouts/${workout.id}`, {
      date: workout.date,
      type: workout.type,
      title: workout.title,
      durationMinutes: workout.durationMinutes,
      notes: workout.notes,
      exercises: serializeExercises(workout.exercises),
    })
  },

  deleteWorkout(id) {
    return request('DELETE', `/workouts/${id}`)
  },

  // Exercises
  fetchExercises() {
    return request('GET', '/exercises')
  },

  addCustomExercise(exercise) {
    return request('POST', '/exercises', {
      name: exercise.name,
      muscleGroup: exercise.muscleGroup,
      secondaryMuscles: exercise.secondaryMuscles || [],
      equipment: exercise.equipment,
      description: exercise.description || '',
    })
  },

  // User
  fetchUser() {
    return request('GET', '/user')
  },

  updateProfile(profile) {
    return request('PATCH', '/user/profile', {
      name: profile.name,
      birthDate: profile.birthDate ?? null,
      avatarUrl: profile.avatarUrl ?? null,
    })
  },

  updateTheme(theme) {
    return request('PATCH', '/user/theme', { theme })
  },

  logWeight(entry) {
    return request('POST', '/user/weight', { date: entry.date, kg: entry.kg })
  },

  deleteWeightEntry(date) {
    return request('DELETE', `/user/weight/${date}`)
  },

  saveGoal(goal) {
    return request('POST', '/user/goals', {
      text: goal.text,
      targetDate: goal.targetDate ?? null,
      done: goal.done ?? false,
    })
  },

  toggleGoal(id) {
    return request('PATCH', `/user/goals/${id}/toggle`)
  },

  deleteGoal(id) {
    return request('DELETE', `/user/goals/${id}`)
  },

  // User maxes (1RM)
  saveUserMax(data) {
    return request('POST', '/user/maxes', data)
  },
  deleteUserMax(exerciseName) {
    return request('DELETE', `/user/maxes/${encodeURIComponent(exerciseName)}`)
  },

  // Training cycles
  fetchCycles() {
    return request('GET', '/cycles')
  },
  fetchCycle(id) {
    return request('GET', `/cycles/${id}`)
  },
  createCycle(data) {
    return request('POST', '/cycles', data)
  },
  updateCycle(id, data) {
    return request('PATCH', `/cycles/${id}`, data)
  },
  deleteCycle(id) {
    return request('DELETE', `/cycles/${id}`)
  },

  // Cycle runs
  fetchCycleRun(cycleId) {
    return request('GET', `/cycles/${cycleId}/run`)
  },
  startCycleRun(cycleId) {
    return request('POST', `/cycles/${cycleId}/start`)
  },
  startCycleWorkout(runId, cycleWorkoutId, notes = '') {
    return request('POST', `/cycle-runs/${runId}/workouts/${cycleWorkoutId}/start`, { notes })
  },
  completeCycleWorkout(runId, cycleWorkoutId, workoutId = null) {
    return request('POST', `/cycle-runs/${runId}/workouts/${cycleWorkoutId}/complete`, { workout_id: workoutId })
  },
  finishCycleRun(runId) {
    return request('POST', `/cycle-runs/${runId}/finish`)
  },

  // Planned workouts
  fetchPlannedWorkouts() {
    return request('GET', '/planned-workouts')
  },
  createPlannedWorkout(data) {
    return request('POST', '/planned-workouts', data)
  },
  updatePlannedWorkout(id, data) {
    return request('PATCH', `/planned-workouts/${id}`, data)
  },
  deletePlannedWorkout(id) {
    return request('DELETE', `/planned-workouts/${id}`)
  },

  // Achievements
  fetchAchievements() {
    return request('GET', '/achievements')
  },
  evaluateAchievements() {
    return request('POST', '/achievements/evaluate')
  },
}

export default workoutService
