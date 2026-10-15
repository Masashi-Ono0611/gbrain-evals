# Preregistration: the proactive brief on Cat 40 family P, development phase v2 (wave 5 D6 redesign)

**Status: draft. No cell may run.** The draft was committed on October 15, 2026 (Pacific). It is frozen by the commit
that fills in [the release under test](#the-release-under-test-filled-in-when-it-ships) in this file and in
`BRIEF_V2_RELEASE` and `BRIEF_V2_EXTRA_CONFIG` (`eval/runner/t0/brief.ts`). That commit lands after gbrain ships the
brief's page-edit source, which another lane is building now, and before any paid cell. Until the pin is filled in,
the runner refuses paid v2 cells. After the freezing commit, every change is an amendment, appended at the bottom with
its reason and committed before any cell it governs.

This is a redesign written after seeing the results of the
[first development run](2026-10-14-proactive-brief-dev.md) (preregistration `6aa12098`). Garry approved it on October
15, 2026. That run's verdict stands: no improvement signal (both arms finished 70 of 72 paired tasks). Its result was
null because hot memory delivered the session-1 facts to both arms and the brief only pushed one of them again. This
design builds tasks where hot memory does not carry the needed fact.

It is still development evidence only. It does not decide whether the brief ships on by default. Under the plan's
wave 5 exit rule, only D6's sealed verdict can make that decision. The sealed seed stays out of scope: nothing here
mints, generates or reads sealed material.

Code: `eval/runner/t0-program-primary.ts` (the T0 carrier with the brief arms and the v2 conditions),
`eval/runner/t0/brief.ts` (conditions, crowd facts, hot-memory control, save path, analysis `summarizeBriefV2`),
`eval/runner/cat40/gbrain-arm.ts` (`GbrainSlot.backdateFactsSince`), and `eval/generators/program-primary-gen.ts`
(`PP_BRIEF_V2_DEV_SEEDS`, `PP_BRIEF_V2_SESSION2_DAY`). Tests: `test/eval/t0-brief.test.ts`.

## The question

The facts the task needs no longer reach the agent through hot memory, because they are too old or crowded out by
newer facts. In that situation, do agents finish meeting-prep and reply tasks correctly more often with gbrain's
"Before you start" brief on than with it off?

## What is known before any spend

These findings come from hermetic runs on October 15 ($0, scripted models, keyless brains) against gbrain v0.60.240.0
(`1355f32f`), the release the first run used. They shape the design, so they are frozen here.

1. **How hot memory chooses facts.** The UserPromptSubmit and SessionStart "Hot memory (recent facts)" block reads
   facts whose `created_at` is within the last 24 hours. It fetches the 30 newest and shows the top 10 after
   collapsing duplicates (`src/core/facts/meta-hook.ts`, `listFactsSince`). gbrain reads `Date.now()` and has no clock
   parameter, so the harness simulates elapsed time by moving timestamps.
2. **The aged condition removes the facts from hot memory.** After session 1, the harness backdated the facts session
   1 created to at least 72 hours before the cell. Hot memory then carried none of the three needed facts in 4 of 4
   aged cells. The brief still fired in 2 of 2 brief-on aged cells, because the brief has no time window. It carried
   the newest fact about the contact.
3. **The crowded condition pushes the facts out of hot memory.** After session 1, the harness saved 40 newer facts
   about other people through `remember`. Hot memory then carried none of the needed facts in 4 of 4 crowded cells,
   and a separate probe showed it filled with 10 of the newer facts. The brief fired in 2 of 2 brief-on crowded cells.
4. **The facts stay on the contact's page.** `remember` writes each fact into the entity page's `## Facts` fence
   (checked: after one `remember`, `get_page` on the contact returns the fact). The UserPromptSubmit hook names the
   contact's page in both arms ("Brain pages mentioned this turn"). So a reader that opens that page sees every saved
   fact whatever the brief switch says, and a reader that edited the page in session 1 left the facts there too. The
   brief can only change the outcome for a reader that does not open the page. It can also save the tool calls and
   tokens needed to find the facts.
5. **What the brief carries.** In this release, per counterparty, the brief carries the top open loop, then the newest
   fact, then more loops, with at most 3 items. Without loops it carries one fact, while each task needs three facts
   (the commitment, the moved date and the correction).
6. **Loops from mail or calendar cannot reach the pushed brief in this release.** Commitments that the mail extractor
   finds are written as private facts (`src/core/google/loops-extract.ts`, `visibility: 'private'`). The push brief
   is world-only: a loop is admitted only through a world-visible fact. Detector loops have no fact at all. The calendar
   trigger also needs a Google-kind source synced within 24 hours. So this draft has no loop condition. At the pin,
   the [loop presence check](#loop-presence-check-at-the-pin) decides whether one can be added.
7. **Save path.** In the first run, all 14 brief-on misses were Sonnet 5.5 sessions that saved by editing pages and
   never called `remember`, which left the brief no fact to push. The release this draft waits for adds a page-edit
   source to the brief, off by default. The brief-on arm turns it on.

**Prediction.** Finding 4 still makes a small or null difference in task success likely. Readers that open the
contact's page, or search, find the facts in both arms. In the first run, 143 of 144 session-2 cells called `get_page`,
`search`, `recall`, `entity` or `get_chunks`.
Effects are more likely in session-2 tool calls and input tokens than in success. The decision rule below is written
so that a null result or a token saving cannot read as a gain in success.

## Workload (frozen)

- Generator `program-primary-v1`, unchanged: one brain of 73 pages and 4 tasks per persona, with the same two
  sessions as the first run. In session 1 the user reports a call (a commitment, a moved meeting and a correction) and
  asks the agent to update the brain. Session 2 asks for meeting prep or a reply that names none of the three facts.
- **New development seeds:** 20261211, 20261213, 20261214, 20261215, 20261216, 20261217 (`PP_BRIEF_V2_DEV_SEEDS`).
  These are the first six seeds from 20261211 that render, pass the solvability check, and put every moved meeting on
  or after October 19, two days after session 2. No earlier run used them. That gives 24 tasks: 12 prep and 12 reply.
- **Session days:** session 1 is on October 14 in the world, and session 2 on October 17 (`PP_BRIEF_V2_SESSION2_DAY`).
- **Conditions,** assigned by task. Each persona's first reply task and first prep task are **aged**; its other two
  tasks are **crowded** (`briefCondition`). That gives 12 aged and 12 crowded tasks, with 6 prep and 6 reply in each.
  - **Aged:** after session 1 the server stops. Every fact created since the cell's restore gets its `created_at` set,
    and its `valid_from` when that is newer, to noon Pacific on October 14, or to 72 hours before the cell if that is
    earlier (`agedFactsAt`). This happens in one statement with triggers off, because gbrain's managed-writer trigger
    refuses operator writes to `facts` (`GbrainSlot.backdateFactsSince`). Page writes are untouched. Then session 2
    starts in a new server process.
  - **Crowded:** after session 1 the harness saves 40 facts (`CROWD_FACTS`) through the server's own `remember`
    tool, with provenance "user, a later session" and `content_origin: user_said`. Each fact is about a person in
    the persona's brain other than the task's contact and anyone sharing the contact's first name (the namesake). The
    facts contain no number or date and match none of the task's gold values (`crowdFacts`, tested). Then session 2
    starts in a new server process.

## The release under test (filled in when it ships)

- gbrain version and commit: **to be pinned.** This is the first release containing the brief's page-edit source.
  It is recorded here and in `BRIEF_V2_RELEASE`, and built with tree and CLI-version verification, surface `starter`.
- Page-edit source switch: **to be pinned.** It goes in `BRIEF_V2_EXTRA_CONFIG` and only brief-on sets it.
- When the pin lands, the hermetic slice reruns on the pinned release (one persona, both arms, $0). It must show the
  hot-memory control holding, the brief firing in brief-on cells and staying silent in brief-off cells. Its record
  goes into the freezing commit's message or a file under the results directory added after the freezing commit.

### Loop presence check at the pin

On the pinned release, and before the freezing commit, one hermetic or minimal check answers one question. Can a
commitment that gbrain's own pipeline derives from a mail or calendar fixture appear as a loop item in a pushed
(world-only) brief? If it cannot, the loop condition is recorded as not runnable on that release, with the reason. If
it can, a loop condition is added only by a dated amendment. The amendment sets the condition's tasks, budget and
analysis before any of its cells, and the loop condition never joins this design's primary.

## Arms (frozen)

| Arm | What differs |
|---|---|
| `brief-off` | Nothing is set: the release defaults, with the brief off and the page-edit source off. |
| `brief-on` | After every snapshot restore and before session 1, `context.proactive_brief` is set to `true` and the page-edit source switch is turned on. Both stay on through session 2. |

Everything else is the T0 carrier, unchanged from the first run: the snapshot, the native-event delivery contract
`t0-delivery-v1`, the stdio MCP tools, 20 turns per session and the system prompt. Every task runs once in each arm
for each reader (paired), with 1 repeat.

## Readers and settings (frozen)

`claude-opus-5-5`, `claude-sonnet-5-5` and `gpt-6.1-sol`, the newest Opus, Sonnet and GPT models, with provider
defaults. If a newer model in any of these families exists on the day of the freezing commit, the commit names it and
says why. No Fable, no older generation and no gpt-5.4-mini run. Results are reported for each reader, and every
reader whose brief-off arm is at 24 of 24 is named as a ceiling.

## Scorer (frozen)

The primary scorer is `t0-score-v3`, the same as the first run, and `t0-score-v2` is reported as a secondary. A cell
succeeds when the primary scorer does not fail it.

## Size (frozen)

6 personas × 4 tasks × 3 readers × 2 arms × 1 repeat = 144 cells. That is 72 pairs: 36 aged and 36 crowded, clustered
by persona (6 clusters).

## Primary measure and decision rule (frozen)

**Primary:** the paired difference in end-to-end task success, brief-on minus brief-off, over the task × reader pairs
of both conditions, pooled across the three readers. It comes with a persona-clustered 95% interval (`pairedSuccess`,
t on 5 degrees of freedom). Each condition is also reported separately, and neither is a co-primary.

**Development signal.** The run is labelled "improvement signal (development evidence only)" only when all six checks
hold, and "no improvement signal (development evidence only)" otherwise (`summarizeBriefV2`):

1. the pooled paired success difference has a 95% lower bound above 0;
2. **the hot-memory control holds:** in each condition, at most 10% of cells (both arms) carry any needed fact in
   session 2's hot-memory lines. If more do, the condition did not remove the fact from hot memory and the run cannot
   answer the question;
3. **the paid-arm guard holds:** no brief-off cell shows a brief (the run halts otherwise), and among brief-on cells
   whose session 1 saved anything (`remember` or a page write), the brief fails to fire in at most 10%. Brief-on cells
   whose session 1 saved nothing are reported separately, because the brain then holds nothing to push;
4. attention: no session-2 brief block exceeds 1,800 characters;
5. false pushes: at most 0.05 false-push items per brief-on session;
6. no rise in confident-wrong: brief-on has no more confident-wrong cells than brief-off.

Checks 4 to 6 are the plan's exit bar. Uptake, fewer tool calls or fewer tokens never satisfy the rule.

**What each label allows.** "Improvement signal" means the design may go to the sealed phase unchanged, under its own
preregistration and custody. "No improvement signal" means the result is reported, and whether D6 continues is
Garry's decision. Neither label changes the release default.

## Diagnostics (frozen definitions; for each arm, condition and reader)

- Everything the first run reported, with the same definitions: the guard, brief characters, item classes, false
  pushes per session and per day, uptake with the paired brief-off rate for the same facts, opportunity recall of the
  brief and of all injected context, the confident-wrong rate, session-2 tool calls and input tokens per task, cell
  input tokens, dollars per cell, and capture.
- **The hot-memory control:** for each cell, which needed facts (by gold matcher) appear in session 2's hot-memory
  lines, across all hooks. Counts are given per condition and separately for brief-off cells.
- **Save path:** session 1's save path, which is `remember` if any `remember` call was made, else `page` if a
  `put_page` or `edit_page` call was made, else `none`. The brief's firing rate is reported for each save path.
- **Setup records:** for each cell, the backdated fact ids and their timestamp (aged), or the count of crowd facts
  saved and refused (crowded).

## Budget and stopping (frozen)

- A new budget ledger is capped at $35 for this phase, so no earlier ledger's balance is used. The preflight estimate
  is the first run's measured mean cost per cell plus about 10%: Opus $0.34, Sonnet $0.18, gpt-6.1-sol $0.10, about
  $30 for 144 cells. The ledger enforces the real cap.
- Paid cells refuse to start without `--preregistration` naming this file committed and on `origin`. They also refuse
  until `BRIEF_V2_RELEASE` is pinned, and on any build other than the pinned commit.
- Harness errors follow the same rules as the first run. The same command runs once more to fill missing cells.
  Pairs with a missing side drop out of the primary. If the cap stops the run, the analysis covers the complete pairs
  and the report says it was truncated. There is no other stopping, peeking or re-running, and the analysis runs once
  after the last cell.

## What is reported

The development record (`docs/benchmarks/2026-10-15-proactive-brief-dev-v2.md` and the run directory
`docs/benchmarks/2026-10-15-proactive-brief-dev-v2/`) reports:

- the primary with its interval and discordant pairs, and the label with each check;
- each condition, each reader with ceilings, and prep and reply separately;
- the hot-memory control and firing by save path;
- every diagnostic, with raw counts;
- spend from the ledger with the budget run id;
- `t0-score-v2` as a secondary;
- the hermetic slice on the pinned release;
- the loop presence check's outcome.

Machine-local paths are scrubbed from committed files.

## Amendments

None.
