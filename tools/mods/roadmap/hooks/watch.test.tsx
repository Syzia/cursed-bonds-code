// roadmap run through the engine, over a project whose roadmap file is held in memory.

import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

const ROOT = '/work'
const PATH = `${ROOT}/docs/roadmap.json`
const POLL = 10_000

const fileOf = (build: string, pictures: number): string =>
  JSON.stringify({
    goal: { title: 'The finished game', what: 'Playable from start to end.' },
    phases: [
      { id: 'one', title: 'Phase 1', steps: [{ title: 'Plan', state: 'done' }] },
      {
        id: 'two',
        title: 'Phase 2',
        steps: [
          { title: 'Build the thing', state: build },
          { title: 'Pictures', done: pictures, total: 10 },
        ],
      },
    ],
  })

const BAND = { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 100, scroll: { offset: 0, bodyRows: 9 }, view: {} }
const PANE = { title: 'Roadmap', isFocused: false, bodyColumns: 60, bodyRows: 30 }

// The world beneath the mod. A test changes the file between looks.
function world(on: On) {
  const state = { text: fileOf('now', 2) as string | null, mtime: 1, toasts: [] as string[], panes: [] as string[] }
  const clock = mock.clock(on, { now: 1_800_000_000_000 })

  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('command.register', ($, e) => ({ value: { command: e.name } }))
  on('session.root', () => ({ value: ROOT }))
  on('fs.stat', ($, e) =>
    e.path === PATH && state.text !== null
      ? { value: { kind: 'file', size: state.text.length, mtimeMs: state.mtime, isLink: false } }
      : { deny: 'ENOENT' },
  )
  on('fs.read', () => ({ value: state.text ?? '' }))
  on('ui.toast', ($, e) => {
    state.toasts.push(e.text)

    return { value: undefined }
  })
  on('ui.panes', () => ({ value: state.panes.map(id => ({ id, title: 'Roadmap', isShown: true, isFocused: false, isPlaced: true })) }))
  on('ui.open', ($, e) => {
    state.panes.push(e.id)

    return { value: { isPlaced: true } }
  })
  on('ui.close', ($, e) => {
    state.panes = state.panes.filter(id => id !== e.id)

    return { value: undefined }
  })
  // What another mod, or the engine, draws in the band.
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>another bar</Text>
  })

  const write = (text: string | null) => {
    state.text = text
    state.mtime += 1
  }

  return { state, clock, write }
}

test('the band draws the goal over the phase in hand, and keeps what is beneath it', async ($, on) => {
  const { clock } = world(on)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  const desktop = await $.ui.mount({ plugin: 'roadmap', surface: 'desktop', component: 'AbovePrompt', props: BAND })
  const picture = await desktop.find({ type: 'Svg' })
  expect(picture).toBeDefined()
  expect(await desktop.find({ key: 'roadmap-open' })).toBeDefined()
  expect(await desktop.find({ type: 'Text', text: 'another bar' })).toBeDefined()
  await desktop.unmount()

  const terminal = await $.ui.mount({ plugin: 'roadmap', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await terminal.find({ type: 'Text', text: 'The finished game' })).toBeDefined()
  expect(await terminal.find({ type: 'Text', text: /now: Build the thing/ })).toBeDefined()
  expect(await terminal.find({ type: 'Text', text: 'another bar' })).toBeDefined()
  await terminal.unmount()
})

test('dismissing the band leaves the other bar alone, and a step that finishes brings it back with a toast', async ($, on) => {
  const { state, clock, write } = world(on)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  const ui = await $.ui.mount({ plugin: 'roadmap', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  await ui.press({ key: 'roadmap-dismiss' })
  expect(await ui.find({ type: 'Text', text: 'The finished game' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'another bar' })).toBeDefined()

  write(fileOf('done', 2))
  await clock.advance(POLL)
  expect(state.toasts).toEqual(['Done: Build the thing · Phase 2 ≈60%'])
  expect(await ui.find({ type: 'Text', text: 'The finished game' })).toBeDefined()
  await ui.unmount()
})

test('the pane lists every phase, and the steps of the one in hand', async ($, on) => {
  const { clock } = world(on)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  const ui = await $.ui.mount({ plugin: 'roadmap', surface: 'terminal', component: 'Pane', requestId: 'roadmap', props: PANE })
  expect(await ui.find({ type: 'Text', text: 'Phase 1' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Build the thing/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Pictures \(2 of 10\)/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Plan/ })).toBeUndefined()

  await ui.press({ key: 'steps-one' })
  expect(await ui.find({ type: 'Text', text: /Plan/ })).toBeDefined()
  await ui.press({ key: 'steps-two' })
  expect(await ui.find({ type: 'Text', text: /Build the thing/ })).toBeUndefined()
  await ui.unmount()

  const desktop = await $.ui.mount({ plugin: 'roadmap', surface: 'desktop', component: 'Pane', requestId: 'roadmap', props: PANE })
  expect((await desktop.findAll({ type: 'Svg' })).length).toBe(4)
  await desktop.unmount()
})

test('a file that stops being a roadmap keeps the last good one on show and says why', async ($, on) => {
  const { clock, write } = world(on)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  write('{ not json')
  await clock.advance(POLL)

  const ui = await $.ui.mount({ plugin: 'roadmap', surface: 'terminal', component: 'Pane', requestId: 'roadmap', props: PANE })
  expect(await ui.find({ type: 'Text', text: 'Phase 2' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /cannot be read \(docs\/roadmap.json: the file is not valid JSON\)/ })).toBeDefined()
  await ui.unmount()
})

test('with no file there is no band, and the pane says so', async ($, on) => {
  const { clock, write } = world(on)
  write(null)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  const band = await $.ui.mount({ plugin: 'roadmap', surface: 'desktop', component: 'AbovePrompt', props: BAND })
  expect(await band.find({ type: 'Svg' })).toBeUndefined()
  expect(await band.find({ type: 'Text', text: 'another bar' })).toBeDefined()
  await band.unmount()

  const pane = await $.ui.mount({ plugin: 'roadmap', surface: 'desktop', component: 'Pane', requestId: 'roadmap', props: PANE })
  expect(await pane.find({ type: 'Text', text: 'The roadmap cannot be shown: there is no docs/roadmap.json in this project.' })).toBeDefined()
  await pane.unmount()
})

test('/roadmap opens the pane, and closes it when it is open', async ($, on) => {
  const { state, clock } = world(on)

  await $.session.start({ cwd: ROOT, surface: 'desktop', isInteractive: true })
  await clock.settle()

  expect((await $.command.run({ command: 'roadmap', args: '' })).text).toBe('Roadmap opened.')
  expect(state.panes).toEqual(['roadmap'])
  expect((await $.command.run({ command: 'roadmap', args: '' })).text).toBe('Roadmap closed.')
  expect(state.panes).toEqual([])
})
