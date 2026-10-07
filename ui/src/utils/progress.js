import { sessionE1RM, sessionLoad, round1 } from '@/utils/strength.js'

const defaultLinkFor = (kind, id) => (kind === 'plan' ? `/planning/${id}` : `/workouts/${id}`)

// Per-session load series for one exercise, from whoever's data is passed in:
// the current user's store, or an athlete's history loaded by their coach.
// `source: 'plan'` builds the same series from planned workouts instead —
// what the plan asks for, measured against the 1RM known on that date.
// `linkFor(kind, id)` decides where a session row links to (null = nowhere).
export function computeProgress({
  exercise, exerciseId, workouts = [], planned = [], maxes = [],
  range = {}, source = 'fact', linkFor = defaultLinkFor,
}) {
  const isCardio = exercise?.muscleGroup === 'Кардио'
  // Relative intensity is measured against the best 1RM known *at that
  // session*: the profile max recorded on/before it, or the best estimate
  // from actual sessions up to then — so the baseline is walked over full
  // history and the period filter is applied only at the end.
  const declaredMax = exercise && maxes.find(m => m.exercise_name === exercise.name)
  const declaredOn = date => declaredMax && declaredMax.recorded_at.slice(0, 10) <= date ? declaredMax.weight_kg : 0
  const factSessions = [...workouts]
    .sort((a, b) => a.date.localeCompare(b.date))
    .map(w => ({ id: w.id, date: w.date, title: w.title, ex: w.exercises.find(e => e.exerciseId === exerciseId) }))
  const planSessions = planned
    .filter(p => p.status !== 'skipped')
    .sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
    .map(p => ({ id: p.id, date: p.scheduledDate, title: p.title, ex: p.exercises?.find(e => e.exerciseId === exerciseId) }))

  // Best actual e1RM per date, for plan baselines.
  const actualBest = []
  let running = 0
  factSessions.forEach(({ date, ex }) => {
    if (!ex) return
    running = Math.max(running, sessionE1RM(ex.sets.filter(s => !s.failed)))
    actualBest.push({ date, best: running })
  })
  const actualBestOn = date => {
    let best = 0
    for (const a of actualBest) { if (a.date > date) break; best = a.best }
    return best
  }

  const isPlan = source === 'plan'
  const sessions = []
  running = 0
  ;(isPlan ? planSessions : factSessions).forEach(({ id, date, title, ex }) => {
    if (!ex || !ex.sets?.length) return
    const sets = ex.sets.filter(s => !s.failed)
    if (!sets.length) return
    const setsCount = sets.length
    const totalSetsCount = ex.sets.length
    const base = {
      date, setsCount, totalSetsCount, workoutId: id, workoutTitle: title,
      link: linkFor(isPlan ? 'plan' : 'workout', id),
    }
    if (isCardio) {
      const totalMinutes = sets.reduce((sum, s) => sum + (s.reps || 0), 0)
      sessions.push({ ...base, totalMinutes })
      return
    }
    const bestSet = sets.reduce((a, b) => b.weight > a.weight ? b : a, sets[0])
    const e1RM = sessionE1RM(sets)
    let baseline1RM
    if (isPlan) {
      // Only fall back to the plan's own implied 1RM when nothing real is
      // known yet — otherwise a plan above the current max should read >100%.
      baseline1RM = Math.max(actualBestOn(date), declaredOn(date)) || e1RM
    } else {
      running = Math.max(running, e1RM)
      baseline1RM = Math.max(running, declaredOn(date))
    }
    const { lifts, tonnage, workingTonnage, avgWeight } = sessionLoad(sets, baseline1RM)
    sessions.push({
      ...base,
      maxWeight: bestSet.weight,
      maxWeightReps: bestSet.reps,
      maxReps: Math.max(...sets.map(s => s.reps)),
      totalVolume: tonnage,
      workingTonnage,
      lifts,
      best1RM: Math.round(e1RM),
      baseline1RM: Math.round(baseline1RM),
      avgWeight: round1(avgWeight),
      relIntensity: baseline1RM ? Math.round(avgWeight / baseline1RM * 100) : null,
      topSetIntensity: baseline1RM ? Math.round(bestSet.weight / baseline1RM * 100) : null,
    })
  })
  return sessions.filter(s => (!range.from || s.date >= range.from) && (!range.to || s.date <= range.to))
}

export function computePersonalRecord(progress, isCardio) {
  if (!progress.length) return null
  if (isCardio) {
    let bestDuration = 0, bestDurationDate = null
    progress.forEach(session => {
      if (session.totalMinutes > bestDuration) {
        bestDuration = session.totalMinutes
        bestDurationDate = session.date
      }
    })
    return { bestDuration, bestDurationDate }
  }
  let bestWeight = 0, bestWeightReps = 0, bestWeightDate = null
  let best1RM = 0, best1RMDate = null
  let bestVolume = 0, bestVolumeDate = null
  progress.forEach(session => {
    if (session.maxWeight > bestWeight) {
      bestWeight = session.maxWeight
      bestWeightReps = session.maxWeightReps
      bestWeightDate = session.date
    }
    if (session.best1RM > best1RM) {
      best1RM = session.best1RM
      best1RMDate = session.date
    }
    if (session.totalVolume > bestVolume) {
      bestVolume = session.totalVolume
      bestVolumeDate = session.date
    }
  })
  return { bestWeight, bestWeightReps, bestWeightDate, best1RM, best1RMDate, bestVolume, bestVolumeDate }
}

// Up to five most recent logged versions of an exercise (newest first), used
// to prefill sets when planning — "same as last time" and older alternatives.
export function exerciseHistoryOptions(workouts, exerciseId) {
  const sorted = [...workouts].sort((a, b) => b.date.localeCompare(a.date))
  const options = []
  for (const w of sorted) {
    const ex = w.exercises.find(e => e.exerciseId === exerciseId)
    const validSets = ex?.sets?.filter(s => !s.failed)
    if (validSets?.length) {
      options.push({ date: w.date, sets: validSets })
      if (options.length >= 5) break
    }
  }
  return options
}

// Planned workouts laid out from a cycle, grouped by layout ("прогон"):
// newest first, with how far along each one is.
export function cycleSchedules(planned) {
  const byId = {}
  planned.forEach(p => {
    if (!p.cycleScheduleId) return
    const s = (byId[p.cycleScheduleId] ||= {
      id: p.cycleScheduleId, cycleId: p.cycleId, title: p.cycleTitle || 'Цикл',
      createdByName: p.createdByName, plans: [],
    })
    s.plans.push(p)
  })
  return Object.values(byId)
    .map(s => {
      s.plans.sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
      return {
        ...s,
        from: s.plans[0].scheduledDate,
        to: s.plans[s.plans.length - 1].scheduledDate,
        total: s.plans.length,
        completed: s.plans.filter(p => p.status === 'completed').length,
        skipped: s.plans.filter(p => p.status === 'skipped').length,
        mainExercises: s.plans.find(p => p.cycleMainExercises?.length)?.cycleMainExercises || [],
      }
    })
    .sort((a, b) => b.from.localeCompare(a.from))
}
