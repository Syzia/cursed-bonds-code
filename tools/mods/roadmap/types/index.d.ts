/** Where a step, or a whole phase, stands. */
export type StepState = 'done' | 'now' | 'planned'

/** One step of a phase, as read from the roadmap file. */
export type Step = {
  title: string
  state: StepState
  /** How much of the step is done, 0 to 1: a count's share, or 1, a half or 0 by its state. */
  share: number
  /** Its rough share of the phase's work. */
  weight: number
  /** "6 of 49" for a step that is a count; '' otherwise. */
  count: string
}

/** One phase on the way to the main goal. */
export type Phase = {
  id: string
  title: string
  what: string
  /** "done 1 Oct", "since 6 Oct"; '' when the file gives none. */
  when: string
  state: StepState
  /** Its rough share of the whole work. */
  weight: number
  /** How much of it is done, 0 to 1, by its steps' weights. */
  progress: number
  /** True for a phase that has not been planned yet: its steps are only an outline. */
  isOutline: boolean
  steps: Step[]
}

/** The roadmap as it is drawn. */
export type Roadmap = {
  title: string
  what: string
  /** How much of the main goal is done, 0 to 1, by the phases' weights. */
  progress: number
  /** The id of the phase being worked on. */
  current: string
  phases: Phase[]
}

declare module 'claude-code' {
  interface PluginState {
    roadmap: {
      map: Roadmap | null
      /** Why the file could not be read; '' when it could. */
      problem: string
      /** Phases whose list of steps the person opened or closed, against the default (only the current one open). */
      toggled: string[]
      /** True while the person has dismissed the band. */
      hidden: boolean
    }
  }
}
