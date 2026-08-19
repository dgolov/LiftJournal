import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}

function workoutVolume(w) {
  return w.exercises.reduce((s, ex) =>
    s + ex.sets.reduce((ss, set) => ss + (set.failed ? 0 : set.weight * set.reps), 0), 0)
}

function escapeCSV(val) {
  const str = val == null ? '' : String(val)
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

function exportFilename(workouts, ext) {
  if (workouts.length === 1) return `gym_${workouts[0].date}.${ext}`
  return `gym_${new Date().toISOString().split('T')[0]}.${ext}`
}

// The badge is a small inline SVG so its own label is centered by the browser's
// native SVG engine (text-anchor/dominant-baseline), not html2canvas's approximate
// text layout. It's floated into the corner rather than inlined next to text —
// floats don't need any vertical-centering computation, sidestepping the whole
// class of misalignment html2canvas produces for vertical-align/flex/line-height.
const BADGE_HEIGHT = 26

function badgeSvg(text) {
  const height = BADGE_HEIGHT
  const width = Math.max(56, Math.round(text.length * 7.5) + 24)
  return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="float:right;">
    <rect width="${width}" height="${height}" rx="${height / 2}" fill="#6366f1" />
    <text x="${width / 2}" y="${height / 2}" text-anchor="middle" dominant-baseline="central" fill="#ffffff" font-size="12" font-weight="600" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">${text}</text>
  </svg>`
}

export function exportCSV(workouts) {
  const rows = [
    ['Дата', 'Название', 'Тип', 'Длительность (мин)', 'Тоннаж (кг)', 'Упражнение', 'Подход', 'Вес (кг)', 'Повторения', 'Статус'],
  ]

  for (const w of workouts) {
    const volume = workoutVolume(w)
    if (!w.exercises.length) {
      rows.push([w.date, w.title, w.type, w.durationMinutes || 0, volume, '', '', '', '', ''])
      continue
    }
    for (const ex of w.exercises) {
      if (!ex.sets.length) {
        rows.push([w.date, w.title, w.type, w.durationMinutes || 0, volume, ex.exerciseName || '', '', '', '', ''])
        continue
      }
      ex.sets.forEach((set, i) => {
        rows.push([
          w.date,
          w.title,
          w.type,
          w.durationMinutes || 0,
          volume,
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
  a.download = exportFilename(workouts, 'csv')
  a.click()
  URL.revokeObjectURL(url)
}

function buildReportHtml(workouts) {
  const workoutTables = workouts.map(w => {
    const volume = workoutVolume(w)

    const exerciseRows = w.exercises.map(ex => {
      return ex.sets.map((set, i) =>
        `<tr>
          <td></td>
          <td class="ex-name">${ex.exerciseName || ''}</td>
          <td class="center">${i + 1}</td>
          <td class="center">${set.weight} кг</td>
          <td class="center">${set.reps}</td>
          <td class="center ${set.failed ? 'failed' : 'ok'}">${set.failed ? '✗' : '✓'}</td>
        </tr>`
      ).join('')
    }).join('')

    const metaParts = [formatDate(w.date)]
    if (w.durationMinutes) metaParts.push(`${w.durationMinutes} мин`)
    if (volume) metaParts.push(volume >= 1000 ? (volume / 1000).toFixed(1) + ' т' : volume + ' кг')

    return `
      <table class="workout-table">
        <thead>
          <tr class="workout-header">
            <td colspan="6">
              ${badgeSvg(w.type)}
              <div class="workout-title">${w.title || 'Без названия'}</div>
              <div class="meta">${metaParts.join(' · ')}</div>
              ${w.notes ? `<div class="notes">${w.notes}</div>` : ''}
            </td>
          </tr>
          <tr>
            <th style="width:28px"></th>
            <th>Упражнение</th>
            <th class="center" style="width:52px">Подход</th>
            <th class="center" style="width:64px">Вес</th>
            <th class="center" style="width:52px">Повт.</th>
            <th class="center" style="width:44px">Статус</th>
          </tr>
        </thead>
        <tbody>
          ${exerciseRows}
        </tbody>
      </table>
    `
  }).join('')

  const title = workouts.length === 1 ? workouts[0].title : 'Gym — История тренировок'
  const subtitle = workouts.length === 1
    ? formatDate(workouts[0].date)
    : `Экспорт от ${new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })} · ${workouts.length} тренировок`

  return `
    <style>
      .gym-export-report { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; color: #111; }
      .gym-export-report h1 { font-size: 20px; margin: 0 0 4px; }
      .gym-export-report .subtitle { color: #666; font-size: 12px; margin: 0 0 20px; }
      .gym-export-report table.workout-table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
      .gym-export-report th { background: #f3f4f6; text-align: left; padding: 6px 8px; font-size: 11px; font-weight: 600; color: #555; border-bottom: 1px solid #e5e7eb; }
      .gym-export-report td { padding: 5px 8px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }
      .gym-export-report .center { text-align: center; }
      .gym-export-report .workout-header td { background: #eef2ff; padding: 10px 12px; border-top: 2px solid #6366f1; border-bottom: 1px solid #c7d2fe; overflow: hidden; }
      .gym-export-report .workout-title { font-size: 14px; font-weight: 700; color: #1e1b2e; margin: 1px 0 3px; }
      .gym-export-report .meta { font-size: 11px; color: #6b7280; }
      .gym-export-report .notes { font-size: 11px; color: #555; margin-top: 4px; font-style: italic; }
      .gym-export-report .ex-name { color: #374151; }
      .gym-export-report .ok { color: #16a34a; font-weight: bold; }
      .gym-export-report .failed { color: #dc2626; font-weight: bold; }
    </style>
    <div class="gym-export-report">
      <h1>${title}</h1>
      <p class="subtitle">${subtitle}</p>
      ${workoutTables}
    </div>
  `
}

export async function exportPDF(workouts) {
  const CONTAINER_WIDTH = 800

  // Rendered in normal document flow (just pushed off the visible area) rather than
  // hidden via opacity/visibility — html2canvas rasterizes actual paint output, so an
  // invisible element captures as a blank canvas, which is what produced empty PDFs.
  const container = document.createElement('div')
  container.style.position = 'absolute'
  container.style.top = '0'
  container.style.left = `-${CONTAINER_WIDTH + 100}px`
  container.style.width = `${CONTAINER_WIDTH}px`
  container.style.background = '#ffffff'
  container.innerHTML = buildReportHtml(workouts)
  document.body.appendChild(container)

  try {
    // Let the browser finish layout/paint of the freshly-inserted content before capture.
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))

    const canvas = await html2canvas(container, {
      scale: 2,
      backgroundColor: '#ffffff',
      width: CONTAINER_WIDTH,
      windowWidth: CONTAINER_WIDTH,
    })

    const pageWidthPt = 595.28
    const pageHeightPt = 841.89
    const marginPt = 24
    const contentWidthPt = pageWidthPt - marginPt * 2
    const contentHeightPt = pageHeightPt - marginPt * 2
    const pxToPt = contentWidthPt / canvas.width
    const pageHeightPx = Math.floor(contentHeightPt / pxToPt)

    const doc = new jsPDF({ unit: 'pt', format: 'a4' })
    let renderedPx = 0
    let pageIndex = 0

    while (renderedPx < canvas.height) {
      const sliceHeightPx = Math.min(pageHeightPx, canvas.height - renderedPx)

      const pageCanvas = document.createElement('canvas')
      pageCanvas.width = canvas.width
      pageCanvas.height = sliceHeightPx
      pageCanvas.getContext('2d').drawImage(
        canvas, 0, renderedPx, canvas.width, sliceHeightPx, 0, 0, canvas.width, sliceHeightPx
      )

      if (pageIndex > 0) doc.addPage()
      doc.addImage(
        pageCanvas.toDataURL('image/png'), 'PNG',
        marginPt, marginPt, contentWidthPt, sliceHeightPx * pxToPt
      )

      renderedPx += sliceHeightPx
      pageIndex++
    }

    doc.save(exportFilename(workouts, 'pdf'))
  } finally {
    document.body.removeChild(container)
  }
}
