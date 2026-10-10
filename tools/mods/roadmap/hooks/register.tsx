// roadmap: the road to the finished game, kept in sight.
//
// It reads one file of the project, docs/roadmap.json (the main goal, its
// phases, each phase's steps), and draws it: a band above the prompt with the
// main goal's bar over the bar of the phase in hand, and a pane (/roadmap) that
// lists every phase with its steps. It looks at the file every ten seconds and
// redraws when it has changed; a step that has just been finished gets a toast.
// It only reads and draws. Whatever another mod draws in the band stays, under
// this one's rows.

import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Roadmap } from '../types'
import {
  BAND_H,
  HEADER_H,
  PHASE_H,
  bandAlt,
  bandSvg,
  barText,
  headerSvg,
  phaseSvg,
  stepsHeight,
  stepsSvg,
} from './draw'
import { currentPhase, currentStep, isOpen, metaOf, placeOf, readRoadmap, rough, stepsLeft } from './logic'

const PANE = 'roadmap'
const POLL_MS = 10_000
const MARK = { done: '✓', now: '●', planned: '○' } as const

const roadmap = atom({ plugin: 'roadmap', key: 'map' } as const, null)
const problem = atom({ plugin: 'roadmap', key: 'problem' } as const, '')
const toggled = atom({ plugin: 'roadmap', key: 'toggled' } as const, [])
const hidden = atom({ plugin: 'roadmap', key: 'hidden' } as const, false)

// The steps that are done in `after` and were not in `before`, as "phase: step".
function finished(before: Roadmap, after: Roadmap): string[] {
  const was = new Set(
    before.phases.flatMap(phase => phase.steps.filter(step => step.state === 'done').map(step => `${phase.id}\n${step.title}`)),
  )

  return after.phases.flatMap(phase =>
    phase.steps.filter(step => step.state === 'done' && !was.has(`${phase.id}\n${step.title}`)).map(step => step.title),
  )
}

export const register: Register = (on, options) => {
  const asked = typeof options.file === 'string' ? options.file.trim() : ''
  const file = asked === '' ? 'docs/roadmap.json' : asked

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'roadmap',
      description: 'Show or hide the roadmap: the main goal, its phases and their steps',
    })

    let seen = ''
    let written = ''
    let isLooking = false

    const say = async (why: string) => {
      if ((await read($, problem)) !== why) await update($, problem, () => why)
    }

    const look = async () => {
      if (isLooking) return
      isLooking = true
      try {
        const path = file.startsWith('/') ? file : `${await $.session.root()}/${file}`
        const stat = await $.fs.stat(path).catch(() => undefined)
        if (stat === undefined) {
          seen = ''
          await say(`there is no ${file} in this project`)
          return
        }

        const stamp = `${stat.mtimeMs}:${stat.size}`
        if (stamp === seen) return
        seen = stamp

        let latest: Roadmap
        try {
          latest = readRoadmap(await $.fs.read(path))
        } catch (error) {
          await say(`${file}: ${error instanceof Error ? error.message : 'it could not be read'}`)
          return
        }
        await say('')

        const text = JSON.stringify(latest)
        if (text === written) return
        const before = await read($, roadmap)
        written = text
        await update($, roadmap, () => latest)

        // What changed is worth a look: the band comes back, and a finished step is said.
        if (before !== null && JSON.stringify(before) !== text) {
          await update($, hidden, () => false)
          const phase = currentPhase(latest)
          for (const title of finished(before, latest).slice(0, 2)) {
            $.ui.toast(`Done: ${title}${phase === undefined ? '' : ` · ${phase.title} ${rough(phase.progress)}`}`, {
              timeoutMs: 12_000,
            })
          }
        }
      } finally {
        isLooking = false
      }
    }

    $.clock.every(POLL_MS, () => {
      void look().catch(() => undefined)
    })
    void look().catch(() => undefined)

    return next(e)
  })

  on('command.run', { command: 'roadmap' }, async $ => {
    const isUp = (await $.ui.panes()).some(pane => pane.id === PANE)
    if (isUp) {
      await $.ui.close({ id: PANE })

      return { text: 'Roadmap closed.' }
    }
    await update($, hidden, () => false)
    await $.ui.open({ id: PANE, title: 'Roadmap' })

    return { text: 'Roadmap opened.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const map = await read($, roadmap)
    if (e.props.hasSurvey || map === null || (await read($, hidden))) return next(e)

    const phase = currentPhase(map)
    if (phase === undefined) return next(e)

    // Whatever is drawn beneath (another mod's bar, the engine's own) keeps its place under these rows.
    const beneath = await next(e)
    const ui = $.ui.resolve(e)
    const { Box, Button, Text } = ui
    const open = <Button key="roadmap-open" label="Roadmap" plain onPress={() => $.ui.open({ id: PANE, title: 'Roadmap' })} />
    const dismiss = <Button key="roadmap-dismiss" label="✕" plain role="dismiss" onPress={() => update($, hidden, () => true)} />

    // The terminal's table answers for Svg with an empty box: only a surface that draws pictures gets them.
    if (e.surface !== 'terminal' && 'Svg' in ui) {
      const { Svg } = ui
      // About 8 CSS px to a reported column; the rest is the two buttons and their gaps.
      const width = Math.max(220, Math.min(1100, (e.props.bodyColumns || 100) * 8 - 150))

      return (
        <Box flexDirection="column">
          <Box flexDirection="row" alignItems="center" gap={1}>
            <Svg source={bandSvg(width, map)} alt={bandAlt(map)} width={width} height={BAND_H} />
            {open}
            {dismiss}
          </Box>
          {beneath}
        </Box>
      )
    }

    const step = currentStep(phase)
    const cells = Math.max(6, Math.min(30, Math.floor(e.props.bodyColumns / 4)))

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={2}>
          <Text color="claude">◆</Text>
          <Text wrap="truncate-end">{map.title}</Text>
          <Text color="claude">{barText(map.progress, cells)}</Text>
          <Text dimColor>
            {rough(map.progress)} · {placeOf(map, phase)}
          </Text>
        </Box>
        <Box flexDirection="row" gap={2}>
          <Text color="suggestion">●</Text>
          <Text wrap="truncate-end">{phase.title}</Text>
          <Text color="suggestion">{barText(phase.progress, cells)}</Text>
          <Text dimColor>
            {rough(phase.progress)}
            {step === undefined ? '' : ` · now: ${step.title}`}
          </Text>
          {open}
          {dismiss}
        </Box>
        {beneath}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const ui = $.ui.resolve(e)
    const { Box, Button, Text } = ui
    const map = await read($, roadmap)
    const why = await read($, problem)
    const flips = await read($, toggled)

    if (map === null) {
      return (
        <Box flexDirection="column">
          <Text>{why === '' ? 'Reading the roadmap…' : `The roadmap cannot be shown: ${why}.`}</Text>
        </Box>
      )
    }

    const flip = (id: string) => () =>
      update($, toggled, list => (list.includes(id) ? list.filter(one => one !== id) : [...list, id]))
    const current = currentPhase(map)
    const warning = why === '' ? null : <Text color="warning">The file has changed and cannot be read ({why}); this is the last good copy.</Text>

    if (e.surface !== 'terminal' && 'Svg' in ui) {
      const { Svg } = ui
      const width = Math.max(240, Math.min(900, (e.props.bodyColumns || 40) * 8 - 8))

      return (
        <Box flexDirection="column">
          <Svg
            source={headerSvg(width, map)}
            alt={`${map.title}: ${rough(map.progress)}. ${map.what}`}
            width={width}
            height={HEADER_H}
          />
          {warning}
          {map.phases.map(phase => {
            const isListed = isOpen(map, flips, phase.id)

            return (
              <Box key={`phase-${phase.id}`} flexDirection="column">
                <Svg
                  source={phaseSvg(width, phase, phase.id === map.current)}
                  alt={`${phase.title}: ${phase.state}, ${rough(phase.progress)}. ${metaOf(phase)}`}
                  width={width}
                  height={PHASE_H}
                />
                {phase.steps.length > 0 && (
                  <Button
                    key={`steps-${phase.id}`}
                    label={`${isListed ? '▾' : '▸'} ${phase.steps.length} ${phase.steps.length === 1 ? 'step' : 'steps'}`}
                    plain
                    onPress={flip(phase.id)}
                  />
                )}
                {isListed && phase.steps.length > 0 && (
                  <Svg
                    source={stepsSvg(width, phase)}
                    alt={phase.steps.map(step => `${step.state}: ${step.title}${step.count === '' ? '' : ` (${step.count})`}`).join('; ')}
                    width={width}
                    height={stepsHeight(phase)}
                  />
                )}
              </Box>
            )
          })}
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        <Text bold>
          {map.title} · {rough(map.progress)}
        </Text>
        <Text dimColor>
          {current === undefined ? '' : `${current.title}: ${rough(current.progress)}, ${stepsLeft(current)} steps left`}
        </Text>
        {warning}
        {map.phases.map(phase => {
          const isListed = isOpen(map, flips, phase.id)

          return (
            <Box key={`phase-${phase.id}`} flexDirection="column">
              <Box flexDirection="row" gap={1}>
                <Text color={phase.state === 'done' ? 'success' : phase.state === 'now' ? 'suggestion' : 'inactive'}>
                  {MARK[phase.state]}
                </Text>
                <Text bold={phase.id === map.current}>{phase.title}</Text>
                <Text dimColor>{rough(phase.progress)}</Text>
                {phase.steps.length > 0 && (
                  <Button key={`steps-${phase.id}`} label={isListed ? '▾' : '▸'} plain onPress={flip(phase.id)} />
                )}
              </Box>
              {isListed &&
                phase.steps.map(step => (
                  <Text dimColor={step.state !== 'now'}>
                    {'  '}
                    {MARK[step.state]} {step.title}
                    {step.count === '' ? '' : ` (${step.count})`}
                  </Text>
                ))}
            </Box>
          )
        })}
      </Box>
    )
  })
}
