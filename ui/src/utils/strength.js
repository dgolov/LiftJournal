// Strength-training load metrics for a single exercise session.
//
//   Volume              — tonnage (Σ weight × reps, all sets) and КПШ
//                         (lifts in working sets, ≥ 50% of 1RM)
//   Absolute intensity  — average weight per working lift, kg
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

// Warm-up sets below this share of 1RM count toward tonnage but not toward
// КПШ or intensity (the usual Medvedev/Sheiko convention), otherwise a few
// light warm-up reps drag the average bar weight far below the working sets.
export const WORKING_SET_THRESHOLD = 0.5

// `baseline1RM` decides which sets are working sets; without one (no loaded
// sets yet, bodyweight work) every set counts.
export function sessionLoad(sets, baseline1RM = 0) {
  const tonnageOf = list => list.reduce((sum, s) => sum + (s.weight || 0) * (s.reps || 0), 0)
  const minWeight = baseline1RM * WORKING_SET_THRESHOLD
  const working = baseline1RM ? sets.filter(s => (s.weight || 0) >= minWeight) : sets
  const lifts = working.reduce((sum, s) => sum + (s.reps || 0), 0)
  const workingTonnage = tonnageOf(working)
  return {
    tonnage: tonnageOf(sets),
    workingTonnage,
    lifts,
    avgWeight: lifts ? workingTonnage / lifts : 0,
  }
}

export function round1(x) {
  return Math.round(x * 10) / 10
}
