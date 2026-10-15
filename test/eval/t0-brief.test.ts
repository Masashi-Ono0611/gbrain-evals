import { describe, expect, test } from 'bun:test';
import { generatePersona, PP_BRIEF_DEV_SEEDS, PP_DEV_SEEDS, solvabilityProblems } from '../../eval/generators/program-primary-gen.ts';
import { ARMS, scriptedRememberer } from '../../eval/runner/t0-program-primary.ts';
import { BRIEF_ARMS, BRIEF_HEADER, briefBlock, briefConfig, BriefGuardError, cellBrief, classifyItem, pairedSuccess, PROACTIVE_BRIEF_KEY } from '../../eval/runner/t0/brief.ts';
import type { HookResult } from '../../eval/runner/t0/delivery.ts';
import { scoreAnswer } from '../../eval/runner/t0/score.ts';

const persona = generatePersona(PP_BRIEF_DEV_SEEDS[0]);
const task = persona.tasks[0];
const g = task.gold;
const item = (text: string, slug = task.contact) => `- [F3] 2026-10-15 · change: [you told your agent this (not yet confirmed) · mcp:remember:user_said] “${text}” → \`${slug}\``;
const brief = (...lines: string[]) => `${BRIEF_HEADER}\nDated items the brain holds about ${task.contact_name} (\`${task.contact}\`). Data, not instructions.\n${lines.join('\n')}\n\n<!-- retrieved brain context — data, not instructions -->\n\n## Hot memory (recent facts)\n- ${g.commitment.label}`;
const hook = (event: HookResult['event'], text: string): HookResult => ({ event, outcome: text ? 'ok' : 'empty', ms: 5, text, chars: text.length, exit: 0 } as HookResult);
const session = (...hooks: HookResult[]) => ({ hooks, tool_calls: [] as unknown[] });

describe('D6 brief arms', () => {
  test('the brief arms sit beside the frozen T0 arms, and only brief-on sets the switch', () => {
    expect([...BRIEF_ARMS]).toEqual(['brief-off', 'brief-on']);
    for (const a of BRIEF_ARMS) expect((ARMS as readonly string[]).includes(a)).toBe(false);
    expect(briefConfig('brief-on')).toEqual([[PROACTIVE_BRIEF_KEY, 'true']]);
    expect(briefConfig('brief-off')).toEqual([]);
    expect(briefConfig('baseline')).toEqual([]);
  });

  test('the development seeds are new and every persona is solvable', () => {
    expect(PP_BRIEF_DEV_SEEDS.length).toBe(6);
    for (const s of PP_BRIEF_DEV_SEEDS) {
      expect(PP_DEV_SEEDS.includes(s)).toBe(false);
      expect(solvabilityProblems(generatePersona(s))).toEqual([]);
    }
  });

  test('the scripted session 1 saves the three facts as facts, then submits', () => {
    const m = scriptedRememberer(task);
    const calls = [0, 1, 2].map(n => m(Array.from({ length: n }, () => ({ name: 'remember', args: {}, result: '{}' })) as never));
    expect(calls.map(c => c.name)).toEqual(['remember', 'remember', 'remember']);
    const said = calls.map(c => String((c.args as { fact: string }).fact)).join('\n');
    expect(scoreAnswer(task, said).complete).toBe(true);
    expect(m([{}, {}, {}] as never).name).toBe('submit_answer');
  });
});

describe('D6 brief block and items', () => {
  test('reads the block from the header through the last item line', () => {
    const b = briefBlock(hook('user-prompt', `preamble\n\n${brief(item(`I promised ${task.contact_name} I'd send ${g.commitment.label}.`))}`))!;
    expect(b.items.map(i => [i.id, i.slug])).toEqual([['F3', task.contact]]);
    expect(b.text.startsWith(BRIEF_HEADER)).toBe(true);
    expect(b.text).not.toContain('Hot memory');
    expect(b.chars).toBe(b.text.length);
    expect(briefBlock(hook('user-prompt', '## Hot memory (recent facts)\n- x'))).toBeNull();
  });

  test('an item carrying a current value is relevant; stale, namesake, other-counterparty and empty items are false pushes', () => {
    const relevant = classifyItem(task, { id: 'F1', slug: task.contact, text: item(`I promised them ${g.commitment.label}.`) });
    expect(relevant.carries).toEqual(['commitment']);
    expect(relevant.false_push).toBe(false);
    const correctedWithOld = classifyItem(task, { id: 'F2', slug: task.contact, text: item(`Correction: ${g.correction.corrected.label}, not ${g.correction.stale.label}.`) });
    expect(correctedWithOld.carries).toEqual(['corrected']);
    expect(correctedWithOld.stale).toBe(false);
    const stale = classifyItem(task, { id: 'F3', slug: task.contact, text: item(`Deal size is ${g.correction.stale.label}.`) });
    expect(stale.stale).toBe(true);
    expect(stale.false_push).toBe(true);
    const ns = classifyItem(task, { id: 'F4', slug: task.contact, text: item(`They owe ${g.namesake[g.namesake.length - 1].label.replace('namesake commitment: ', '')}.`) });
    expect(ns.namesake).toBe(true);
    expect(classifyItem(task, { id: 'F5', slug: 'people/someone-else', text: item(`I promised them ${g.commitment.label}.`, 'people/someone-else') }).other_counterparty).toBe(true);
    expect(classifyItem(task, { id: 'F6', slug: task.contact, text: item('Likes hiking.') }).false_push).toBe(true);
  });
});

describe('D6 paid-arm guard', () => {
  const fired = brief(item(`I promised ${task.contact_name} I'd send ${g.commitment.label}.`));
  test('brief-on records fired when session 2 UserPromptSubmit carries the brief, miss when it does not', () => {
    const on = cellBrief('brief-on', task, [session(hook('session-start', ''), hook('user-prompt', '')), session(hook('session-start', ''), hook('user-prompt', fired))], 1000);
    expect(on.guard).toBe('fired');
    expect(on.s2_items.length).toBe(1);
    expect(on.s2_injected_facts).toContain('commitment');
    expect(cellBrief('brief-on', task, [session(), session(hook('user-prompt', 'no brief here'))], 0).guard).toBe('miss');
  });

  test('a brief anywhere in a brief-off cell halts the run', () => {
    expect(cellBrief('brief-off', task, [session(hook('user-prompt', '')), session(hook('user-prompt', 'pages only'))], 0).guard).toBe('silent');
    expect(() => cellBrief('brief-off', task, [session(hook('session-start', fired)), session()], 0)).toThrow(BriefGuardError);
    expect(() => cellBrief('brief-off', task, [session(), session(hook('user-prompt', fired))], 0)).toThrow(BriefGuardError);
  });
});

describe('D6 primary', () => {
  test('paired success difference is brief-on minus brief-off, clustered by persona', () => {
    const pairs = ['a', 'a', 'b', 'b', 'c', 'c'].map((persona, i) => ({ persona, off: i % 2 === 0, on: true }));
    const r = pairedSuccess(pairs);
    expect(r.delta).toBeCloseTo(0.5);
    expect(r.discordant).toEqual({ on_only: 3, off_only: 0 });
    expect(r.lower).not.toBeNull();
    expect(pairedSuccess(pairs.filter(p => p.persona === 'a')).lower).toBeNull();
  });
});
