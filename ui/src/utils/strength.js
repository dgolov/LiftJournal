// Strength-training load metrics for a single exercise session.
//
//   Volume              — КПШ (total lifts) and tonnage (Σ weight × reps)
//   Absolute intensity  — average weight per lift: tonnage / КПШ, kg
//   Relative intensity  — absolute intensity as % of the athlete's 1RM
//   Estimated 1RM       — Epley, weight × (1 + reps / 30), where reps are
//                         counted to failure: reps + reps-in-reserve (10 − RPE)
//                         when the set has an RPE logged.

// Epley overestimates badly past ~12 reps, so high-rep sets only feed the
// 1RM estimate when a session has nothing heavier to go on.
const MAX_RELIABLE_REPS = 12

export function estimate1RM(weight, reps, rpe = null) {
  if (!weight || !reps) return 0
  const rir = rpe != null ? Math.max(0, 10 - rpe) : 0
  const repsToFailure = reps + rir
  if (repsToFailure <= 1) return weight
  return weight * (1 + repsToFailure / 30)
}

export function sessionE1RM(sets) {
  const loaded = sets.filter(s => s.weight > 0 && s.reps > 0)
  const reliable = loaded.filter(s => s.reps <= MAX_RELIABLE_REPS)
  const pool = reliable.length ? reliable : loaded
  if (!pool.length) return 0
  return Math.max(...pool.map(s => estimate1RM(s.weight, s.reps, s.rpe)))
}

export function sessionLoad(sets) {
  const lifts = sets.reduce((sum, s) => sum + (s.reps || 0), 0)
  const tonnage = sets.reduce((sum, s) => sum + (s.weight || 0) * (s.reps || 0), 0)
  return {
    lifts,
    tonnage,
    avgWeight: lifts ? tonnage / lifts : 0,
  }
}

export function round1(x) {
  return Math.round(x * 10) / 10
}
