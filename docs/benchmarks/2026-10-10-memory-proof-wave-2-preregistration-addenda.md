# Memory proof wave 2 preregistration: addenda

The [preregistration](2026-10-10-memory-proof-wave-2-preregistration.md) was pushed at commit `442bb366` and verified by its SHA-256, `baf0ec0ee49f51062a17e5978d7206ead04d8bc55ca5805b4b7d8a13a922932a`. Later decisions are recorded here, dated, instead of editing that file. Each one is written before the cells it governs run.

## Every dev and confirmation cell sets its knobs explicitly (October 11, 2026)

**Decision (Garry, October 11).** From stage 2 on, every gbrain cell sets every read-time and ingest knob explicitly. No cell relies on the pinned build's defaults.

**Why.** Master's defaults changed when gbrain#6066 shipped with the query facts arm on. Before that merge, master had no facts arm and no temporal fact reserve; #6066 added both keys, with the facts arm on by default. Step 0's specs take those knobs from the build: the facts arm on, the reserve off, date grounding on, the voyage-4 supersession threshold 0.95. `search.mode` comes from the unit's keys. Those values match the wave-1 build `d7467d1cf` and the dev pin. A cell that names them keeps its meaning if a later build changes a default.

**Read-time knobs.** These go in `provider_config.search_config` and are set in each unit's brain before its server starts. They are not ingest inputs, so lanes that differ only here share a store.

| Key | Value | Notes |
|---|---|---|
| `search.mode` | `tokenmax` on every facts-store lane; `conservative` on `raw@pin` | wave 1's modes, which came from the unit's keys |
| `search.reranker.enabled` | `true` with `tokenmax`, `false` with `conservative` | the mode bundles' values |
| `search.reranker.model` | `voyage:rerank-2.5` | the bundle default |
| `search.reranker.gate` | `off` | `on` only on `combined-v2+gate`, `shadow` only on the A15 replay |
| `search.reranker.gate_min_gap` | `0.05` | the build default; inert with the gate off; A15 picks δ from {0, 0.05} |
| `search.query_facts_arm` | `true` | on in wave 1 and at the pin |
| `search.temporal_fact_reserve` | `false` | failed validation in wave 1 ([addendum](2026-10-05-memory-proof-wave-preregistration-addenda.md#temporal-fact-reserve-validation-verdict-october-7-2026)) |
| `search.evidence_date_header` | `false` | the harness writes its own date header on each page |
| `search.entity_anchoring` | `false` | off in wave 1 |
| `recall.question_admission` | `reserve`, except the `facts_arm` tuning lane | W1's admission rule (below) |

**Ingest knobs.** These go in `provider_config.gbrain_config` and are set on the store template before ingest. They are ingest keys, so they are part of each store's identity.

| Key | Value |
|---|---|
| `extraction.date_grounding` | `true` |
| `facts.attribution` | `true` |
| `facts.supersession_thresholds` | `{"voyage:voyage-4@1024": 0.95}` |

The raw store sets the same keys. With no extraction, they have no effect there.

**Per call.** The harness already sends `expand: false` on every page query. Every lane's `query` call passes `token_budget` without `return_unit: "auto"`, so `search.auto_packing` never applies and is not set.

**Enforcement.** [`tests/test_mpw2_dev_specs.py`](../../eval/harness-provider/tests/test_mpw2_dev_specs.py) fails if any spec under `cells/mpw2/dev/` or `cells/mpw2/confirm/` lacks a key above, uses another mode or reranker setting for its lane, or fails the provider's config validation. The specs are written by [`mpw2-dev-specs.py`](../../eval/harness-provider/mpw2-dev-specs.py).

Step 0 keeps its specs as they ran, and stays exploratory.

## Dev pin: #6445 merged with master v0.60.169.0 (October 11, 2026)

**Decision (Garry, October 11).** Every dev cell runs on gbrain `8d4f6ab6e589df8b59bedd791cffb8092540b646`. This replaces the preregistration's "head of the W1 PR (PR-A)" and the earlier pin, `f44a0947808334d4187fd0842af265c6c31d9fb5`.

**Why.** W1 merged to master as v0.60.169.0 (merge `77cf8e111`, migration v237, with concurrent index builds), so dev measures the build that ships. `8d4f6ab6e` is gbrain#6445 (W3) with that master merged in. It holds:

- the shipped W1;
- the wave-1 defaults;
- W3 stage 1, with `search.reranker.gate` defaulting to `off`.

The A15 shadow probe needs W3 stage 1, so it can replay these stores with `search.reranker.gate: shadow` without a second build. Verified: `8d4f6ab6e` contains both `77cf8e111` and #6445's previous head `a2a08a15`, and its `VERSION` is `0.60.169.0`. Its local suites passed. GitHub CI on #6445 was queued when this was written. Dev does not wait for it. The record for this pin reads "GitHub CI: queued at pin time; local suites passed".

The counted pin (PR-B's head) is still recorded in its own addendum, before any counted cell.

## Dev cells and their caps (October 11, 2026)

Dev runs in five groups. Each group has its own VM and its own ledger, so groups run in parallel. In each group, the cell that builds a store runs first.

| Group | Questions | Cells, in run order | Ledger cap |
|---|---|---|---:|
| `dev-lme` | LongMemEval-S dev, 100 | `combined-v2` (builds the measured-default store), `raw@pin` (builds the raw store), `combined-v2` with `facts_arm` admission, `combined-v1@pin`, `filler-removed`, `recall-one-call` | $20 |
| `dev-locomo` | LoCoMo10 `conv-42`, `conv-44`, 322 | `combined-v2`, `raw@pin`, `combined-v2` with `facts_arm`, `combined-v1@pin`, `recall-one-call`, gpt-6-luna `combined-v1@pin` | $32 |
| `dev-beam-100k` | BEAM 100k {3, 11}, 40 | `combined-v2`, `combined-v2` with `facts_arm`, `combined-v1@pin`, `recall-one-call`, `cost-matched` (7,560 tokens), gpt-6-luna `combined-v1@pin` | $10 |
| `dev-beam-500k` | BEAM 500k {12, 21, 28, 31}, 80 | as 100k; `cost-matched` at 7,665 | $20 |
| `dev-beam-1m` | BEAM 1M {16, 21, 22, 25}, 80 | as 100k; `cost-matched` at 7,846 | $21 |

The ledger caps total $103. The A15 shadow probe's Voyage-only replay, about $1, takes the stage to about $104.

- **Delivered totals.** Each lane delivers 8,100 tokens: `combined-v2` packs the facts block (1,800 on LongMemEval-S and LoCoMo10, 600 on BEAM) and the pages under 8,100; `combined-v1@pin` gives pages 8,100 minus the block; `filler-removed`, `raw@pin` and `recall-one-call` give 8,100 to pages or to gbrain's packer. `cost-matched` is `combined-v2` at the comparator's mean delivered total on that BEAM split in wave 1's sealed cells.
- **Admission rule.** W1 shipped `recall.question_admission` with two rules: `reserve` (the default) and `facts_arm`. Dev picks the rule with the higher `combined-v2` mean over all 422 LongMemEval-S and LoCoMo10 dev questions plus the 200 BEAM dev questions, each question weighted equally. A tie keeps `reserve`, the shipped default. The pick is recorded here before any counted cell. The decision lanes (`recall-one-call`, `cost-matched`) run at `reserve`.
- **The gpt-6-luna continuity row** on LongMemEval-S is step 0's arm comb, which is `combined-v1` on a gpt-6-luna store (build `59782b95`). It is not rerun at the pin, which saves about $10. It is descriptive and decides nothing.
- **Judging.** Dev lanes are judged in-cell by the preregistered judge. Dev decides tuning, not gates, so there is no joint re-judge in stage 2.
- **Refusal.** A cell whose cap exceeds what is left on its group's ledger is refused and reported, not shrunk.
- **Custody.** Each group's ledger is copied to `~/.capy/work/mpw-ledgers/wave2/<group>.sqlite` on the integrator's primary machine after every cell, with SHA-256 checked on both sides.
