# Cat 40 next wave: confirmation preregistration

Written 2026-10-13, after development closed and before any confirmation cell runs. The draft (`fb04c5d0`) set out
decisions D1-D3, and this version records the answers. Once this document is committed, the executor only appends
values that don't exist yet under "Recorded before cells": the wave build SHA, the harness SHA, sealed world digests,
VM names, ledger run ids and the round 3 diagnostic. Any other change after the first counted cell needs a dated
amendment that gives its reason.

Plan: `docs/plans/2026-10-11-cat40-next-wave/PLAN.md` on `plan/cat40-next-wave` (`f0b8418b`), section "Development
and confirmation". Development records, merged into this branch from `capy/cat40-dev-harness`:

- `docs/benchmarks/2026-10-13-cat40-dev-gate/` (d4b)
- `2026-10-13-cat40-dev-round-1/`
- `2026-10-13-cat40-dev-round-2/`
- `2026-10-13-cat40-dev-d1b/`
- `2026-10-13-cat40-dev-round-3/` (declared; it runs before cells)

## Authorization

- Confirmation budget about **$3,400** including the baseline arm (Garry, gate rev 2, relayed through GBRA-40,
  2026-10-12).
- D1-D3 (below) were auto-approved under Garry's standing rule (2026-10-12) and relayed by GBRA-39's parent on
  2026-10-13.
- **Models.** The newest model per family; no Fable in counted cells (project rule, 2026-10-07).

## Decisions

- **D1, worlds: two fresh seeds per generator, 100 tasks each.** Plan Option B (40 tasks per family) can't be built:
  the public generator runs out of person names and unique values above about 23 tasks per family with the frozen
  knobs (feasibility table below). Two seeds per generator keep B's 200 tasks per generator and its cell cost, with no
  generator change. The `tasks_per_family` custody precondition is dropped.
- **D2, F5: off. d1b is not overridden.** F5 failed d1b. Overriding a preregistered gate after seeing its result is a
  one-way door, so the verdict stands. The plan never put numbers on d1b's minimum effect or per-family margin, and
  the verdict doesn't depend on them: the seen share is +0.2 pp [−3.3, +3.6], which fails every reading of "rises".
  The plan's packaging fallback applies, so the wave build is the Part 1 head with F5's commits removed.
- **D3, wrong-value minimum effect:** wave − baseline ≤ −2.0 pp, pooled over both generators, with the 95% upper
  bound below 0.

## What runs

| | Value |
|---|---|
| Wave build | gbrain `capy/cat40-next-part1` at the head with F5's commits removed (the plan's fallback, made by the Part 1 implementer). The SHA, its version and its `src/` difference from `e67dcc9f88c07234710e30ef69d2d8bf5071fe3e` are recorded below before any cell. That difference must be F5's removal plus at most master merges. Any other `src/` change needs a dated note here first. Reference: `e67dcc9f8` (v0.60.189.0), whose `src/` is identical to the development build `a798de1f966d`. |
| Baseline build | gbrain `09d21554d7ab75cc5643a7f5a0e7f163aa4dae5b`. This is the wave's merge base with master (PR #6566, 2026-10-13), and `0460af28` is its ancestor, as the plan requires. It gets no wave keys. If the F5-removed head has a different merge base with master, the baseline stays `09d21554d`, and the wave's added master changes are listed with the wave SHA. |
| Harness | gbrain-evals `capy/cat40-next-prereg`: `main` (`1ad2370c`) with `capy/cat40-dev-harness` merged in, plus the executor commits listed under "Freeze rules". The SHA is recorded below before cells. |
| Arms | `gbrain-wave`, `gbrain-baseline`, `fs` (counted); `oracle` (world check only). |
| Models | `claude-opus-5-5`, `claude-sonnet-5-5`, `gpt-6.1-sol`. |
| Judge | `gpt-6.1-sol`. |
| Tasks | Every task in each world: 100 (H1-H5, 20 per family), repeat 1. |
| Fixed settings | Hard tool limits, 16-turn cap, concurrency 10, 5 gbrain slots per world and build, `--no-pglite-analyze`, `--transcripts` (whole results). Every setting not named here is the same for every arm and equal to development rounds 1-2. |

### Arm configs

- **gbrain-wave.** `--gbrain-config` is exactly the development all-on list:
  `entity.names_references=true,entity.record_types=contract,amendment,entity.row_page_status=true,search.long_page_unit=section,search.long_page_min_chars=20000,mcp.instructions_governing_rule=in_effect`.
  There is no build config. **F5 (`mentions.owner_phrases`) is off** (D2), and the F5-removed build doesn't have the
  key. Slots are built from the wave build.
- **gbrain-baseline.** No `--gbrain-config` and no build config. Slots are built from the baseline build.
- **fs** and **oracle** are as in #93 (`2026-10-10-model-ladder-hard-confirmation`).
- **Checks before paid cells.** Each recipe is verified by slot restore, pack resolution and config readback. The
  readback and the served-instructions hash are recorded per arm.

## Models

`bun scripts/model-freshness.ts --models anthropic:claude-opus-5-5,anthropic:claude-sonnet-5-5,openai:gpt-6.1-sol`
was run on 2026-10-13. It read both providers' live model lists and exited 0 with no warnings: the newest Opus is
`claude-opus-5-5`, the newest Sonnet `claude-sonnet-5-5` and the newest GPT `gpt-6.1-sol`. No newer frontier model
exists. Fable 5.1 is smoke-only and is not used. The check is rerun on the day the first counted cell runs. If a newer
counted-family model exists then, the run stops and the change goes into this document before any cell (project
rule).

## Worlds

### Feasibility of Option B (why D1 changed it)

Generating 4k worlds with the frozen knobs (`docs/benchmarks/cat40-hard/knobs.frozen.json`, SHA-256 `53c5be3c…`) and
only `tasks_per_family` raised, on scratch seeds 20261099 (smoke) and 20261005 (calibration, already public), gave:

| tasks_per_family | Result |
|---|---|
| 20 to 23 | generated |
| 24 | generated on 20261099; failed an H3 invariant on 20261005 |
| 25 and 30 | "ran out of person names" |
| 35 and 40 | "ran out of unique values" |

### Public generator: generated 2026-10-13

- **Settings.** Generator `model-ladder-hard-v2`, `--scale large`, frozen knobs (knob digest `37a16085…`), harness
  `fb04c5d0`. The world-shaping code (`eval/generators/hard/`, `model-ladder-hard.ts`, `model-ladder-gen.ts`, the
  sealed generator) is unchanged since #93's harness `d0057206`. The same commands reproduce #93's M base digest
  `84f0614a…` exactly.
- **Seeds.** D1 named seeds 20261041 and 20261051. Both failed the generator's own invariants at the 4k base (H3
  look-alike rules: 2 failures on 20261041, 1 on 20261051), and no file was written. The draft's fallback rule
  (pushed in `fb04c5d0` before any generation: "that seed plus 1,000") gave **20262041** and **20262051**. Both
  generate and validate.
- **Commands per seed** (no world content was opened; only counts, variants and hashes were read):
  1. `bun eval/generators/model-ladder-gen.ts --mode hard --seed <s> --knobs docs/benchmarks/cat40-hard/knobs.frozen.json --out <dir>/base-4k`
  2. The same command with `--scale large --base-world <dir>/base-4k/world.json --out <dir>/world`
  3. The validation from `scripts/cat40-hard.sh` (`checkHardWorld` plus `hardWorldDigest`).

| World | Seed | 4k base digest | 50k world digest | `world.json` file SHA-256 | Docs | Tasks | H4 tasks with `+long` | H4 items (`+long`) |
|---|---|---|---|---|---|---|---|---|
| P1 | 20262041 | `e5cbde0bf94050b497c6fce4321231d867172c455c7974a4b8f63e7ff4199c47` | `7485a765f4b1981ba9d2541b06cd17e05a78e0bd1399fb4044ee9aed2e2b516e` | `d30ea091734e645336044ee516f7b376cb89db2714ec0558aab87731baf70922` | 55,916 | 100 | 19/20 | 68 (30) |
| P2 | 20262051 | `06e226296c5209b195228a7d09179bfebb81293d09b1e0bf0108006f5a3abd63` | `885b294f9cf6dcdfd3a21daf9b8f3ae46ab6ddcf949d7c0e3d0f3fcf86b50281` | `6a57f0ff6b04b6ca7bf1541ea09a2a06561c35c0d4023a07ce6bc711323b8601` | 55,213 | 100 | 14/20 | 66 (17) |
| #93 M (reference) | 20261021 | `84f0614a…` | `6f08629e…` | `99c53db0…` | 55,838 | 100 | 16/20 | 70 (27) |

The H4 variant mix spans M's on both sides. The worlds live outside the repository; the executor copies them to the
public-world VM and checks the file SHA-256 there before slots are built.

### Sealed generator: two new private seeds on Garry's Mac (GBRA-40)

- **Settings.** `hard-sealed-v2`, `--scale large`, frozen knobs, at the recorded harness SHA. Neither seed has been
  used before.
- **Custody.** As #93's S: seeds stay on the Mac (mode 600, never printed, never committed, never on Capy Drive),
  and only digests and counts are reported.
- **Mint commands** (run on the Mac in a gbrain-evals checkout at the recorded harness SHA, after `bun install`):

```bash
umask 077
mkdir -p ~/Private/gbrain-sealed
od -An -N4 -tu4 /dev/urandom | tr -d ' ' > ~/Private/gbrain-sealed/cat40-next-sealed-seed-1.txt
od -An -N4 -tu4 /dev/urandom | tr -d ' ' > ~/Private/gbrain-sealed/cat40-next-sealed-seed-2.txt
chmod 600 ~/Private/gbrain-sealed/cat40-next-sealed-seed-*.txt
git rev-parse HEAD
for i in 1 2; do
  bun eval/generators/hard-sealed/cli.ts --seed "$(cat ~/Private/gbrain-sealed/cat40-next-sealed-seed-$i.txt)" \
    --scale large --knobs docs/benchmarks/cat40-hard/knobs.frozen.json \
    --out ~/Private/gbrain-sealed/cat40-next-s$i --digest-only
done
```

- **What gets reported.** `git rev-parse HEAD` and, for each seed, the printed digest, knob digest and counts.
  `--digest-only` writes no document and prints no seed.
- **Seed rules.** Neither seed may be one of the plan's fixed seeds (20261005, 20261006, 20261021, 20261031, 20261041,
  20261051, 20261099, 20262041, 20262051) or a test seed (101, 202, 303). If a printed run reports an invariant failure, that seed is
  redrawn with the same `od` line, and the failure is reported as a count.
- **Generation.** The worlds are generated later, for the run, with the same command without `--digest-only`. They
  travel Mac → one Capy cloud machine → the custody VM. The transit copy is deleted once the custody VM's SHA-256
  matches, and `confirm-world` (sealed) confirms each digest against the one recorded below.

## Gates before counted cells (per world)

1. The world validates against its generator, and its digest equals the one recorded here.
2. Oracle on all 100 tasks with the three models: pooled success ≥ 95%. Below that, stop and report, and run no counted
   cell on that world.
3. Every gbrain slot, for both builds, passes the write probe, the restore probe and the fail-closed rerank probe,
   with 0 queued effects at snapshot. Config readback for both recipes matches the lists above, and wave slots report
   0 owner-phrase links.
4. Model freshness is rerun (see Models).
5. The projected spend plus 15% fits the machine's ledger.

## Endpoints

Development results are never pooled with confirmation results. Arm, model and task identify a cell; worlds are P1,
P2 (public) and S1, S2 (sealed).

### Primary: Δ wave − fs, per generator

For generator G with worlds G1 and G2:

1. For each model m, r_arm,m is the arm's success rate over all 200 tasks of G1 and G2 (canonical cells: the last
   harness-clean attempt per arm, model and task).
2. Δ_G = (1/3) Σ_m (r_wave,m − r_fs,m).
3. **Interval:** a task-clustered percentile bootstrap with tasks nested in seeds. Seeds are fixed, not resampled
   (two seeds can't estimate between-world variance), so the interval is conditional on these worlds.
   - 10,000 resamples, using one `random.Random(1)` stream (seed 1, #93's convention).
   - Each resample visits G1, then G2 (in seed order). For each world it draws 100 task ids with replacement
     (`rng.choice` over that world's task ids sorted as strings), so every resample keeps 100 tasks per world.
   - A drawn task brings all three models' wave and fs cells, and Δ_G is recomputed on the resample.
   - The interval is the 2.5th and 97.5th percentiles.
4. Δ is also reported per world, with the same procedure on that world alone.

Wording, as in #93:

- **Parity** only when the lower bound is above −3 pp; otherwise "not distinguishable", with the point estimate.
- **Ahead** only when the lower bound is above 0.
- **General claim:** the wave holds gbrain's place against files only if Δ_public ≥ 0 and Δ_sealed ≥ 0 (point
  estimates), as last wave. If either is below 0, the result is published as it is, and #93's statement applies:
  stop claiming that gbrain beats files on hard company questions. If only the public generator passes, the result
  is reported as "the main generator's wording only", and it still counts as failing the general claim.

### Secondary

All secondaries use the same nested bootstrap. Each is reported per world and per generator, and is pooled over all
four worlds where stated.

1. **Wave − baseline success.**
2. **Wrong values, wave − baseline (D3).** The wrong-value rate is cells with `score.said_wrong` (naming a listed wrong
   value) over all cells, paired by world, task and model.
   - **Test:** pooled over all four worlds, the effect counts only if wave − baseline ≤ −2.0 pp and the 95% upper
     bound is below 0.
   - **Reported separately:** wrong submitted cells (submitted and not successful) over all cells and over submitted
     cells, plus non-submission and turn-cap stops. Fewer wrong answers can't come from more non-answers.
   - **Development reference:** −4.5 pp [−7.3, −1.7], all-on against the all-off control on M.
3. **Per family,** wave vs baseline and wave vs fs. H4 is called out and stratified by the `+long` variants.
4. **Per model,** with the people-facing models first and ceilings called out. Sol had 1 wrong-value cell in 200 for
   control on M.
5. **Sol wrong values (round 2 watch item).** Sol's wrong-value cells under wave vs baseline per world, with the
   paired test. Development had 4 under all-on vs 1 under control, pooled. This is reported, not a gate, and it is
   flagged if the wave exceeds the baseline by 3 or more cells pooled over the four worlds.
6. **Draft-first firing and harm,** with `draft_first.py`'s settled definition. An H4 item is draft-led when the
   account's contract and amendment documents that reference it by name, code or nickname, ordered newest document
   date first with ties by id, lead with a `DRAFT` amendment.
   - **Firing:** `entity` names rows whose records list a draft ahead of every executed record, per model and `+long`
     stratum.
   - **Harm:** wave vs baseline wrong-value cells and successes on draft-led tasks, and on the cells served a
     draft-first row.
   - **Expected sign:** firing is positive. Harm is expected to be ≤ 0 (development: 0 vs 12 wrong values over 69
     served cells).
7. **Firing counters** per arm (`firing.ts`), names-call p50/p99, cost per successful task, median seconds per cell,
   and the rerank check.

## Budget and stop rule

Priced from the plan's per-arm costs at 100 tasks (gbrain about $198, fs about $286, oracle about $25) times #93's
ledger rate of 1.108:

| Item | Per world | 4 worlds |
|---|---|---|
| gbrain-wave | $219 | $877 |
| gbrain-baseline | $219 | $877 |
| fs | $317 | $1,268 |
| oracle | $28 | $111 |
| Slot builds, 5 slots: wave and baseline per world (public about $13.68 each, sealed about $17) | | about $123 |
| **Total** | | **about $3,256** |

- **Approved:** $3,400, which leaves about $144 for ordinary retries.
- **Ledgers:** one per machine. `.budget/cat40-next-confirm-public.sqlite` (P1 and P2) and
  `.budget/cat40-next-confirm-sealed.sqlite` (the custody VM, S1 and S2), each with a $1,700 program cap.
- **Per-arm caps** (`--budget-usd`, 1.15 × price): gbrain arms $252, fs $364 (#93's M fs cost $334 priced), oracle
  $32. Sealed slot builds use `--slot-build-allowance-usd 6` (#93's S corpus needed more than $4 per slot).
- **Stop rule:**
  - An arm that reaches its cap stops. Its world's endpoints are not computed, and the shortfall is escalated to
    Garry through GBRA-40 before any more money is spent.
  - If a harness fault voids an arm, confirmation stops and the rerun is escalated. The reserve doesn't fit a
    full-arm rerun.
  - After each world's first counted arm, the ledger projection plus 10% is checked against the cap. A projection
    over the cap stops the run and escalates it.
  - No cell is rerun, except harness or provider errors covered by the runner's existing retry rules.

## Freeze rules

- **Seeds.** Public 20262041 and 20262051, digests above. Sealed: private, digests recorded below before generation.
  Bootstrap seed 1.
- **Knobs.** `knobs.frozen.json` (SHA-256 `53c5be3c…`, knob digest `37a16085…`) for every world.
- **Scorer and analysis.** `eval/runner/cat40/score-hard.ts` and `judge-hard.ts` at the recorded harness SHA, judge
  `gpt-6.1-sol`. The analysis scripts are frozen at that SHA: `draft_first.py`, `firing.ts`, and the confirmation
  analysis script that implements the primary procedure above. The executor adds that script and tests it on #93's
  M and S cells before any confirmation cell.
- **Harness.** The executor may add only these commits before cells:
  - registering the four confirmation seeds and digests (public seeds in `HARD_SEEDS`; sealed digests only);
  - registering the confirmation program steps (baseline and wave arms, two worlds per machine, one ledger per
    machine, the oracle gate, per-arm caps);
  - the confirmation analysis script.

  None of them may change a world, a score or an arm setting. The SHA and a freeze check of the frozen files are
  recorded below.
- **Drift note.** Counted steps run with
  `--accept-freeze-drift "PREREG.md (cat40-next-wave): harness <sha> preregistered; drift is confirmation seed and program-step registration on the dev harness (scripted gbrain agent, whole-result transcripts), neither of which changes a model cell (<date>)"`.
  The SHA and date are filled in at the executor's freeze check, and nothing else in the note changes.
- **Builds.** Wave (the F5-removed head, recorded below) and baseline `09d21554d`. Component retention is frozen on
  development data, and no component is selected using a confirmation world. If master is merged into the wave after
  confirmation and touches the measured path set, the decision record needs a written no-effect argument or a
  re-confirmation (plan).
- After confirmation, no gbrain change is tuned on these worlds' tasks.

## Hygiene

- No development agent has read the sealed generator's code or any sealed output.
- Sealed seeds never leave Garry's Mac. Sealed worlds cross one Capy cloud machine in transit, are deleted there once
  the custody VM holds them, and never touch Capy Drive.
- Each VM is destroyed after its outputs (results, transcripts, receipts; no world documents for sealed worlds) are
  copied.
- Reports name counts, ids, models, tools and document types only. No entity names or values appear.

## Known limitations

- **Development never ran the confirmation's wave config,** all-on without F5 on the F5-removed head. The round 3
  diagnostic arm (`all-on-no-f5`, declared in `docs/benchmarks/2026-10-13-cat40-dev-round-3/DECLARATION.md`) runs
  before any confirmation cell, and its result is recorded below. If it is clearly worse than all-on by the
  declaration's definition, that is recorded here as a known limitation. Either way, the wave arm stays all-on
  without F5.
- **F5's links reached agents in development only through F1's record rows** (d1b record). Without F5, documents
  that name an account only by an owner phrase can't appear among that account's records.
- **Intervals are conditional on the two worlds per generator.** Seeds are not resampled.
- **The wave config is clearly worse than all-on with F5 in development** (round 3 diagnostic, recorded below, as
  the first bullet of this section provides). On World M, all-on without F5 on `a3384b989` is level with the pooled
  control (success −0.5 pp [−3.8, +2.8]) and below pooled all-on (success −5.3 pp [−9.5, −1.3], wrong values +4.8 pp
  [+1.5, +8.5]), with the loss concentrated in H4 (−20.0 pp) and in Sonnet (−10.5 pp). So the confirmation tests a
  wave that development measured at about the control's level, not all-on's +4.8 pp. The arm does not change.

## Recorded before cells

(Appended by the executor; no edits above this line.)

- **Wave build** (2026-10-13): gbrain `capy/cat40-next-part1` @ `a3384b989a85f1f5fbb582c596e47af798a6157d` (v0.60.189.0,
  "Remove F5 owner phrases from Part 1: failed the preregistered d1b gate"). The Part 1 implementer reports the full
  8-VM ci:ubicloud gate green on this SHA.
  - **`src/` against `e67dcc9f8`:** 23 files, 21 insertions and 1,829 deletions, all on F5 paths: the owner-phrase
    module, mention wiring, ops, persistence, verbs and the F5 schema migrations. The implementer reports that this
    mechanically matches the inverse of F5's own diff.
  - **`src/` against the baseline:** `src/schema.sql` is byte-identical to the baseline `09d21554d`. The merge base
    with master is still `09d21554d`. The confirmation's measured path set is `git diff --name-only 09d21554d a3384b989
    -- src`: 35 files, list SHA-256 `cd4c3e926a3c…`. It replaces the 53-file `e67dcc9f8` set named above.
- **Harness** (2026-10-13): gbrain-evals `capy/cat40-next-prereg` @ `f4208ddd54e900f4ea8d410e0cbae2e16451d705`. That is
  `a85e6e29` plus four executor commits:
  - `dc2bb79a`: `HARD_SEEDS.next_confirmation = [20262041, 20262051]`, and `requiresFreeze` covers them.
  - `9696e195`: `eval/runner/cat40/next-confirm.ts`, which holds the worlds, builds, recipes, caps, ledgers, oracle gate
    and `check-world`. `plan --world <w> --date <d>` prints every step's exact command.
  - `76558dc7`: `eval/runner/cat40/next_confirm_analysis.py` and `test/eval/cat40-next-confirm.test.ts`.
  - `f4208ddd`: the drift note, below.

  Later commits on this branch touch only this file. `bunx tsc --noEmit -p .` is clean, and the 316 cat40 tests pass.
  - **Freeze check** (`hard-ops.ts freeze check`): frozen code changed in `schema.ts`, `hard.ts`, `loop.ts` and
    `pg-arm.ts`. In detail: the seed constants; the scripted gbrain agent and whole-result transcripts in `hard.ts`
    (both on the development harness); two optional loop hooks merged from main that the Hard runner doesn't pass;
    and an embedder base-URL default merged from main that the pg arm (not run here) uses. None changes a model cell.
  - **World output is unchanged.** At this SHA the public generator still produces P1's base digest `e5cbde0b…` and
    #93 M's `84f0614a…`. The sealed generator's test seed 101 (4k, frozen knobs, `--digest-only`) prints `cc784e5f…`
    at both `a85e6e29` and this SHA. So sealed digests minted at `a85e6e29` hold here.
- **Drift note, corrected before any cell** (2026-10-13). The freeze check names `loop.ts` and `pg-arm.ts` too, so the
  note under "Freeze rules" undercounted the drift. Counted steps use the note `next-confirm.ts` builds:
  `PREREG.md (cat40-next-wave): harness f4208ddd54e900f4ea8d410e0cbae2e16451d705 preregistered; drift is the confirmation seed registration (schema.ts, hard.ts), the scripted gbrain agent and whole-result transcripts (hard.ts), and unused loop hooks (loop.ts) and an embedder base URL (pg-arm.ts) merged from main; none changes a model cell (<date>)`.
  `<date>` is the date passed to `plan --date`, and it is the same for every step of a world.
- **Analysis check** (2026-10-13): on #93's M cells (`main-cells/results.jsonl`, gbrain-hard vs fs) the primary
  procedure reproduces the published +7.67 pp [+2.67, +12.67]. A synthetic two-world test confirms that draws stay
  inside each seed. #93's S cells were not used, because this executor doesn't open sealed outputs.
- **Sealed digests.** They are not compiled into the harness. `check-world --world s1|s2 --digest <d>` compares each
  sealed world with the digest recorded here.
- **Sealed worlds minted** (2026-10-13, GBRA-40 on Garry's Mac): gbrain-evals `a85e6e2997def8652996cc0386c43f78453d7150`,
  `hard-sealed-v2`, `--scale large`, frozen knobs (knob digest `37a16085e0fbf2e92072b2e7cf00468d43451dd4fb35bb1232ebbf79d3027434`),
  Bun 1.3.13, `--digest-only`, no redraws. The seeds stay on the Mac.

  | World | Digest | Entities | Docs | Tasks |
  |---|---|---|---|---|
  | S1 | `561759a86819cda78184da4f22398daeee92f2ccd4b57fac89c8ed6ce6cb8fb8` | 2,880 | 55,758 | 100 |
  | S2 | `54d6ca94860c6401653d415afbb00ed69e7aae84dd8b228e9e76355e1b3d2dc6` | 2,882 | 55,676 | 100 |

- **Staging precondition (sealed).** The worlds are regenerated from the seeds at staging, with the mint command
  without `--digest-only`. That world's digest must equal the minted digest above. On the custody VM,
  `bun eval/runner/cat40/next-confirm.ts check-world --world s1|s2 --file <world.json> --digest <digest above>`
  regenerates the world from its recorded seed and knobs, and compares digests; for sealed worlds `hardWorldDigest`
  equals `sealedWorldDigest`, checked on test seed 202. A world whose digest differs is void: no slot or cell runs on
  it, and it is escalated to Garry through GBRA-40.
- **Runtime independence of the generators** (checked 2026-10-13 at `31c73953`, whose world-shaping code is that of
  `a85e6e29`). Bun 1.3.13 and Bun 1.4.3 print identical digests for the sealed generator on test seed 101 at
  `--scale large` (`1c3ee3c8…`) and on test seed 202 at 4k (`8d2a4284…`), and for the public generator on P1's base
  (`e5cbde0b…`). #93's M base (`84f0614a…`) and the d4b base (`82b983fa…`) also reproduce under Bun 1.4.3. So
  staging doesn't need Bun 1.3.13. The digest precondition above still decides each world.
- **Harness re-frozen** (2026-10-13, before any confirmation cell): `e805203fd60f87d1bc7249925dbfef7e01773fed`. It
  replaces `f4208ddd` because development round 3 hit a harness crash that the confirmation could also hit.
  - **The crash.** `runHardCell` asked the gbrain slot for its write-tool list after the pool had taken the slot back.
    The pool's restart for the next cell clears the client, so an H5 cell's write diagnostic could throw "gbrain slot
    not started" and end the whole runner process. In round 3 that happened after 194 cells; the run resumed with no
    lost or duplicated cell.
  - **The fix** (`3cb5aaaf`, merged from `capy/cat40-dev-harness`). The list is taken once, when the cell acquires its
    freshly restored slot, which is the same base list the old code read after the restore. So no score or diagnostic
    changes. A forced probe in `test/eval/cat40-hard.test.ts` fails with the crash before the fix and passes after.
  - **Scope of the change.** `git diff f4208ddd e805203f` touches only `arms.ts`, `hard.ts`, `next-confirm.ts` (the
    drift note), the test and this file. No world-shaping file changed, so the minted digests hold.
  - **Checks:** tsc is clean, and the 317 cat40 tests pass.
  - **Freeze check:** it now also lists `arms.ts`.
  - **Drift note:** counted steps use the note `next-confirm.ts` builds at this SHA:
    `PREREG.md (cat40-next-wave): harness e805203fd60f87d1bc7249925dbfef7e01773fed preregistered; drift is the confirmation seed registration (schema.ts, hard.ts), the scripted gbrain agent and whole-result transcripts (hard.ts), the write-tool list taken while the gbrain slot is live (hard.ts, arms.ts), and unused loop hooks (loop.ts) and an embedder base URL (pg-arm.ts) merged from main; none changes a model cell (<date>)`.
- **Round 3 diagnostic** (2026-10-13, before any confirmation cell). Record: `docs/benchmarks/2026-10-13-cat40-dev-round-3/`
  (gbrain-evals `capy/cat40-dev-harness` @ `b70e0536`, merged here). Arm `all-on-no-f5`: the all-on keys with F5 off on
  wave build `a3384b989`, World M, full family, three models, 300 canonical cells, 0 harness errors, two budget runs
  (`cat40-model-ladder-2026-10-13T17-27-42-075Z-e349245f`, 194 cells, and `…T18-06-13-246Z-f41f415a`, 106 cells, after
  the crash described under "Harness re-frozen"). Comparisons as declared in that directory's `DECLARATION.md`
  (task bootstrap, 4,000 resamples, seed 11; references are the per-pair mean of rounds 1 and 2):

  | Δ pp, 95% interval | vs pooled control | vs pooled all-on |
  |---|---:|---:|
  | success | −0.5 [−3.8, +2.8] | −5.3 [−9.5, −1.3] |
  | wrong values | +0.3 [−2.5, +3.2] | +4.8 [+1.5, +8.5] |
  | H4 success | −4.2 [−15.8, +7.5] | −20.0 [−33.3, −8.3] |
  | claude-sonnet-5-5 success | +2.0 [−5.0, +8.5] | −10.5 [−18.0, −4.0] |

  **Clearly worse than all-on: yes** (both overall intervals exclude 0 in the harmful direction), so it is added under
  "Known limitations". The wave arm stays all-on without F5. Firing: served instructions are identical to all-on's;
  known_as and owner-phrase rows are 0, and the share of names rows carrying records falls from about 82% to 60%.
  Spend: round 3 $187.20 of its $228.19 cap; development program $1,518.50 of $1,777.15.
