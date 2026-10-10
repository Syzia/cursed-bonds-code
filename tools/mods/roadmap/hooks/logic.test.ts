import { describe, expect, test } from 'claude-code/testing'

import { BAND_H, bandAlt, bandSvg, barText, fit, headerSvg, phaseSvg, stepsHeight, stepsSvg, widthOf, wrap } from './draw'
import { currentPhase, currentStep, isOpen, metaOf, placeOf, readRoadmap, rough, stepsLeft } from './logic'

const FILE = JSON.stringify({
  goal: { title: 'The finished game', what: 'Playable from start to end.' },
  phases: [
    { id: 'one', title: 'Phase 1', when: 'done 1 Oct', weight: 1, steps: [{ title: 'Plan', state: 'done' }, { title: 'Build', state: 'done' }] },
    {
      id: 'two',
      title: 'Phase 2',
      weight: 2,
      steps: [
        { title: 'Plan', state: 'done' },
        { title: 'Build', state: 'now' },
        { title: 'Pictures', done: 5, total: 20, weight: 2 },
        { title: 'Play it', state: 'planned' },
      ],
    },
    { id: 'three', title: 'Phase 3', weight: 1, outline: true, steps: [{ title: 'Fights' }] },
  ],
})

describe('the file', () => {
  const map = readRoadmap(FILE)

  test('gives each phase its state from its steps', () => {
    expect(map.phases.map(phase => phase.state)).toEqual(['done', 'now', 'planned'])
    expect(map.current).toBe('two')
  })

  test('counts a phase by the weights of its steps: done whole, in hand a half, a count by its share', () => {
    // Plan 1, Build 0.5, Pictures 2 * 5/20, Play it 0: 2 of 5.
    expect(map.phases[1]!.progress).toBe(0.4)
    expect(map.phases[1]!.steps[2]).toEqual({ title: 'Pictures', state: 'now', share: 0.25, weight: 2, count: '5 of 20' })
  })

  test('counts the goal by the weights of its phases', () => {
    // 1 * 1 + 2 * 0.4 + 1 * 0, over 4.
    expect(Math.round(map.progress * 1000) / 1000).toBe(0.45)
  })

  test('says in plain words what is wrong with a file that is not a roadmap', () => {
    expect(() => readRoadmap('{')).toThrow('the file is not valid JSON')
    expect(() => readRoadmap('{"phases":[]}')).toThrow('the file has no goal with a title')
    expect(() => readRoadmap('{"goal":{"title":"G"},"phases":[]}')).toThrow('the file lists no phases')
    expect(() => readRoadmap('{"goal":{"title":"G"},"phases":[{"title":"P","steps":[{}]}]}')).toThrow('step 1 of "P" has no title')
    expect(() => readRoadmap('{"goal":{"title":"G"},"phases":[{"id":"a","title":"P"},{"id":"a","title":"Q"}]}')).toThrow(
      'two phases share an id',
    )
  })

  test('takes a phase with no steps at its word', () => {
    const bare = readRoadmap('{"goal":{"title":"G"},"phases":[{"title":"P","state":"done"},{"title":"Q"}]}')

    expect(bare.phases.map(phase => [phase.state, phase.progress])).toEqual([['done', 1], ['planned', 0]])
    expect(bare.progress).toBe(0.5)
  })
})

describe('the words', () => {
  const map = readRoadmap(FILE)
  const phase = currentPhase(map)!

  test('a percentage is rough, and only a finished thing reads 100%', () => {
    expect(rough(0.31)).toBe('≈31%')
    expect(rough(0)).toBe('0%')
    expect(rough(1)).toBe('100%')
    expect(rough(0.999)).toBe('≈99%')
    expect(rough(0.001)).toBe('≈1%')
  })

  test('the phase in hand, its step, and what is left', () => {
    expect(phase.title).toBe('Phase 2')
    expect(currentStep(phase)?.title).toBe('Build')
    expect(stepsLeft(phase)).toBe(3)
    expect(placeOf(map, phase)).toBe('phase 2 of 3')
    expect(metaOf(phase)).toBe('3 steps left')
    expect(metaOf(map.phases[0]!)).toBe('done 1 Oct')
    expect(metaOf(map.phases[2]!)).toBe('1 step left  ·  an outline, planned when we get there')
  })

  test("only the current phase's steps are listed until the person says otherwise", () => {
    expect(isOpen(map, [], 'two')).toBe(true)
    expect(isOpen(map, [], 'one')).toBe(false)
    expect(isOpen(map, ['two', 'one'], 'two')).toBe(false)
    expect(isOpen(map, ['two', 'one'], 'one')).toBe(true)
  })
})

describe('the drawings', () => {
  const map = readRoadmap(FILE)
  const phase = currentPhase(map)!

  test('a title too wide for its room is cut with an ellipsis', () => {
    expect(fit('Short', 13, 200)).toBe('Short')
    const cut = fit('A very long title that cannot fit', 13, 80)
    expect(cut.endsWith('…')).toBe(true)
    expect(widthOf(cut, 13)).toBeLessThanOrEqual(80)
  })

  test('a sentence runs onto a second line between words, and is cut only at its last', () => {
    expect(wrap('one two three', 10, 1000, 2)).toEqual(['one two three'])
    const room = widthOf('aaa bbb', 10) + 1
    expect(wrap('aaa bbb ccc ddd', 10, room, 2)).toEqual(['aaa bbb', 'ccc ddd'])
    const cut = wrap('aaa bbb ccc ddd eee fff', 10, room, 2)
    expect(cut.length).toBe(2)
    expect(cut[0]).toBe('aaa bbb')
    expect(cut[1]!.endsWith('…')).toBe(true)
    expect(widthOf(cut[1]!, 10)).toBeLessThanOrEqual(room)
  })

  test('the band is one document with both rows, their words escaped', () => {
    const odd = readRoadmap(FILE.replace('The finished game', 'Fish & <chips>'))
    const drawn = bandSvg(700, odd)

    expect(drawn.startsWith(`<svg xmlns="http://www.w3.org/2000/svg" width="700" height="${BAND_H}"`)).toBe(true)
    expect(drawn.endsWith('</svg>')).toBe(true)
    expect(drawn).toContain('Fish &amp; &lt;chips&gt;')
    expect(drawn).toContain('phase 2 of 3')
    expect(drawn).toContain('>Build<')
    expect(drawn).toContain('≈45%')
    expect(drawn).toContain('≈40%')
    expect(bandAlt(map)).toBe('The finished game: ≈45%, phase 2 of 3. Phase 2: ≈40%, now: Build')
  })

  test('even a full band at its widest stays far under the size a drawing may be', () => {
    const full = readRoadmap(FILE.replace(/"now"|"planned"/g, '"done"').replace('"done":5', '"done":20').replace('"title":"Fights"', '"title":"Fights","state":"done"'))

    expect(full.progress).toBe(1)
    expect(bandSvg(1100, full).length).toBeLessThan(100_000)
  })

  test('the pane draws a head, a card for a phase and a line for each step', () => {
    expect(headerSvg(400, map)).toContain('The main goal')
    expect(phaseSvg(400, phase, true)).toContain('3 steps left')
    const steps = stepsSvg(400, phase)
    expect(steps).toContain('5 of 20')
    expect(steps.split('<text').length - 1).toBe(5)
    expect(stepsHeight(phase)).toBe(86)
  })

  test('a surface with no pictures gets a bar of blocks', () => {
    expect(barText(0.4, 10)).toBe('████░░░░░░')
  })
})
