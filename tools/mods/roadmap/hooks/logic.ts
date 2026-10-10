// Reading the roadmap file and the arithmetic of "how far along": nothing here
// needs the engine, so each part is tested alone.

import type { Phase, Roadmap, Step, StepState } from '../types'

const STATES: readonly StepState[] = ['done', 'now', 'planned']

/** A value from the file as a plain object, or null when it is anything else. */
function record(value: unknown): Record<string, unknown> | null {
  return typeof value === 'object' && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : null
}

const text = (value: unknown): string => (typeof value === 'string' ? value.trim() : '')
const weightOf = (value: unknown): number => (typeof value === 'number' && value > 0 ? value : 1)
const stateOf = (value: unknown): StepState | null =>
  STATES.includes(value as StepState) ? (value as StepState) : null

/** One step: a count when it has a `total`, else done, now (half) or planned by its state. */
function stepFrom(value: unknown, where: string): Step {
  const row = record(value)
  const title = text(row?.title)
  if (row === null || title === '') throw new Error(`${where} has no title`)

  const total = row.total
  if (typeof total === 'number' && total > 0) {
    const done = Math.max(0, Math.min(total, typeof row.done === 'number' ? row.done : 0))
    const asked = stateOf(row.state)
    const state = done >= total ? 'done' : done > 0 || asked === 'now' ? 'now' : 'planned'

    return { title, state, share: done / total, weight: weightOf(row.weight), count: `${done} of ${total}` }
  }

  const state = stateOf(row.state) ?? 'planned'

  return { title, state, share: state === 'done' ? 1 : state === 'now' ? 0.5 : 0, weight: weightOf(row.weight), count: '' }
}

function phaseFrom(value: unknown, n: number): Phase {
  const row = record(value)
  const title = text(row?.title)
  if (row === null || title === '') throw new Error(`phase ${n} has no title`)

  const steps = (Array.isArray(row.steps) ? row.steps : []).map((step, i) => stepFrom(step, `step ${i + 1} of "${title}"`))
  const weight = steps.reduce((sum, step) => sum + step.weight, 0)
  const asked = stateOf(row.state)
  // A phase with no steps is as far along as the file says it is.
  const progress =
    steps.length === 0 ? (asked === 'done' ? 1 : 0) : steps.reduce((sum, step) => sum + step.weight * step.share, 0) / weight
  const state: StepState =
    steps.length === 0
      ? (asked ?? 'planned')
      : steps.every(step => step.state === 'done')
        ? 'done'
        : steps.every(step => step.state === 'planned')
          ? 'planned'
          : 'now'

  return {
    id: text(row.id) || `phase-${n}`,
    title,
    what: text(row.what),
    when: text(row.when),
    state,
    weight: weightOf(row.weight),
    progress,
    isOutline: row.outline === true,
    steps,
  }
}

/** The roadmap a file holds. Throws, in plain words, when the file is not one. */
export function readRoadmap(source: string): Roadmap {
  let parsed: unknown
  try {
    parsed = JSON.parse(source)
  } catch {
    throw new Error('the file is not valid JSON')
  }

  const root = record(parsed)
  const goal = record(root?.goal)
  const title = text(goal?.title)
  if (root === null || title === '') throw new Error('the file has no goal with a title')
  if (!Array.isArray(root.phases) || root.phases.length === 0) throw new Error('the file lists no phases')

  const phases = root.phases.map((phase, i) => phaseFrom(phase, i + 1))
  const ids = new Set(phases.map(phase => phase.id))
  if (ids.size !== phases.length) throw new Error('two phases share an id')

  const weight = phases.reduce((sum, phase) => sum + phase.weight, 0)
  const current =
    phases.find(phase => phase.state === 'now') ?? phases.find(phase => phase.state === 'planned') ?? phases[phases.length - 1]

  return {
    title,
    what: text(goal?.what),
    progress: phases.reduce((sum, phase) => sum + phase.weight * phase.progress, 0) / weight,
    current: current?.id ?? '',
    phases,
  }
}

/** A share as a rough percentage: "≈31%"; plain "0%" and "100%" at the ends. */
export function rough(share: number): string {
  const percent = Math.round(Math.max(0, Math.min(1, share)) * 100)
  // Nearly there is not there: only a finished thing reads 100%.
  const shown = share < 1 && percent === 100 ? 99 : share > 0 && percent === 0 ? 1 : percent

  return shown === 0 || shown === 100 ? `${shown}%` : `≈${shown}%`
}

/** The phase being worked on, by the roadmap's own word. */
export function currentPhase(map: Roadmap): Phase | undefined {
  return map.phases.find(phase => phase.id === map.current)
}

/** The step a phase is on: the first one under way, else the next one planned. */
export function currentStep(phase: Phase): Step | undefined {
  return phase.steps.find(step => step.state === 'now') ?? phase.steps.find(step => step.state === 'planned')
}

/** How many of a phase's steps are not done yet. */
export function stepsLeft(phase: Phase): number {
  return phase.steps.filter(step => step.state !== 'done').length
}

/** Where a phase stands among the others: "phase 3 of 7". */
export function placeOf(map: Roadmap, phase: Phase): string {
  return `phase ${map.phases.indexOf(phase) + 1} of ${map.phases.length}`
}

/** Whether a phase's steps are listed: the current phase's are unless closed, another's only when opened. */
export function isOpen(map: Roadmap, toggled: readonly string[], id: string): boolean {
  return (id === map.current) !== toggled.includes(id)
}

/** One line for a phase under its title: when, how many steps are left, whether it is only an outline. */
export function metaOf(phase: Phase): string {
  const left = stepsLeft(phase)
  const parts = [
    phase.when,
    phase.state === 'done' ? '' : `${left} ${left === 1 ? 'step' : 'steps'} left`,
    phase.isOutline ? 'an outline, planned when we get there' : '',
  ]

  return parts.filter(part => part !== '').join('  ·  ')
}
