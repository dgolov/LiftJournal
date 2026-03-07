const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${method} ${path} → ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined
  return res.json()
}

const workoutService = {
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
      exercises: workout.exercises,
    })
  },

  updateWorkout(workout) {
    return request('PATCH', `/workouts/${workout.id}`, {
      date: workout.date,
      type: workout.type,
      title: workout.title,
      durationMinutes: workout.durationMinutes,
      notes: workout.notes,
      exercises: workout.exercises,
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
      age: profile.age,
      avatarUrl: profile.avatarUrl ?? null,
    })
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
}

export default workoutService
