// Planned load of a training cycle straight from its percentages — no 1RM
// or kilograms needed, so it can be charted while the cycle is being written.
// Sets under 50% of 1RM are warm-ups and don't count (same rule as КПШ and
// intensity everywhere else, see WORKING_SET_THRESHOLD).

export const ZONES = [
  { min: 50, max: 60, label: '50–60%' },
  { min: 60, max: 70, label: '60–70%' },
  { min: 70, max: 80, label: '70–80%' },
  { min: 80, max: 90, label: '80–90%' },
  { min: 90, max: Infinity, label: '90%+' },
]

function zoneIndex(percent) {
  return ZONES.findIndex(z => percent >= z.min && percent < z.max)
}

// workouts: [{ exercises: [{ exercise_name, sets: [{ percent_1rm, reps }] }] }]
// → one entry per cycle workout: null where the lift isn't trained that day.
export function planLoadFor(workouts, exerciseName) {
  return workouts.map((w, i) => {
    const ex = w.exercises.find(e => e.exercise_name === exerciseName)
    if (!ex || !ex.sets.length) return null
    const working = ex.sets.filter(s => Number(s.percent_1rm) >= 50)
    const lifts = working.reduce((sum, s) => sum + (Number(s.reps) || 0), 0)
    const percentReps = working.reduce((sum, s) => sum + Number(s.percent_1rm) * (Number(s.reps) || 0), 0)
    const zones = ZONES.map(() => 0)
    working.forEach(s => { zones[zoneIndex(Number(s.percent_1rm))] += Number(s.reps) || 0 })
    return {
      n: i + 1,
      lifts,
      avgPercent: lifts ? Math.round(percentReps / lifts * 10) / 10 : null,
      topPercent: working.length ? Math.max(...working.map(s => Number(s.percent_1rm))) : null,
      zones,
    }
  })
}

// Whole-cycle totals for one lift: lift-weighted average intensity and the
// share of lifts in each zone.
export function planSummary(points) {
  const done = points.filter(Boolean)
  const lifts = done.reduce((s, p) => s + p.lifts, 0)
  const zones = ZONES.map((_, zi) => done.reduce((s, p) => s + p.zones[zi], 0))
  const avg = lifts ? done.reduce((s, p) => s + (p.avgPercent || 0) * p.lifts, 0) / lifts : null
  return {
    sessions: done.length,
    lifts,
    avgPercent: avg != null ? Math.round(avg) : null,
    zoneShare: zones.map(z => (lifts ? Math.round(z / lifts * 100) : 0)),
  }
}
