// The roadmap's drawings for the desktop: each is one SVG document, drawn as
// an image. A row is a dot, a title, a bar filled with small squares that
// thicken towards its head, a label riding the head, and a rough percentage.
// Colours follow the person's light or dark theme from inside the drawing.

import type { Phase, Roadmap, Step } from '../types'
import { currentPhase, currentStep, metaOf, placeOf, rough, stepsLeft } from './logic'

export const FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',sans-serif"
/** The work in hand. */
export const ACCENT = '#8f8cf4'
/** The main goal. */
export const GOAL = '#D97757'
export const DONE = '#5fbf8f'

const ROW = 22
const BAR = 16
const CELL = 3
/** The band: the goal's row over the current phase's. */
export const BAND_H = ROW * 2 + 4
export const HEADER_H = 106
export const PHASE_H = 56
const STEP_H = 20

const STYLE = `<style>
.t{fill:#1f1f1f}.s{fill:#6b6b68}.m{fill:#9a9a96}.k{fill:#e4e4e2}.ln{stroke:#e4e4e1}.tile{fill:#f4f3f0}.ring{stroke:#b4b4b0}
@media (prefers-color-scheme: dark){.t{fill:#ececec}.s{fill:#a8a8a4}.m{fill:#7d7d79}.k{fill:#2c2c2c}.ln{stroke:#333331}.tile{fill:#262625}.ring{stroke:#5a5a5a}}
.p0,.p1,.p2,.p3{animation:glint 2.4s ease-in-out infinite}
.p1{animation-duration:3.1s;animation-delay:-.8s}.p2{animation-duration:2s;animation-delay:-1.4s}.p3{animation-duration:3.6s;animation-delay:-.3s}
@keyframes glint{0%,100%{opacity:1}50%{opacity:.35}}
.live{animation:pulse 1.6s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}
.still .p0,.still .p1,.still .p2,.still .p3{animation:none}
@media (prefers-reduced-motion: reduce){.p0,.p1,.p2,.p3,.live{animation:none}}
</style>`

const xml = (text: string): string =>
  text.replace(/[&<>"]/g, ch => (ch === '&' ? '&amp;' : ch === '<' ? '&lt;' : ch === '>' ? '&gt;' : '&quot;'))

// How wide system text runs, roughly, in ems: enough to give a title its room.
const advance = (ch: string): number => (" .,:;'|!ilj1()[]·".includes(ch) ? 0.3 : /[A-ZmwMW@%≈]/.test(ch) ? 0.7 : 0.55)

export const widthOf = (text: string, size: number): number => [...text].reduce((sum, ch) => sum + advance(ch) * size, 0)

/** `text`, cut with an ellipsis when it would run wider than `max` pixels. */
export function fit(text: string, size: number, max: number): string {
  if (widthOf(text, size) <= max) return text

  let out = ''
  for (const ch of text) {
    if (widthOf(`${out}${ch}…`, size) > max) break
    out += ch
  }

  return `${out.trimEnd()}…`
}

/** `text` on at most `lines` lines of `max` pixels, broken between words; the last line is cut if it must be. */
export function wrap(text: string, size: number, max: number, lines: number): string[] {
  const out: string[] = []
  let line = ''

  for (const word of text.split(/\s+/).filter(part => part !== '')) {
    const longer = line === '' ? word : `${line} ${word}`
    if (widthOf(longer, size) <= max || line === '') {
      line = longer
      continue
    }
    if (out.length === lines - 1) {
      line = longer
      break
    }
    out.push(line)
    line = word
  }
  if (line !== '') out.push(fit(line, size, max))

  return out
}

// The same square is filled or empty at every redraw, so the bar never shimmers by accident.
const grain = (column: number, row: number): number => {
  const value = Math.sin(column * 127.1 + row * 311.7) * 43758.5453

  return value - Math.floor(value)
}

/** The squares that fill `width` pixels of a bar: sparse at its start, dense at its head. */
function squares(width: number): string {
  const columns = Math.floor(width / CELL)
  const rows = Math.floor(BAR / CELL)
  const out: string[] = []

  for (let column = 0; column < columns; column++) {
    const density = 0.3 + 0.65 * Math.pow(column / Math.max(1, columns - 1), 1.3)
    for (let row = 0; row < rows; row++) {
      if (grain(column, row) < density) {
        out.push(`<rect class="p${Math.floor(grain(row + 11, column + 5) * 4)}" x="${column * CELL + 1}" y="${row * CELL + 1}" width="2" height="2"/>`)
      }
    }
  }

  return out.join('')
}

type Row = {
  /** The drawing's width and where the row starts, in pixels. */
  width: number
  top: number
  /** Unique within the drawing: it names the row's clip. */
  id: string
  title: string
  /** The room every row of the drawing gives its title, so that the bars line up. */
  titleWidth: number
  label: string
  share: number
  color: string
  isMoving: boolean
}

function row(spec: Row): string {
  const barLeft = Math.round(16 + spec.titleWidth + 12)
  // A bar past 520 px would spend the drawing's size on squares nobody counts.
  const barWidth = Math.max(60, Math.min(520, spec.width - barLeft - 52))
  const share = Math.max(0, Math.min(1, spec.share))
  const color = share >= 1 ? DONE : spec.color
  const filled = Math.round(barWidth * share)
  const label = fit(spec.label, 11, barWidth * 0.6)
  const labelWidth = Math.round(18 + widthOf(label, 11))
  // The label rides the bar's head; where the filled part is too short to hold it, it sits just past the head,
  // so that what is filled is always as long as the share it stands for.
  const labelLeft =
    labelWidth <= filled ? filled - labelWidth : Math.max(0, Math.min(barWidth - labelWidth, filled + (filled > 0 ? 4 : 0)))
  const middle = ROW / 2

  return `<g transform="translate(0,${spec.top})"${spec.isMoving ? '' : ' class="still"'}>
<defs><clipPath id="${spec.id}"><rect width="${barWidth}" height="${BAR}" rx="${BAR / 2}"/></clipPath></defs>
<circle cx="5" cy="${middle}" r="4" fill="${color}"/>
<text class="t" x="16" y="${middle + 4.5}" font-family="${FONT}" font-size="13" font-weight="500">${xml(fit(spec.title, 13, spec.titleWidth))}</text>
<g transform="translate(${barLeft},${(ROW - BAR) / 2})">
<rect class="k" width="${barWidth}" height="${BAR}" rx="${BAR / 2}"/>
<g clip-path="url(#${spec.id})" fill="${color}">${squares(filled)}</g>
<rect x="${labelLeft}" width="${labelWidth}" height="${BAR}" rx="${BAR / 2}" fill="${color}"/>
<text x="${labelLeft + labelWidth / 2}" y="${BAR / 2 + 4}" text-anchor="middle" font-family="${FONT}" font-size="11" font-weight="600" fill="#ffffff">${xml(label)}</text>
</g>
<text class="m" x="${barLeft + barWidth + 8}" y="${middle + 4.5}" font-family="${FONT}" font-size="12.5" font-variant-numeric="tabular-nums">${rough(share)}</text>
</g>`
}

const svg = (width: number, height: number, body: string): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${STYLE}${body}</svg>`

/** The band above the prompt: the main goal's row over the row of the phase in hand. */
export function bandSvg(width: number, map: Roadmap): string {
  const phase = currentPhase(map)
  if (phase === undefined) return svg(width, BAND_H, '')

  const step = currentStep(phase)
  const room = Math.max(60, width * 0.4)
  const titleWidth = Math.min(room, Math.max(widthOf(map.title, 13), widthOf(phase.title, 13)))

  return svg(
    width,
    BAND_H,
    row({ width, top: 0, id: 'goal', title: map.title, titleWidth, label: placeOf(map, phase), share: map.progress, color: GOAL, isMoving: false }) +
      row({
        width,
        top: ROW + 4,
        id: 'phase',
        title: phase.title,
        titleWidth,
        label: step === undefined ? 'done' : step.title,
        share: phase.progress,
        color: ACCENT,
        isMoving: phase.state === 'now',
      }),
  )
}

/** What the band says, for a reader who cannot see it. */
export function bandAlt(map: Roadmap): string {
  const phase = currentPhase(map)
  if (phase === undefined) return `${map.title}: ${rough(map.progress)}`

  const step = currentStep(phase)

  return `${map.title}: ${rough(map.progress)}, ${placeOf(map, phase)}. ${phase.title}: ${rough(phase.progress)}${step === undefined ? '' : `, now: ${step.title}`}`
}

/** The pane's head: the goal in words, then three figures. */
export function headerSvg(width: number, map: Roadmap): string {
  const phase = currentPhase(map)
  const gap = 6
  const tileWidth = (width - gap * 2) / 3
  const tile = (n: number, name: string, value: string): string =>
    `<rect class="tile" x="${n * (tileWidth + gap)}" y="60" width="${tileWidth}" height="42" rx="8"/>
<text class="s" x="${n * (tileWidth + gap) + 9}" y="77" font-family="${FONT}" font-size="11">${xml(fit(name, 11, tileWidth - 18))}</text>
<text class="t" x="${n * (tileWidth + gap) + 9}" y="95" font-family="${FONT}" font-size="15" font-weight="600" font-variant-numeric="tabular-nums">${xml(value)}</text>`
  const what = wrap(map.what, 11.5, width, 2)
    .map((line, n) => `<text class="s" x="0" y="${34 + n * 15}" font-family="${FONT}" font-size="11.5">${xml(line)}</text>`)
    .join('')

  return svg(
    width,
    HEADER_H,
    `<circle cx="5" cy="10" r="4" fill="${GOAL}"/>
<text class="t" x="16" y="15" font-family="${FONT}" font-size="14" font-weight="600">${xml(fit(map.title, 14, width - 16))}</text>
${what}
${tile(0, 'The main goal', rough(map.progress))}${tile(1, 'This phase', phase === undefined ? '–' : rough(phase.progress))}${tile(2, 'Steps left in it', phase === undefined ? '–' : String(stepsLeft(phase)))}`,
  )
}

// A done thing is a green disc with a tick, the thing in hand a pulsing dot, a planned one a ring.
function mark(x: number, y: number, state: Step['state'], color: string): string {
  if (state === 'done') {
    return `<circle cx="${x}" cy="${y}" r="6" fill="${DONE}"/><path d="M${x - 3},${y} l2,2.4 l4,-5" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>`
  }
  if (state === 'now') return `<circle class="live" cx="${x}" cy="${y}" r="5" fill="${color}"/>`

  return `<circle class="ring" cx="${x}" cy="${y}" r="4.5" fill="none" stroke-width="1.5"/>`
}

/** One phase: its mark and title, a line of small print, a thin bar, its rough percentage. */
export function phaseSvg(width: number, phase: Phase, isCurrent: boolean): string {
  const color = phase.state === 'done' ? DONE : ACCENT
  const barWidth = width - 22
  const percent = rough(phase.progress)
  const titleRoom = width - 22 - widthOf(percent, 12.5) - 10

  return svg(
    width,
    PHASE_H,
    `${mark(7, 13, phase.state, color)}
<text class="${phase.state === 'planned' ? 's' : 't'}" x="22" y="17.5" font-family="${FONT}" font-size="13" font-weight="${isCurrent ? 700 : 600}">${xml(fit(phase.title, 13, titleRoom))}</text>
<text class="m" x="${width}" y="17.5" text-anchor="end" font-family="${FONT}" font-size="12.5" font-variant-numeric="tabular-nums">${percent}</text>
<text class="m" x="22" y="34" font-family="${FONT}" font-size="11">${xml(fit(metaOf(phase) || phase.what, 11, barWidth))}</text>
<rect class="k" x="22" y="42" width="${barWidth}" height="6" rx="3"/>
<rect x="22" y="42" width="${Math.round(barWidth * Math.max(0, Math.min(1, phase.progress)))}" height="6" rx="3" fill="${color}"/>
<line class="ln" x1="0" y1="${PHASE_H - 0.5}" x2="${width}" y2="${PHASE_H - 0.5}"/>`,
  )
}

export const stepsHeight = (phase: Phase): number => phase.steps.length * STEP_H + 6

/** A phase's steps, one to a line: its mark, its words, and its count when it is one. */
export function stepsSvg(width: number, phase: Phase): string {
  const lines = phase.steps.map((step, n) => {
    const y = n * STEP_H + 12
    const room = width - 36 - (step.count === '' ? 0 : widthOf(step.count, 11) + 10)
    const look = step.state === 'done' ? 'class="m"' : step.state === 'now' ? 'class="t" font-weight="600"' : 'class="s"'

    return `${mark(26, y, step.state, ACCENT)}
<text ${look} x="40" y="${y + 4}" font-family="${FONT}" font-size="12">${xml(fit(step.title, 12, room - 8))}</text>${
      step.count === ''
        ? ''
        : `<text class="m" x="${width}" y="${y + 4}" text-anchor="end" font-family="${FONT}" font-size="11" font-variant-numeric="tabular-nums">${xml(step.count)}</text>`
    }`
  })

  return svg(width, stepsHeight(phase), lines.join('\n'))
}

/** A plain bar for a surface that draws no pictures: "█████░░░░░". */
export function barText(share: number, cells: number): string {
  const filled = Math.round(cells * Math.max(0, Math.min(1, share)))

  return '█'.repeat(filled) + '░'.repeat(cells - filled)
}
