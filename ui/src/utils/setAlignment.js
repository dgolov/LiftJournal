// How close to the lightest planned set a logged set must be to count as a
// working set rather than a warm-up: 92.5 against a planned 100 is a lighter
// working set (and shows as −7.5 кг), 80 is a warm-up.
const WARMUP_TOLERANCE = 0.9

// Line up logged sets against planned ones. Coaches often plan only the
// working sets ("100 × 5 × 5") and leave warm-ups to the athlete, so leading
// sets lighter than anything in the plan are split off as warm-ups instead of
// being matched against the first working sets — which would show every set
// after them as off-plan. Planned warm-ups need no special casing: they're
// the lightest planned sets, so the logged ones match them as usual.
//
// → { warmups: [factSet], rows: [{ n, plan, fact }] }
export function alignSets(planSets, factSets) {
  const plan = planSets || []
  const fact = factSets || []
  const plannedWeights = plan.map(s => s.weight || 0).filter(w => w > 0)

  let warmupCount = 0
  if (plan.length && plannedWeights.length) {
    const cutoff = Math.min(...plannedWeights) * WARMUP_TOLERANCE
    while (warmupCount < fact.length && (fact[warmupCount].weight || 0) < cutoff) warmupCount++
    // All light, nothing reached the plan: those were the working sets, just lighter.
    if (warmupCount === fact.length) warmupCount = 0
  }

  const working = fact.slice(warmupCount)
  const n = Math.max(plan.length, working.length)
  return {
    warmups: fact.slice(0, warmupCount),
    rows: Array.from({ length: n }, (_, i) => ({ n: i + 1, plan: plan[i] || null, fact: working[i] || null })),
  }
}

// Plan-vs-fact totals over what the plan actually covered: unplanned warm-ups
// and failed sets are left out of the fact so they don't read as overshoot.
export function comparableTotals(planSets, factSets) {
  const { rows } = alignSets(planSets, factSets)
  const sum = (sets, f) => sets.reduce((acc, s) => acc + f(s), 0)
  const planned = rows.map(r => r.plan).filter(Boolean)
  const done = rows.map(r => r.fact).filter(s => s && !s.failed)
  return {
    plan: { tonnage: sum(planned, s => s.weight * s.reps), reps: sum(planned, s => s.reps), sets: planned.length },
    fact: { tonnage: sum(done, s => s.weight * s.reps), reps: sum(done, s => s.reps), sets: done.length },
  }
}
