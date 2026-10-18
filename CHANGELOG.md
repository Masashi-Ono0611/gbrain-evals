# Changelog

This records what each gbrain-evals release changed and what its measurements meant at the time. Versions follow `VERSION` and `package.json`. Historical scores keep their original dates; later corrections do not turn them into measurements of today's code.

## [Unreleased] - 2026-10-18

### Graph backend: HydraDB vs Postgres for gbrain's graph walks (GBRA-123)

- **Report** ([doc](docs/benchmarks/2026-10-17-graph-backend.md), [preregistration](docs/benchmarks/2026-10-17-graph-backend-preregistration.md), pushed before any timed run). gbrain's `traverseGraph` and `traversePathsDetailed` on seeded fictional power-law graphs of 10,000, 100,000 and 1,000,000 pages: the old recursive CTE (`b1fdcb843`) and the breadth-first walks of #6934 (`fc1121cae58`) on Postgres 17, against HydraDB `fe496d475be` as the walk engine with Postgres hydration. HydraDB returned the same answer as breadth-first Postgres on all 54,842 compared calls, but its warm p95 was 6.28 s against 1.44 s at 100,000 pages and 6.28 s against 3.45 s at 1,000,000. The preregistered rule (2x and 50 ms faster) is not met, so production HydraDB routing is not built. HydraDB is faster on deep `both` edge walks (10.3 s against 3.8 s p95 at depth 3, 1,000,000 pages), flagged as the next Postgres target. The old CTE differs from breadth-first only where its row cap fired.
- **Harness**: `eval/runner/graph-backend/` (generator, loaders, eval-only HydraDB HTTP adapter, resumable runner, analyzer); receipts per tier under `docs/benchmarks/2026-10-17-graph-backend/`. Cost: $0 in model spend; one Ubicloud `standard-16` for 8 h 24 min (about $4.20).

## [0.10.120] - 2026-10-17

### W11: sealed confirmation of gbrain W4 (weekly belief diff), preregistered

- **Preregistration** ([file](docs/benchmarks/2026-10-17-w11-w4-sealed-confirmation-preregistration.md), results glob in `preregistrations.d/w11-w4-sealed-confirmation.json`). W11 now confirms W4 alone (`delta {beliefs: true}`, `gbrain beliefs`, gbrain #6866) on gbrain release v0.60.289.0. The custodian mints three fresh seeds and fresh wording for every belief-changing line inside custody on the Dyson Sphere; only the aggregate verdict leaves it. Gates: W4's own bar, set-F1 at least 0.95 on every seed, plus exact before and after for every re-score, and correct cause and evidence pointer on every reported change. Tokens against `delta`'s page list are reported, not gated.
- **Harness**: `eval/runner/belief-weekly-probes.ts` with `eval/generators/belief-weekly-gen.ts`, a port of gbrain's W4 probe that takes custodian phrasing (`--phrasing-file`, access-logged) and fresh seeds. It calls no model. On v0.60.289.0 with development phrasing and seed 20261016 it passes every gate (37 of 37 changes) and matches the gbrain probe's per-week counts exactly. Cost: $0, cap $1.

## [0.10.119] - 2026-10-17

### Living pages (gbrain W9) decided on prior: not built in V1, W10 dropped with it

- **Verdict** ([file](docs/benchmarks/2026-10-17-living-pages/verdict.json); the [preregistration](docs/benchmarks/2026-10-17-living-pages-preregistration.md) records it under Changes). No owner data: the owner declined to supply production-brain counts, so the observed ratio is unknown and the decision is taken on the prior. The build threshold is 1,387 reads per changed page-day (0.5 review minutes at $2.00 a minute, $0.017 a refresh), and nothing known about a personal brain's read rate comes close, so W9 is not built in V1 and W10 (provenance render and block undo) is dropped with it. The preregistered rule is unchanged. Reopen if aggregate telemetry from a hosted brain shows the observed ratio at or above the threshold. Cost: $0.

## [0.10.118] - 2026-10-17

### Living pages (gbrain wave 4b W9): the read/write break-even, preregistered before the owner's counts

- **Preregistration** ([doc](docs/benchmarks/2026-10-17-living-pages-preregistration.md)). The plan builds living pages only if the cheaper designs lose, and the answer turns on reads per change. From pinned questions, the closest measured analogue (C4 run 3, Sonnet 5.5), a refreshed page is cheaper per correct answer than equal-token anchored retrieval above **8.2** reads per change with the cheapest measured refresh and free review, **23.2** with the plan's $0.017 living-page refresh, and **1,387** once a proposal costs 0.5 review minutes at $2.00 a minute (the build threshold; the doc tabulates 194 to 13,663 across review times and prices). The owner's ratio comes from two read-only aggregate queries over 30 days: operation counts from `mcp_request_log` (frozen read set) over changed page-days from `page_versions` and new pages. W9 is built only at or above 1,387; otherwise it and W10 (provenance render and block undo, which need refreshed blocks) are dropped. If W9 is built, the paid `living-pages` category (capped at $40) replaces the priors with measured review minutes and costs before any default.
- **Classifier**: `eval/runner/living-pages-breakeven.ts` turns the two query results into the decision, with a test that pins the thresholds; `preregistrations.d/living-pages.json` registers the experiment. No owner data is in this repository. Cost: $0.

## [0.10.117] - 2026-10-17

### Forecast journal (gbrain wave 4b W7, #6886), shipped in v0.60.286.0

- **Report** ([doc](docs/benchmarks/2026-10-17-forecast-journal.md), [preregistration](docs/benchmarks/2026-10-17-forecast-journal-preregistration.md), frozen in gbrain `65ed40ec6` before any scored run). The $0 synthetic gate for the private forecast journal: 20 cohorts of placeholder holders with known skill, 5,622 predictions, in-memory PGLite. It passes every criterion. Shrunk accuracy ranks holders in their true order (median Spearman ρ 0.905, bar 0.80). Who-was-right set-F1 is 1.000. Journal totals, per-holder counts, `low_n` flags and uncertified prediction-time labels match exactly. All 8 remote probes pass: remote `takes_list`, `takes_search` and `takes_scorecard {}` are unchanged and carry no journal field, and remote `group_by` or `min_n` is refused with `scorecard_group_by_local_only`. Set-F1 and the exact counts are a ceiling (regression guards); ρ is a diagnostic of shrinkage, not a ranking of real people.
- **Shipped**: gbrain #6886 merged as `d28cbaeee` (v0.60.286.0). A rerun at that commit gives identical results; its `summary.json` and `summary.md` and a `verdict.json` are in `docs/benchmarks/2026-10-17-forecast-journal/`. `README.md` and `docs/README.md` gain the row.
- Measured through gbrain's own harness; the pin is unchanged. Cost: $0.

## [0.10.116] - 2026-10-17

### P1 E2 rerun on gbrain W5: late closures disclosed as upper bounds, apply certification holds

- **Held-out verdict** ([file](docs/benchmarks/2026-10-05-heldout-verdicts/p1-e2-w5-heldout-2026-10-16.json), [preregistration](docs/benchmarks/2026-10-16-p1-e2-w5-rerun-preregistration.md), frozen in 0.10.113 before the first cell). The custodian ran gbrain `6c3e6fe05` (v0.60.273.0, wave 4a W4 and W5) with harness `3a9360b86` on phrasing set C's joins-only ledger, whose SHA-256 matches the E2 attempt-2 receipt: `claude-opus-5-5`, `claude-sonnet-5-5` and `gpt-6.1-sol`, seeds 11, 13 and 17, 27 of 27 runs. C1 passes: every late closure is disclosed as an upper bound (`late_upper_bound` equals `late` in every run). C2 passes for all three models: 0 wrong and 0 undated closures in every run, as-of exact 0.392 to 0.397 against the 0.361 floor. So the three models keep `apply` on the W5 build.
- **Late closures, reported, not gated**: 48 of 75 per run (48 of 74 in one Sonnet run, where one judge error left a proposal unapplied; no harness errors, no reruns). W5's build applies more closures per run than E2's (74 to 75 against 66), so this is not comparable with E2's 41 of 66.
- **Records**: the verdict index and the held-out program's P1 section and scorecard gain the rerun. Row-level output stays in custody. Cost: $2.40 of the $8 cap, on the custodian's eval ledger.

## [0.10.115] - 2026-10-17

### Take grading shipped in gbrain v0.60.282.0 (#6882), and the auto-resolve follow-ups

- **Shipped**: gbrain #6882 merged as `4e698e9d9` (v0.60.282.0). `GRADE_TAKES_MEASURED_MODELS` is `openai:gpt-6.1-sol` for prompt `hybrid-evidence-v2`, and auto-resolve stays unwired. The [take-grading report](docs/benchmarks/2026-10-16-take-grading.md) and its `verdict.json` (`gbrain_shipped_in`) name the release.
- **Follow-ups for auto-resolve** (decided October 16, recorded in the report): auto-resolve is a later opt-in PR, built only after a real sample of about 300 graded takes passes. A take whose numeric target was missed is never auto-applied, neither as `partial` nor as `incorrect`; it is held for manual review. The measured judge is scoped to its prompt version. A thinking setting or larger output ceiling for the judge, and a parser tolerance, are proposed for the next preregistration.
- Measured through `--gbrain`; the pin is unchanged. Cost: $0.

## [0.10.114] - 2026-10-17

### Take grading (gbrain wave 4b W6, #6882)

- **Report** ([doc](docs/benchmarks/2026-10-16-take-grading.md), [preregistration](docs/benchmarks/2026-10-16-take-grading-preregistration.md), frozen in gbrain `d99b84694` before any counted run). 790 counted synthetic forecasting takes with dated evidence and placeholder names (750 in the rule: 500 resolvable, 250 the evidence cannot settle; 40 exploratory), one run per model through gbrain's production evidence block, judge call and parser, $9.25 in all. A verdict counts as applied when it is not `unresolvable` and its confidence is at least 0.95; a model qualifies when the one-sided 95% upper bound on wrong applied verdicts is at most 1%. `gpt-6.1-sol` applied 496 with none wrong (0.6%), resolving 99.2% of resolvable takes and holding back on every unresolvable one; it qualifies, and gbrain's `GRADE_TAKES_MEASURED_MODELS` lists it. `claude-opus-5-5` gave the gold verdict on every resolvable take but applied 2; `claude-sonnet-5-5` applied 121 with one wrong (a real-world proposition graded from its own knowledge). On the exploratory `partial` set every model calls a missed target `incorrect`, a policy question left open; 12 of 18 unparsed answers spent the judge's 600-token ceiling on thinking.
- **Records**: fixtures, dev-round and counted rows with each model's reasoning, `summary.json`, `summary.md` and `verdict.json` in `docs/benchmarks/2026-10-16-take-grading/`; `README.md` and `docs/README.md` gain the row.

## [0.10.113] - 2026-10-16

### N6 on gbrain's weekly belief diff (delta beliefs) at the v0.60.273.0 release, and the P1 E2 rerun preregistration for W5

gbrain v0.60.273.0 (#6866, wave 4a) adds `beliefs: true` to `delta`: each belief that changed in a window, with its value
before and after, the event that caused it and a pointer to the evidence, read from the belief ledger. N6 now fuzzes it
with the ledger on before seeding, records the trusted and remote outcome of every `beliefs` probe, counts the probes
that read real history with signal, and fails the HTTP verdict when a build exposes `beliefs` and none do. The oracle
view masks `beliefs.until`, the request instant. On the branch, N6 found 12 content leaks in process and over Postgres
HTTP (held Takes shown to remote callers, as revisions and in a new page's creation body), fixed before review. At the
release, from a clean checkout of the tag: Postgres over HTTP passes 155 of 155 mandatory cells with 0 leaks and 0
oracles, and in process on PGLite 0 leaks and 0 oracles, with 28 `beliefs` probes reading real history on each
([report](docs/benchmarks/2026-10-16-n6-delta-beliefs.md)).

The P1 E2 rerun after gbrain W5 is preregistered ([preregistration](docs/benchmarks/2026-10-16-p1-e2-w5-rerun-preregistration.md)):
Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol on phrasing set C's joins-only ledger, seeds 11, 13 and 17, run by the custodian
after this release with a $8 cap. It reports the late-closure count and checks that every late closure is disclosed as
an upper bound. `temporal-contradictions.ts` gains that count, `late_upper_bound`, with a test. No held-out text is in
this repository. Measured through `--gbrain`; the pin is unchanged. Cost: $0.

## [0.10.112] - 2026-10-16

### N6 with gbrain's recorded-time reads (known_as_of), at the v0.60.267.0 release

gbrain v0.60.267.0 (#6850) adds `known_as_of` to `get_page` and `get_versions`: the page as the brain had recorded it at an
instant, from the belief ledger. N6 now fuzzes both params, with the ledger on before seeding, and records for every
`known_as_of` probe what the trusted caller and the remote caller got back (`history`, `coverage_from`, `coverage_gap`,
`unproven`, `invalid_params` or `refused`). The Postgres-over-HTTP verdict fails when a build exposes `known_as_of` and no
probe reads real history. At the release, from a clean checkout of the tag: Postgres over HTTP passes 155 of 155
mandatory cells with 0 leaks and 0 oracles, and 56 of its 136 `known_as_of` probes read real history with signal; in
process on PGLite, 0 leaks and 0 oracles, with 90 of 180 reading real history. An earlier W2 head had 16 existence
oracles over HTTP (a remote client got `page_not_found` for a private page but `coverage_from` for a slug never written),
fixed before release ([report](docs/benchmarks/2026-10-16-n6-known-as-of.md)). Measured through `--gbrain`; the pin is
unchanged. Cost: $0.

## [0.10.111] - 2026-10-16

### N1 with gbrain's belief ledger on (probe 40), at the v0.60.265.0 release

gbrain's belief ledger (W1, #6806) shipped in v0.60.265.0. Probe 40 of its design requires that turning the ledger on
changes no answer, so N1 ran with the ledger off and on against the release commit `09943580e`, on PGLite and Postgres
over the CLI, stdio MCP and HTTP MCP. Both arms gave 388 of 388 current values, 0 stale, 385 of 385 history, 124 of 124
negative controls, and no leaks, lost writes or system errors, with identical per-cell and per-checkpoint counts
([report](docs/benchmarks/2026-10-16-belief-ledger-n1.md)). The runner gains the `EVAL_BELIEF_LEDGER=1` hook, which
runs `gbrain beliefs enable` in each cell before any write, and the N1 runner now scrubs home and temp paths from its
receipts. Measured through `--gbrain`; the pin is unchanged. Cost: $0.

## [0.10.110] - 2026-10-16

### LHF wave 2: plan, verdicts and the attendance paraphrase gate

gbrain's second low-hanging-fruit wave (latency, retrieval and cost) shipped as gbrain v0.60.259.0 (#6822). Its plan,
the three audits it came from, both rounds of gstack autoplan reviews and the measured verdict for every item are in
[docs/plans/2026-10-15-lhf-wave-2/](docs/plans/2026-10-15-lhf-wave-2/VERDICTS.md). Against master, every shipped
performance item was parity-clean on PGLite and Postgres. A remote MCP search 30 ms from Postgres went from 1.72 s to
0.88 s at p50, and the 79-call parity run went from 6,008 to 3,580 statement round trips. The attendance paraphrase item
failed its [preregistered gate](docs/benchmarks/2026-10-16-lhf-wave-2-attendance-preregistration.md). The development
split went from 0 to 150 of 150, but 30 independently written held-out questions fired 18 of 90 runs (master 6 of 90),
against an 80% floor, so it did not ship. The held-out text is not published. N9 gains `--extra-split`, and the gate adds
a relation-aware scorer (`eval/runner/lhf-wave-2-attendance-gate.ts`) and a parser probe
(`eval/runner/parse-relational-questions.ts`). Cost: $0.

## [0.10.109] - 2026-10-15

### N14 at large pages Wave B PR 1: segmented storage (exploratory)

An exploratory, hermetic N14 run against gbrain master `7f3c9f5` (v0.60.252.0, #6787) with `pages.segmented_storage` on
and off. It cost $0. With the switch on, the 2 MB documents and the 20 MB chat are stored in segments (8, 8, 6 and 74) and
found 40 of 40 in every decile. A 1 KB append writes one tail segment and re-embeds one chunk (two for the 2 MB chat, a
4.35x ratio). The 20 MB append takes 7.1 s, against 11.9 s inline, and ingest peaks at 2.9 GB, against 4.1 GB. The stored
segments match the source byte for byte. But `get_page` and `gbrain export` refuse a segmented page with
`page_body_segmented` until PR 2, so windowed reads are 0 of 40 and the export round trip fails. The 200 MB chat is
still refused: `put_page` with `request_too_large` at 24 MiB, and the streamed import with `file_too_large` at PGLite's
128 MiB ceiling. With the switch off, the same commit reproduces Wave A. The runner gains `--config`,
`--native-ingest import`, segment storage, append-write and segment round-trip measures, polling of `write_pending`
receipts and a wait for the segmented projection (preregistration Amendments 2 and 3). The bug ledger reviews N14-2.
See the [report](docs/benchmarks/2026-10-15-n14-large-page-fidelity-wave-b1.md).

## [0.10.108] - 2026-10-15

### D9 remote `find_contradictions`: N6 holds at 0 leaks; N2's verdict carries forward

gbrain v0.60.250.0 (#6784) gives remote, source-scoped and `min_trust` callers stored contradiction findings, re-reading
each side live under the caller's read policy. N6 could not test this before, because the op returned nothing to scoped
callers and its world had no stored report. The N6 runner now seeds one (`seedContradictionReport`), built by gbrain's own
contradiction probe with an oracle judge, so the report copies every protected marker. The
[D9 report](docs/benchmarks/2026-10-15-d9-find-contradictions.md) has three N6 runs on seed 20260930:

- v0.60.250.0 (`3c16e9ba4`): 540 `find_contradictions` probes, 160 with signal, 0 leaks; the whole run passes with
  0 content and 0 existence leaks.
- master before the release (`ea93c770b`): the op was suspended, so 0 signal and 0 leaks.
- A forced probe that skips the live re-read: 288 content and 192 existence leaks, all on `find_contradictions`.

The keyless N2 arm at v0.60.250.0 offers the same 2,680 pairs as the wave 14 re-pin (`77cf8e111`), and no commit since
changes the judge or probe, so the paid compatible-pair result (4 of 51, 7.8%, under the 0.10 cap) carries forward. A
remote caller now reads 100 of N2's 190 stored findings, where it read 0 before. Spend was $0.

## [0.10.107] - 2026-10-15

### D7 Cat 41 brief scenarios: no time-saved signal; the brief stays default-off

Cat 41 gains the D7 brief scenarios: reply, meeting prep, task start and a namesake negative, on two new
program-primary worlds (seeds 20261222 and 20261226), with facts aged 72 hours or crowded out of hot memory. gbrain
wires each harness itself with `gbrain setup`, and the brief switch is off or on, plus a hooks-off pull arm. The driver
timestamps every transcript line, keeps each hook's output, and has a $0 smoke mode that sends the harness's model
calls to its fake provider. `eval/runner/cat41/brief-d7.ts` runs the smoke and the analysis (`summarizeD7`).

The [preregistration](docs/benchmarks/2026-10-15-cat41-brief-preregistration.md) was frozen on gbrain v0.60.247.0
before any spend. The run had 48 native sessions: Claude Code with Sonnet 5.5 and Opus 5.5, Codex with gpt-6.1-sol,
and a Sonnet pull arm. It reports [no time-saved signal](docs/benchmarks/2026-10-15-cat41-brief.md):

- Time to the first correct output fell 6% with the brief on (ratio 0.938, 95% interval 0.853 to 1.032), short of
  the required 20%. Turns and tool calls to it fell about 10%, while per-request provider latency was unchanged.
- Success was 15 of 15 on against 14 of 15 off. Non-inferiority fails on width (lower bound −7.6 points).
- The brief fired in every positive brief-on cell and was always complete. It made 0 false pushes and was silent in
  every negative. Hot memory carried no needed value.
- In 19 of 20 brief-off sessions, the agent pulled the same brief itself with `context_pack(counterparty)`, so the
  push saved one round trip.

Under the preregistered rule, wave 5's brief work closes at default-off. Spend was $4.46 of a new $30 ledger.

## [0.10.106] - 2026-10-15

### D6 proactive brief, development v2: no time-saved signal

The D6 redesign reruns brief-off against brief-on on the T0 carrier where hot memory cannot carry the facts. Session 1's
facts are either backdated 72 hours (aged) or buried under 40 newer, unrelated facts (crowded). Each cell records its
session-1 save path and whether hot memory held a needed fact. The primary moved to time saved (session-2 tool calls
and input tokens) with non-inferiority on success, because the plan's exit allows "task success or user time saved".
The [preregistration](docs/benchmarks/2026-10-15-proactive-brief-dev-v2-preregistration.md) was written after v1's
results, approved, and frozen at `3952fb33` on gbrain v0.60.247.0 (`47f052af`, the brief's page-edit source) before
any spend. There are six new development seeds, 20261211 and 20261213 to 20261217.

The run used Opus 5.5, Sonnet 5.5 and gpt-6.1-sol, 144 cells, and reports
[no time-saved signal](docs/benchmarks/2026-10-15-proactive-brief-dev-v2.md):

- Session-2 tool calls fell 6% with the brief on (ratio 0.940, 95% interval 0.856 to 1.032), short of the required
  20%. Session-2 input tokens fell 8% (ratio 0.918, upper bound 0.971).
- Both arms finished 72 of 72 paired tasks, so success is non-inferior at −5 points.
- Hot memory carried no needed fact in any cell. The brief fired in 72 of 72 brief-on cells, including all 10 page-only
  sessions that v1 missed, and was silent in every brief-off cell. It made 0 false pushes and had no confident-wrong
  cells.

This is development evidence only and does not decide the default. v1's verdict stands. Spend was $29.60 of a new $35
ledger.

## [0.10.105] - 2026-10-15

### Cat 40 next wave: development, preregistration and confirmation

This release adds the Cat 40 next-wave development harness, development rounds 1 to 3, the d1b gate, the frozen
preregistration (`docs/plans/2026-10-11-cat40-next-wave/PREREG.md`, with Amendment 1 and a cap note), and the
counted confirmation on four new 50,000-document worlds: public P1 and P2, and sealed S1 and S2, whose seeds stay in
owner custody. It also includes the #133 plan and its F2 frozen record.

The two generators ended up testing two different builds. On the public worlds, the build with F5 (owner-phrase
resolution) was ahead of plain files by +12.50 points [+9.17, +15.83] and ahead of the baseline by +4.00, with fewer
wrong values (−3.50, D3 passes). F5 then failed its precision ship condition on `messy-company-v1` (6 of 22 links), so
Part 1 ships without it. On the sealed worlds, where F5 resolves nothing, the build without F5 was ahead of files by
+10.67 [+7.00, +14.50]. It was level with the baseline (−1.17 [−4.33, +2.00]), and D3 fails there. Development round 3
had measured the same no-F5 configuration as level with control. The baseline is ahead of files on both generators
(+8.50 public, +11.83 sealed). The wave's gain over the baseline depends on F5 and probably doesn't transfer to real
brains. No single build ran on both generators, so no single general claim is made. Program spend was $2,863.25 of
$3,400.

The harness changes are limited to the confirmation program (`eval/runner/cat40/next-confirm.ts`,
`next_confirm_analysis.py`), the confirmation seeds, a write-tool race fix in `hard.ts`/`arms.ts` with a forced-probe
test, and the development tooling. See the
[confirmation report](docs/benchmarks/2026-10-15-cat40-next-confirm/README.md).

## [0.10.104] - 2026-10-15

### N14 large-page fidelity after large pages Wave A

The N14 rerun against gbrain master `44eb049` (v0.60.242.0) is hermetic and cost $0. Each 2 MB document and the 20 MB chat is
stored as one page and found 40 of 40 in every decile (0 of 40 at the baseline). Windowed reads around a hit are
correct 40 of 40, the largest 20,871 bytes. Export round trips are exact, and a 1 KB append re-embeds one chunk (1.87
to 2.87 times the appended text, under the preregistered 3x). An older brain's skipped page comes back with
`reindex --oversized`. Of the preregistered rules, Wave A passes all measured here except the egress contract: a trusted
local default `get_page` is still the full page by design, while the agent-facing default read is 23.6 to 35.6 KB.
Pages over 24 MiB are refused, now with `request_too_large` (bug N14-4 fixed), and appends still rewrite the whole
page: both wait for Wave B. Preregistration Amendment 1 adds the upgrade-path case and the agent-facing read. The bug
ledger closes N14-1 and N14-3, fixes N14-4 and narrows N14-2. See the
[Wave A report](docs/benchmarks/2026-10-15-n14-large-page-fidelity-wave-a.md).

## [0.10.103] - 2026-10-14

### D6 proactive brief, development phase: no improvement signal

Cat 40 family P gains the proactive-brief arms. The T0 runner takes `--arms brief-off,brief-on`. Brief-on sets
`context.proactive_brief` after every restore. The paid-arm guard halts the run on any brief in a brief-off cell, and
paid brief cells need `--preregistration`. `eval/runner/t0/brief.ts` reads the brief block, classifies each pushed item
against the gold and summarizes the preregistered primary and diagnostics. There are six new development seeds,
20261201 to 20261206, and a registry row `proactive-brief` (D6).

The [preregistration](docs/benchmarks/2026-10-14-proactive-brief-dev-preregistration.md) was frozen and pushed before
any spend. The run used gbrain v0.60.240.0 with Opus 5.5, Sonnet 5.5 and gpt-6.1-sol, 144 cells, and reports
[no improvement signal](docs/benchmarks/2026-10-14-proactive-brief-dev.md):

- Both arms finished 70/72 paired tasks: a difference of 0 points, 95% interval −5.5 to +5.5. Two of the four
  discordant pairs were provider errors.
- The guard check fails: the brief missed in 14 of 72 brief-on cells. Each miss was a Sonnet session that updated
  pages without calling `remember`, which left the brief no fact to push.
- The brief pushed one item per session, 397 characters at most, with 0 false pushes and no rise in confident-wrong
  answers.

This is development evidence only and does not decide the default. Spend was $27.85 of a new $45 ledger.

## [0.10.102] - 2026-10-14

### D5 brief parameters: the re-smoke passes

After gbrain #6708 fixed `list_write_conflicts`, the D5 brief Cat 40 smoke ran again under a dated
[Amendment 1](docs/benchmarks/2026-10-14-d5-brief-smoke-amendment-1.md). It compared master `3961bf16` (v0.60.232.0)
with gbrain #6703's head `f127b1b5`, using the same rules, tasks, models and arm.

It passes every preregistered check:

- Success was 29/30 on master and 28/30 on the head, within R1. Sol lost B01 and F01 and gained F02, and none of those
  cells used a brief parameter.
- Tool calls were at or below master for every model.
- No cell passed `counterparty` or `intent`.
- There were 0 output leaks and 0 unsafe writes.
- N6 found 0 findings of any kind on either build.

Spend was $6.78 of a new $10 ledger. See the [re-smoke verdict](docs/benchmarks/2026-10-14-d5-brief-smoke/resmoke-1/VERDICT.md).
The first run's verdict stands for its builds.

### The Cat 40 runner scrubs what it writes

Every file the Cat 40 runner writes under `--out` now goes through `scrubMachinePaths`. That covers
`experiment.json`, the receipt, results, attempts, transcripts, judge requests, served instructions and tools, and
`run.log`. The gbrain checkout is recorded as `gbrain@<sha>`, the slot root as `<slots>`, and other paths
repo-relative. A resume still binds to an `experiment.json` written before this change. The re-smoke record is the
first written this way, with no hand edits.

## [0.10.101] - 2026-10-14

### D5 brief parameters: Cat 40 smoke on gbrain #6703

gbrain #6703 adds `counterparty` and `intent` to `context_pack`. A preregistered Cat 40 smoke compared master
`14ea3e2e` with the PR head `e6575894` on Opus 5.5, Sonnet 5.5 and gpt-6.1-sol (10 tasks per model per build, callable
`full`, advertised `starter`). Success was 29/30 on master and 30/30 on the head. Tool calls stayed within the frozen
limit for every model, and no cell passed `counterparty` or `intent`.

An N6 fuzz with a new `counterparty` variant found 0 leaks in `context_pack`'s 540 probes, including the pulled brief.
The frozen verdict is "regresses, on L1 only". Both builds show the same 4 existence findings in
`list_write_conflicts` (#6643, already on master), where the op echoes a foreign `source_id` and returns no rows.

Spend was $6.78 of a new $10 ledger. See the [summary](docs/benchmarks/2026-10-14-d5-brief-smoke.md) and the
[verdict](docs/benchmarks/2026-10-14-d5-brief-smoke/VERDICT.md).

### Machine paths in committed receipts

The D5 record's receipts and experiment files now name builds as `gbrain@<sha>`, slot roots as `<slots>/…` and the
ledger as `.budget/d5-brief-smoke.sqlite`. The receipt machine-path test also now rejects Capy checkout and scratch
paths (`/workspace/…`, `~/.capy/…`, `$HOME/.capy/…`), which home scrubbing leaves in a form the old pattern accepted.
The 404 earlier receipts that contain them are frozen by hash in
`test/eval/fixtures/historical-capy-local-paths.json`.

## [0.10.100] - 2026-10-14

### N14 large-page fidelity: preregistered category and master baseline

New category N14 `large-page-fidelity` asks whether an agent can find and read what's deep inside one very large
document, and whether keeping it up to date stays cheap. The preregistration landed before any counted run. On gbrain
master `c71fe74` (v0.60.225.0), hermetic and at $0, each 2 MB document is stored but unsearchable (keyword recall@10
0 of 120 needles, all present in the stored body), `get_page` returns 1.5 to 2.0 MB, a 20 MB write is refused and a
200 MB write gets a retryable `queue_capacity` it can never pass (bug N14-4). The managed-parts arm (hub plus day
pages) finds 40 of 40 needles in every decile at 2, 20 and 200 MB, but a 1 KB append re-embeds 2.1 to 11.8 times the
appended text. The native arm reports "capability absent" until gbrain ships large-page reads. See the
[baseline report](docs/benchmarks/2026-10-14-n14-large-page-fidelity-baseline.md). Receipts now record a `--gbrain`
overlay as `gbrain@<ref>`, never a checkout path.

## [0.10.99] - 2026-10-14

### Query expansion latency: no expansion on `tokenmax` keeps quality at a ninth of the latency

GBRA-94 compared gbrain's `query` expansion setups on 300 LongMemEval-S questions, with embeddings and the reranker
frozen at the proxy so that only expansion varied ([preregistration and results](docs/benchmarks/2026-10-14-expansion-latency-preregistration.md)).

- **No expansion passes the preregistered rule and is fastest:** strict recall@10 299 → 298 (the reference's own re-run
  also scored 298), strict@5 287 → 285, nDCG@10 +0.0008, and end-to-end query time 2,022 → 227 ms p50 (2,292 → 384 ms
  p95). No expanding arm answered a question that the no-expansion arm missed.
- **Faster expansion models don't close the gap.** `claude-haiku-5-5` is 7% faster at p50 and 6x cheaper, but slower at
  p95. `gpt-6-luna` and `gemini-3.8-flash` are slower than Haiku 4.5 at their default reasoning, and Gemini fails nDCG
  on its 90-question screen.
- **Skipping expansion on pasted passages (≥30 words)** changes no score; a short-keyword rule fires on 1 query on this
  set.
- Spend about $4.71 of a $5 cap. This recommends a setting; it does not change gbrain's default.
- **Test flake fix:** the Cat 40 Hard 50k ledger test (`test/eval/cat40-hard.test.ts`) generates two 50k ledgers per
  seed, CPU-bound, and timed out at bun's 5 s default on a busy CI runner (5.6 s). It now has a 60 s test timeout, like
  the file's other heavy test; no assertion changed. Measured on a 4 vCPU cloud machine, Bun 1.4.3, one run each: 3.9 s
  idle; pinned to one CPU shared with two busy loops, it timed out at 5 s before the change and passed in 10.4 s after.

## [0.10.98] - 2026-10-14

### F5 owner-phrase precision on messy-company-v1: FAIL

gbrain's F5 owner-phrase linking at gbrain `4e10136b` derived 6 links across both splits of messy-company-v1. All 6
were correct, but 6 is below the 22-link minimum, and the Wilson 95% lower bound of 0.610 is below the 0.85 bar, so
the ship condition fails. Recall was 2 of 66 should-link phrases on dev and 4 of 58 on held-out, with 0 links on
should-not-link rows. The [run record](docs/benchmarks/2026-10-14-f5-messy-company/README.md) has the decision rule
(sha256 `6ca46ba4…0b11`), the scores and the scripts as run. The dataset's [USES.md](eval/data/messy-company-v1/USES.md)
now lists the run and records that the owner-phrases held-out split has been used once.

## [0.10.97] - 2026-10-14

### messy-company-v1: a frozen messy-company dataset with gold for 9 lanes

New reusable dataset [`eval/data/messy-company-v1`](eval/data/messy-company-v1/README.md): a fictional company
knowledge base of 226 pages (118 dev, 108 held-out, split by account cluster) with gold labels for owner phrases,
entity mentions, aliases, ownership windows, governing records, document status, timelines, changes and agent tasks.
`gpt-6.1-sol` and `gemini-4-argon` wrote the pages, each checked by the other model. 91 of 1,740 labeled items
disagreed (5.2%), and every disagreement was adjudicated by reading the page. Gold comes from the world plan's oracle,
never from a model. `validate-data` now fails if any data file drifts from the frozen manifest (dataset hash
`4a6bd099…4568`). It adds a loader, nine scorers and tests. Model spend was $4.45.

## [0.10.96] - 2026-10-14

### Cat 41 fifth-run report: reading times corrected

The [fifth setup report](docs/benchmarks/2026-10-14-cat41-setup-run5.md) said C r1 and C r2 spent 26.2 and 15.0 s
reading the install guide, against 4.5 and 4.6 s in the fourth run. Those numbers came from tables built two
different ways. Measured the same way, the guide reads took 14.4, 16.9 and 10.2 s against 14.5, 6.9 and 8.2 s. Only C
r2 read for longer, after its own `ls` exited 2 and cut its first fetch short. The report has a dated correction note
and a rebuilt "Where the time went" table. A new descriptive appendix gives the C runs' path through gbrain's docs,
and a phase split of the wired-recall runs against the fourth run. No verdict, score or results artifact changed.

## [0.10.95] - 2026-10-14

### Cat 41 setup, fifth run: first push met on v0.60.219.0

The fourth run's preregistered design, unchanged except the gbrain version (scorer `cat41-score-v8`,
[preregistration](docs/benchmarks/2026-10-14-cat41-setup-run5-preregistration.md) at `b2e32ccb`, approved by GBRA-40
before any paid cell). On v0.60.219.0, with `claude-opus-5-5`, 3 runs per cell and the frozen targets:
- First push: met, 3/3. The SessionStart hook printed the preference into every fresh session, and no agent also
  saved it to Claude Code's own memory.
- Wired recall: missed, 60.2 s against 60 s.
- Consent: met, 0 provider requests.
- Faster setup: missed, 2.8% (the same on reading).

No `setup` run ran `gbrain apply-migrations` by hand, and a positional `gbrain recall "<question>"` returned the saved
fact in all 3 D runs. The fourth run's verdicts stand. $6.56 of a $10 ledger cap
([result](docs/benchmarks/2026-10-14-cat41-setup-run5.md)).

## [0.10.94] - 2026-10-13

### Vector side alongside the keyword arms: about 150 ms faster per search on a 20,000-page Postgres brain

gbrain v0.60.214.0 (gbrain#6641) starts the query embed and expansion with the keyword arms instead of after them
([report](docs/benchmarks/2026-10-13-vector-side-early.md)). Median warm `search` went from 578 / 572 ms to
424 / 402 ms and `query` from 578 / 548 ms to 448 / 428 ms on a 20,000-page Postgres brain with Voyage. On a 400-page
PGLite brain the saving is only the 13 to 15 ms the keyword arms take. Results are unchanged: the bench digests match
master, and with stub providers on the 20k brain all 80 result lists match. About $0.40 in provider calls.

## [0.10.93] - 2026-10-13

### Reranker settings addendum: rerank-3-lite at the shipped shape cuts rerank cost 60% with no loss

GBRA-86 re-ran the frozen LongMemEval-S candidate lists (300 questions) under Voyage `rerank-3` and `rerank-3-lite`,
with a fresh reference run and per-query reranker latency ([addendum](docs/benchmarks/2026-10-13-rerank3-addendum-preregistration.md)).

- **`rerank-3-lite`, 50 candidates × 1,400 tokens, passes the preregistered rule:** strict recall@10 299 → 298,
  strict@5 288 → 289, nDCG@10 −0.0012, and rerank cost $1.51 → $0.60 per 1,000 queries (−60%). Reranker latency is
  about the same (p50 232 → 251 ms, p95 596 → 604 ms).
- **`rerank-3` at the same shape** passes at today's price and has the best strict@5 (291).
- **Cutting candidates to 25 or 15** takes 8–17% off p50 latency but loses 3–5 questions on strict@10 with either
  model, so it fails, as in 0.10.84.
- **The reference reproduced:** fresh `rerank-2.5` calls jittered scores by up to 0.003 and flipped no question.
- Spend about $3.74 of a $5 cap. This recommends a setting; it does not change gbrain's default.

## [0.10.92] - 2026-10-13

### Receipt source-tree hash reads only changed files

The intermittent 2-failure run of the receipts tests (`round-trips atomically` timed out, then `writeReceipt stores
the executed source tree` saw `dirty: null`) came from `sourceTreeIdentity`. The first receipt in each process
hashed every byte of the evals tree, about 1.7 GB of committed artifacts: 1.4 s warm, 2.3 s cold and over 5 s under
load on a 4-core machine, inside a test with Bun's 5 s timeout. A timeout during `git status` also left `dirty: null`
cached for the rest of the process.

- The hash now takes each file's blob id from git's index when `git status` reports the file unchanged, and reads
  and hashes (as a git blob) only changed and untracked files: 0.1 to 0.4 s warm, 0.6 to 0.7 s cold under load.
  For the evals tree and for clones with modified, untracked, deleted, staged, renamed, touched and copied files,
  the result matched a full read of every file.
- The field is versioned. New receipts write `execution.source_tree.scheme: "git-index-blob-v1"` next to `sha256`,
  which is sha256 over (name, git blob id). Receipts written before v0.10.92 have no `scheme`; readers
  (`sourceTreeScheme`) treat them as `legacy-full-read`, sha256 over (name, size, bytes). The validator accepts
  `git-index-blob-v1` or no scheme and rejects anything else. Hashes from the two schemes are not comparable, and
  nothing in the repository compares them. A test pins both: a new receipt carries the scheme, and a legacy receipt
  without one still validates and loads.
- A failed or interrupted git call returns an identity with an error and is no longer cached. A new test makes
  `git status` fail once and checks that the next call hashes the tree.

No assertion or timeout was loosened. A forced probe (cold page cache plus six CPU hogs, the targeted receipts
command, default timeout) failed all 6 trials before the fix and passed all 9 after.

## [0.10.91] - 2026-10-13

### Cat 41 setup, fourth run: push delivers a preference; first push 1/3

A new preregistration, written after the v0.60.208.0 results and approved by Garry, made three changes (scorer
`cat41-score-v8`): a world-visible preference ("I take my coffee black, with a pinch of cardamom") as the first-push
item, any unambiguous form of the expected date, and an agent's save-and-recall smoke fact counted as its exempt