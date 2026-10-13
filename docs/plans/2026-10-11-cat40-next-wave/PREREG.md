# Cat 40 next wave: confirmation preregistration (DRAFT)

Status: **draft, not final.** Written 2026-10-13, after development closed and before any confirmation world is
generated and before any confirmation cell runs. Three decisions below (D1-D3) are open. The document becomes final
when a commit records the answers, with the date and who decided, under "Decisions" and removes this status line.
After that the executor only appends values that don't exist yet (world digests, VM names, ledger run ids, the
harness SHA) under "Recorded before cells". Any other change after the first counted cell needs a dated amendment
that gives its reason.

Plan: `docs/plans/2026-10-11-cat40-next-wave/PLAN.md` on `plan/cat40-next-wave` (`f0b8418b`), section "Development
and confirmation". Development records, all on `capy/cat40-dev-harness` and merged into this branch:
`docs/benchmarks/2026-10-13-cat40-dev-gate/` (d4b), `2026-10-13-cat40-dev-round-1/`, `2026-10-13-cat40-dev-round-2/`
and `2026-10-13-cat40-dev-d1b/`.

## Authorization

- Confirmation budget about **$3,400** including the baseline arm (Garry, gate rev 2, relayed through GBRA-40,
  2026-10-12).
- **Worlds.** Plan Option B: 40 tasks per family on a fresh seed and on a new sealed seed generated on Garry's Mac
  (gate rev 2, accepted). That option can't be built as written; see D1.
- **Models.** The newest model per family; no Fable in counted cells (project rule, 2026-10-07).

## What runs

| | Value |
|---|---|
| Wave build | gbrain `capy/cat40-next-part1` @ `e67dcc9f88c07234710e30ef69d2d8bf5071fe3e` (v0.60.189.0). Its `src/` tree is identical to the development build `a798de1f966d`: the two commits since then touch only `scripts/`, tests and goldens. Measured path set: the 53 `src/` files that differ from the merge base (`git diff --name-only 09d21554d e67dcc9f8 -- src`, list SHA-256 `0763e92df94a…`). |
| Baseline build | gbrain `09d21554d7ab75cc5643a7f5a0e7f163aa4dae5b`. This is the wave's merge base with master (master PR #6566, 2026-10-13), and `0460af28` is its ancestor, as the plan requires. It gets no wave keys. |
| Harness | gbrain-evals `capy/cat40-next-prereg`: `main` (`1ad2370c`) with `capy/cat40-dev-harness` (`5f4d1cea`) merged in, plus the executor commits listed under "Freeze rules". The SHA is recorded before cells. |
| Arms | `gbrain-wave`, `gbrain-baseline`, `fs` (counted); `oracle` (world check only). |
| Models | `claude-opus-5-5`, `claude-sonnet-5-5`, `gpt-6.1-sol`. |
| Judge | `gpt-6.1-sol`. |
| Fixed settings | Hard tool limits, 16-turn cap, repeat 1, concurrency 10, 5 gbrain slots per world and build, `--no-pglite-analyze`, `--transcripts` (whole results). Every setting not named here is the same for every arm and equal to development rounds 1-2. |

### Arm configs

- **gbrain-wave.** `--gbrain-config` is exactly the development all-on list:
  `entity.names_references=true,entity.record_types=contract,amendment,entity.row_page_status=true,search.long_page_unit=section,search.long_page_min_chars=20000,mcp.instructions_governing_rule=in_effect`.
  F5's build key is set by the inclusion rule below. Slots are built from the wave build.
- **gbrain-baseline.** No `--gbrain-config` and no build config. Slots are built from the baseline build. The
  baseline lacks every wave key, F3's `entity.row_page_status` included, so it gets none.
- **fs** and **oracle** are as in #93 (`2026-10-10-model-ladder-hard-confirmation`).
- **Checks before paid cells.** Each recipe is verified by slot restore, pack resolution and config readback; the
  readback and the served-instructions hash are recorded per arm. Development's all-on hash was `3bb1d6aafd23`; the
  wave arm's hash is recorded before cells, since it can differ only if F5's state changes the served text.

### F5 inclusion (`mentions.owner_phrases`)

The plan decides it two ways: the d1b gate on development data, and precision of 0.85 or more (Wilson 95% lower
bound) on a labeled sample from Garry's own brain, run on his Mac through GBRA-40. If either fails, the wave arm runs
with `mentions.owner_phrases` off. That is decided and recorded before any cell, and the plan's packaging fallback
applies at merge.

- **d1b (2026-10-13): fails.** The seen share of needed owner-phrase documents is +0.2 pp [-3.3, +3.6] for F5 alone
  against the all-off control, with cells 24 better and 23 worse. See `2026-10-13-cat40-dev-d1b/`.
- **Precision check:** not run. It is pending Garry's yes.
- **Default under the plan:** the wave arm runs F5 off. Slots are built without `--gbrain-build-config`, so no F5-on
  family is needed. Because d1b already fails, the precision result can't turn F5 on.
- **Open:** D2 asks whether that default stands. If Garry overrides d1b, F5 is on only when the Mac precision check
  has run and passed before the wave slots are built. If it hasn't run by then, F5 stays off and the wave arm runs
  without it. Nothing waits on it.

## Models

`bun scripts/model-freshness.ts --models anthropic:claude-opus-5-5,anthropic:claude-sonnet-5-5,openai:gpt-6.1-sol`
was run on 2026-10-13. It read both providers' live model lists and exited 0 with no warnings: the newest Opus is
`claude-opus-5-5`, the newest Sonnet `claude-sonnet-5-5` and the newest GPT `gpt-6.1-sol`. No newer frontier model
exists. Fable 5.1 is listed as smoke-only and is not used. The run is repeated on the day the first counted cell
runs. If a newer counted-family model exists then, the run stops and the change goes into this document before any
cell runs (project rule).

## Worlds

### Feasibility finding: the public generator can't produce 40 tasks per family

Generating 4k worlds with the frozen knobs (`docs/benchmarks/cat40-hard/knobs.frozen.json`, SHA-256 `53c5be3c…`) and
only `tasks_per_family` raised, on scratch seeds 20261099 (smoke) and 20261005 (calibration, already public), gave:

| tasks_per_family | Result |
|---|---|
| 20 to 23 | generated |
| 24 | generated on 20261099; failed an H3 invariant on 20261005 |
| 25 and 30 | "ran out of person names" |
| 35 and 40 | "ran out of unique values" |

The knob is valid (1-99 in `schema.ts`), but at this world size the generator's name and value pools run out
before 24-25 tasks per family. So Option B needs a world-shaping generator change: a new generator version, new pools
and an equivalent change in the sealed generator, which no agent may read. `knobs.confirm-40.json` on this branch is
the frozen file with only `tasks_per_family: 40`. It records what B would use, and it fails to generate. No
confirmation seed was generated for this check.

### Proposed design (D1): two fresh seeds per generator, 100 tasks each

This gives the same number of tasks per generator as Option B (200) and the same cell cost, with no generator change:

- **Public generator** (`model-ladder-hard-v2`, `--scale large`, frozen knobs, 20 tasks per family): fresh seeds
  **20261041** and **20261051**. Neither was ever generated; they continue the 10-step sequence after 20261021
  (#93's M) and 20261031 (the d4b dev seed). The 4k base and the 50k world are generated only after this document is
  final.
- **Sealed generator** (`hard-sealed-v2`, frozen knobs): two new private seeds, generated on Garry's Mac through
  GBRA-40 with the same custody as #93's S. The seeds never leave the Mac and are never printed; world files reach one
  owner-custody VM only. With D1 as proposed, the custody check below isn't needed.
- **Fallback seed.** If a seed fails generation or validation, that seed plus 1,000 is used (for example 20262041)
  and recorded. Nothing else changes.

**Alternatives for D1:**

- **(b) Option A,** repeat 2 at 20 tasks, one world per generator. It forecasts ±4.2 pp and costs about $2,778 plus
  $55 for slots.
- **(c) Option B as planned.** This first needs a generator change to the public pools (a new version, run through
  `validate.ts`) and a precondition on the custody side.

**Option B precondition (applies only if (c) is chosen).** Before the sealed seed is generated, the custody owner
confirms on the Mac that the sealed generator accepts `tasks_per_family: 40` with the frozen knobs and generates and
validates at that size. Otherwise confirmation does not start.

Each world is reported with its H4 variant and `+long` mix next to #93's M and S. The README states that these are
new worlds.

## Gates before counted cells (per world)

1. The world validates against its generator (`validate.ts` for public worlds; the sealed validator on the custody VM).
2. Oracle on all tasks with the three models: pooled success ≥ 95%. Below that, stop and report, and run no counted
   cell on that world.
3. Every gbrain slot, for both builds, passes the write probe, the restore probe and the fail-closed rerank probe,
   with 0 queued effects at snapshot. Config readback for both recipes matches the lists above, and an F5-off wave
   slot reports 0 owner-phrase links.
4. Model freshness is rerun (see Models).
5. The projected spend plus 15% fits the world's ledger.

## Endpoints

All intervals are percentile bootstraps over tasks with 10,000 resamples and seed 1. Every cell of a task (all three
models, and both seeds' tasks kept separate) moves together, which is #93's convention. Development results are never
pooled with confirmation results.

### Primary: Δ wave − fs, per generator

Δ_G is the pooled gbrain-wave − fs success rate: the mean over the three models of each model's wave rate minus its
fs rate, on the same tasks. It is computed over all of generator G's tasks (both seeds under D1) and also reported per
world. The wording rules are #93's:

- **Parity** only when the lower bound is above −3 pp; otherwise "not distinguishable", with the point estimate.
- **Ahead** only when the lower bound is above 0.
- **The wave holds gbrain's place against files** only if Δ_public ≥ 0 and Δ_sealed ≥ 0 (point estimates).
- **If either is below 0,** the result is published as it is, and #93's statement applies: stop claiming that gbrain
  beats files on hard company questions.

### Secondary (reported for every world and pooled per generator)

1. **Wave − baseline success,** same paired bootstrap.
2. **Wrong values, wave − baseline.** The wrong-value rate is cells with `score.said_wrong`, which names a listed wrong
   value, over all cells. Wrong submitted cells (submitted and not successful) are reported separately, with the same
   denominator and also over submitted cells. Non-submission and turn-cap stops are reported beside both, so fewer
   wrong answers can't come from more non-answers.
   - **Test:** paired by task and model.
   - **Minimum effect (D3):** pooled over both generators, wave − baseline ≤ −2.0 pp with the 95% upper bound below 0.
     Development showed −4.5 pp [−7.3, −1.7] for all-on against the all-off control on M.
3. **Per family,** wave vs baseline and wave vs fs. H4 is called out and stratified by the `+long` variants.
4. **Per model,** with the people-facing models first. Sol is a ceiling for wrong values: it had 1 such cell in 200
   for control on M in development.
5. **Sol wrong values (round 2 watch item).** Sol's wrong-value cells under wave vs baseline per world, with the
   paired test. Development had 4 under all-on vs 1 under control, pooled. This is reported, not a gate, and it is
   flagged if the wave exceeds the baseline by 3 or more cells pooled over the worlds.
6. **Draft-first firing and harm,** using `draft_first.py`'s settled definition. An H4 item is draft-led when the
   account's contract and amendment documents that reference it by name, code or nickname, ordered newest document
   date first with ties by id, lead with a `DRAFT` amendment.
   - **Firing:** `entity` names rows whose records list a draft ahead of every executed record, per model and `+long`
     stratum.
   - **Harm:** wave vs baseline wrong-value cells and successes on draft-led tasks, and on the cells served a
     draft-first row.
   - **Expected sign:** firing is positive, since config-only worlds give drafts no `page_status`. Harm is expected to
     be ≤ 0 (development: 0 vs 12 wrong values over 69 served cells).
7. **Firing counters** per arm (`firing.ts`), names-call p50/p99, cost per successful task, median seconds per cell,
   and the rerank check.

## Budget and stop rule

Priced from the plan's per-arm costs at 100 tasks (gbrain about $198, fs about $286, oracle about $25) times #93's
ledger rate of 1.108:

| Item | Per world | 4 worlds (D1) |
|---|---|---|
| gbrain-wave | $219 | $877 |
| gbrain-baseline | $219 | $877 |
| fs | $317 | $1,268 |
| oracle | $28 | $111 |
| Slot builds, 5 slots: wave and baseline per world (public about $13.68 each, sealed about $17) | | about $123 |
| **Total** | | **about $3,256** |

- **Approved:** $3,400, which leaves about $144 for ordinary retries. The plan priced Option B at about $3,190; D1
  costs the same per cell plus four more slot builds.
- **Ledgers:** one per machine. `.budget/cat40-next-confirm-public.sqlite` (the two public worlds) and
  `.budget/cat40-next-confirm-sealed.sqlite` (the custody VM), each with a $1,700 program cap.
- **Per-arm caps** (`--budget-usd`, 1.15 × price): gbrain arms $252, fs $364 (#93's M fs cost $334 priced, so the cap
  holds it), oracle $32.
- **Stop rule:**
  - An arm that reaches its cap stops. Its world's endpoints are not computed, and the shortfall is escalated to
    Garry through GBRA-40 before any more money is spent.
  - If a harness fault voids an arm, confirmation stops and the rerun is escalated. The reserve doesn't fit a
    full-arm rerun.
  - After each world's first counted arm, the ledger projection plus 10% is checked against the cap. A projection
    over the cap stops the run and escalates it.
  - No cell is rerun, except harness or provider errors covered by the runner's existing retry rules.

## Freeze rules

- **Seeds.** Public: 20261041 and 20261051 under D1, with the +1,000 fallback rule. Sealed: private, on the Mac.
  Bootstrap seed: 1.
- **Knobs.** `knobs.frozen.json` (SHA-256 `53c5be3c…`) for every world under D1.
- **Scorer.** `eval/runner/cat40/score-hard.ts` and `judge-hard.ts` at the recorded harness SHA, judge `gpt-6.1-sol`.
  The analysis scripts are frozen at that SHA too: `summarize_round.py`'s bootstrap, `draft_first.py` and `firing.ts`.
- **Harness.** The executor may add only these commits before cells:
  - registering the confirmation seeds in `HARD_SEEDS`, as #93 did;
  - registering the confirmation program steps (baseline and wave arms, one ledger per machine, the oracle gate,
    per-arm caps);
  - the confirmation ledger caps.

  None of them may change a world, a score or an arm setting. The SHA and a freeze check of the frozen files are
  recorded below.
- **Drift note.** Counted steps run with
  `--accept-freeze-drift "PREREG.md (cat40-next-wave): harness <sha> preregistered; drift is confirmation seed and program-step registration on the dev harness (scripted gbrain agent, whole-result transcripts), neither of which changes a model cell (<date>)"`.
  The SHA and date are filled in at the executor's freeze check, and nothing else in the note changes.
- **Builds.** Wave `e67dcc9f8` and baseline `09d21554d`. Component retention is frozen on development data, and no
  component is selected using a confirmation world. If master is merged into the wave after confirmation and touches
  the measured path set, the decision record needs a written no-effect argument or a re-confirmation (plan).
- After confirmation, no gbrain change is tuned on these worlds' tasks.

## Hygiene

- No development agent has read the sealed generator's code or any sealed output.
- Sealed seeds never leave Garry's Mac. Sealed worlds cross one Capy cloud machine in transit, are deleted there once
  the custody VM holds them, and never touch Capy Drive.
- Each VM is destroyed after its outputs (results, transcripts, receipts; no world documents for sealed worlds) are
  copied.
- Reports name counts, ids, models, tools and document types only. No entity names or values appear.

## Decisions (open)

- **D1, worlds.** Option B can't be generated (see the feasibility finding). Choose one:
  - **(a)** Two fresh seeds per generator at 100 tasks each. Same cell count and interval as B, no generator change,
    about $3,256. This is the proposal.
  - **(b)** Option A: repeat 2, one world per generator, ±4.2 pp, about $2,833.
  - **(c)** Change the generator's pools so B builds. That makes a new generator version, needs the equivalent sealed
    change and adds the custody precondition.
- **D2, F5.** The plan default is that F5 is off, because d1b fails. The d1b record also shows that F5's links reach
  agents only through F1's record rows (79 needed-document record rows in round 1 all-on, 0 in f1 without F5). So
  all-on's measured gain may partly depend on F5, and the wave config without F5 was never run as a paid development
  arm. Choose one:
  - Keep the plan default: F5 off, which confirms a config development didn't run.
  - Override d1b and keep the development all-on config. F5 is then on only if the Mac precision check passes before
    the wave slots are built; otherwise it stays off.
  - Run a free replay first, which the plan assigns to the F1 interaction check.
- **D3, wave − baseline wrong-value minimum effect.** Proposed: −2.0 pp pooled, with the upper bound below 0. The
  plan asks for a stated minimum effect and gives no number.

## Recorded before cells

(Appended by the executor once D1-D3 are recorded; no edits above this line after that.)
