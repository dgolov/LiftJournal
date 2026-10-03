// Where clicking a notification takes you. A coach can't open an athlete's
// workout by its own /workouts/:id route, so athlete activity lands on the
// coach's read-only view of that workout instead.
export function notificationTarget(n, { coachLinks = [], myId = null } = {}) {
  switch (n.type) {
    case 'like':
    case 'comment':
      return n.workoutId ? `/workouts/${n.workoutId}` : null
    case 'follow':
    case 'coach_invite':
      return `/users/${n.actorId}`
    case 'coach_request':
      return '/coach'
    case 'coach_accepted': {
      const link = coachLinks.find(l => l.id === n.coachLinkId)
      return link && link.coachId === myId ? `/coach/athletes/${n.actorId}` : `/users/${n.actorId}`
    }
    case 'plan_assigned':
      return n.plannedWorkoutId ? `/planning/${n.plannedWorkoutId}` : '/planning'
    case 'athlete_completed':
      return n.workoutId
        ? `/coach/athletes/${n.actorId}/workouts/${n.workoutId}`
        : `/coach/athletes/${n.actorId}`
    default:
      return null
  }
}
