function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}

function escapeCSV(val) {
  const str = val == null ? '' : String(val)
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

export function exportCSV(workouts) {
  const rows = [
    ['Дата', 'Название', 'Тип', 'Длительность (мин)', 'Тоннаж (кг)', 'Упражнение', 'Подход', 'Вес (кг)', 'Повторения', 'Статус'],
  ]

  for (const w of workouts) {
    if (!w.exercises.length) {
      rows.push([w.date, w.title, w.type, w.durationMinutes || 0, '', '', '', '', '', ''])
      continue
    }
    for (const ex of w.exercises) {
      if (!ex.sets.length) {
        rows.push([w.date, w.title, w.type, w.durationMinutes || 0, '', ex.exerciseName || '', '', '', '', ''])
        continue
      }
      ex.sets.forEach((set, i) => {
        rows.push([
          w.date,
          w.title,
          w.type,
          w.durationMinutes || 0,
          '',
          ex.exerciseName || '',
          i + 1,
          set.weight,
          set.reps,
          set.failed ? 'провал' : 'выполнен',
        ])
      })
    }
  }

  const csv = rows.map(r => r.map(escapeCSV).join(',')).join('\n')
  const bom = '﻿'
  const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `gym_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export function exportPDF(workouts) {
  const rows = workouts.map(w => {
    const volume = w.exercises.reduce((s, ex) =>
      s + ex.sets.reduce((ss, set) => ss + (set.failed ? 0 : set.weight * set.reps), 0), 0)

    const exerciseRows = w.exercises.map(ex => {
      const sets = ex.sets.map((set, i) =>
        `<tr>
          <td></td>
          <td class="ex-name">${ex.exerciseName || ''}</td>
          <td class="center">${i + 1}</td>
          <td class="center">${set.weight} кг</td>
          <td class="center">${set.reps}</td>
          <td class="center ${set.failed ? 'failed' : 'ok'}">${set.failed ? '✗' : '✓'}</td>
        </tr>`
      ).join('')
      return sets
    }).join('')

    return `
      <tr class="workout-header">
        <td colspan="6">
          <strong>${formatDate(w.date)}</strong> — ${w.title}
          <span class="badge">${w.type}</span>
          ${w.durationMinutes ? `<span class="meta">${w.durationMinutes} мин</span>` : ''}
          ${volume ? `<span class="meta">${volume >= 1000 ? (volume / 1000).toFixed(1) + ' т' : volume + ' кг'}</span>` : ''}
          ${w.notes ? `<div class="notes">${w.notes}</div>` : ''}
        </td>
      </tr>
      ${exerciseRows}
    `
  }).join('')

  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Gym — История тренировок</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; color: #111; padding: 24px; }
    h1 { font-size: 20px; margin-bottom: 4px; }
    .subtitle { color: #666; font-size: 12px; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #f3f4f6; text-align: left; padding: 6px 8px; font-size: 11px; font-weight: 600; color: #555; border-bottom: 1px solid #e5e7eb; }
    td { padding: 5px 8px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }
    .center { text-align: center; }
    .workout-header td { background: #eef2ff; font-size: 13px; padding: 8px 10px; border-top: 2px solid #6366f1; border-bottom: 1px solid #c7d2fe; }
    .badge { display: inline-block; background: #6366f1; color: #fff; border-radius: 4px; padding: 1px 6px; font-size: 10px; margin-left: 8px; vertical-align: middle; }
    .meta { color: #666; font-size: 11px; margin-left: 10px; }
    .notes { font-size: 11px; color: #555; margin-top: 4px; font-style: italic; }
    .ex-name { color: #374151; }
    .ok { color: #16a34a; font-weight: bold; }
    .failed { color: #dc2626; font-weight: bold; }
    @media print {
      body { padding: 0; }
      @page { margin: 16mm; }
    }
  </style>
</head>
<body>
  <h1>Gym — История тренировок</h1>
  <p class="subtitle">Экспорт от ${new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })} · ${workouts.length} тренировок</p>
  <table>
    <thead>
      <tr>
        <th style="width:28px">#</th>
        <th>Упражнение</th>
        <th class="center" style="width:52px">Подход</th>
        <th class="center" style="width:64px">Вес</th>
        <th class="center" style="width:52px">Повт.</th>
        <th class="center" style="width:44px">Статус</th>
      </tr>
    </thead>
    <tbody>
      ${rows}
    </tbody>
  </table>
</body>
</html>`

  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(html)
  win.document.close()
  win.focus()
  setTimeout(() => win.print(), 400)
}
