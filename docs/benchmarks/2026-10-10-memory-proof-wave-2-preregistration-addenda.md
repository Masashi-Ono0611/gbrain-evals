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

## Step 0 result: mode dominates, so the wave pauses (October 11, 2026)

**Rule 1 fires, so the wave pauses for Garry's decision.** On the 100 LongMemEval-S dev questions, switching the combined store's search mode from `tokenmax` to `conservative` gains 13 points. Removing the facts block, and returning its space to pages, changes the score by −1 and 0 points. This result is exploratory: step 0 ran on #6066's head, `59782b95`, with the knobs listed in its specs, and it decides scope only. No dev cell has run.

The figures below come from the joint blinded re-judge of all five arms. The judge was `gemini-3.5-flash`. The in-cell judges gave 79, 81, 81, 93 and 90 in the table's order. The re-judge moves comb up 2 and arms a and b down 1 each, so rule 1 fires on either set.

| Arm | Correct | Abstentions | Delivered tokens (mean / p95) | Cell |
|---|---:|---:|---|---|
| comb | 81 | 22 | 8,128 / 8,156 | `longmemeval-s-gbrain-rag-95369ca39b74` |
| a: block removed | 80 | 21 | 6,335 / 6,363 (below the context gate, by design) | `longmemeval-s-gbrain-rag-0c561a6a744f` |
| b: space returned | 80 | 20 | 8,142 / 8,175 | `longmemeval-s-gbrain-rag-77c9ebfbf567` |
| d: `conservative` | 93 | 12 | 8,058 / 8,105 | `longmemeval-s-gbrain-rag-a1bbbca4a86b` |
| raw | 90 | 14 | 8,052 / 8,098 | `longmemeval-s-gbrain-rag-367592ede32e` |

The gap is raw − comb = 9 points. It splits into four parts. The intervals are paired bootstrap 95% intervals over questions, 9,999 draws, seed `20261010`.

| Part | Points | 95% interval |
|---|---:|---|
| store (raw − d) | −3 | −7 to 0 |
| mode (d − b) | +13 | +6 to +21 |
| page space (b − a) | 0 | −3 to +3 |
| facts block (a − comb) | −1 | −5 to +2 |

- **Rule 1 (mode dominates): fires.** (d − b) = +13 is positive and larger than (b − comb) = −1.
- **Rule 2 (proceed): not reached.** It would fail anyway, because (b − comb) = −1 is below half the gap.
- **Where the gain is.** Multi-session questions account for most of it: 19 of 22 correct under `conservative` against 11 of 22 under `tokenmax`, with the same store and the same 8,100-token page budget. Temporal reasoning goes from 21 to 23 of 27. Every other question type is within one question.
- **What the mode switch changes.** The harness already sends `expand: false`, so query expansion is not part of the difference. The page budget is also the same in both arms, because the caller's `token_budget` overrides each bundle's own budget. Under `tokenmax`, the bundle also turns on these, each of which `conservative` leaves off:
  - the cross-encoder reranker, `voyage:rerank-2.5`, over the top 50;
  - a search limit of 50 instead of 10;
  - graph signals;
  - relational retrieval and its planner;
  - `per_chunk_synopsis` contextual retrieval.

  Step 0 does not isolate which of these costs the points.
- **The facts store helps a little.** With the mode held at `conservative`, the combined store scores 3 points above the raw store. The interval reaches 0, so this is not established.

**Spend.** Step 0 committed $15.14 on its ledger and the joint re-judge $1.30, for a total of $16.44 of the $18 released. Receipts:

- the cells under [`2026-10-10-memory-proof-wave-2/step0/cells/`](2026-10-10-memory-proof-wave-2/step0/cells/);
- the re-judge, with its analysis, under [`step0/rejudge/`](2026-10-10-memory-proof-wave-2/step0/rejudge/).

The ledgers are mirrored to the integrator's primary machine with matching SHA-256:

- `step0.sqlite`: `aa646c6b…`;
- `step0-rejudge.sqlite`: `a4366da6…`.

The step-0 VM is destroyed and recorded in `VMS.md`.

## The wave pauses for re-scope; a mode isolation runs first (October 11, 2026)

**Decision (Garry, through the integrator, October 11).** Step 0's mode-dominates rule fired, so the wave is paused for re-scope. Stage 2 as written above (the dev groups and their caps) does not start. Before the re-scope, one exploratory isolation runs to find which part of `tokenmax` costs the 13 points. It is diagnosis, not a gate, and its result goes to Garry with the re-scope decision.

**Scope.** LongMemEval-S dev only, the same 100 questions. No BEAM, LoCoMo10 or other dev cell runs.

**Build and store.**
- Build: the dev pin, `8d4f6ab6e589df8b59bedd791cffb8092540b646`.
- Store: one measured-default store (Claude Haiku 5.5 extraction, credentials `voyage` and `anthropic`), with the ingest knobs of the explicit-knob addendum. All arms read this one store.
- The first arm, `b`, runs under `tokenmax` and builds the store. A markdown import embeds pages under the inline contextual-retrieval tier of the mode active at ingest, with `per_chunk_synopsis` demoted to `title`. So this store, like step 0's combined store, is embedded at the `title` tier.

**Arms.** Each arm starts from the explicit read-knob set above, with the facts block removed and 8,100 page tokens, unless noted. Specs: `cells/mpw2/iso/`, written by [`mpw2-iso-specs.py`](../../eval/harness-provider/mpw2-iso-specs.py).

| Arm | Mode | Change |
|---|---|---|
| `b` | `tokenmax` | none (step 0's arm b, at the pin) |
| `d` | `conservative` | none (step 0's arm d, at the pin) |
| `comb` | `tokenmax` | wave-1 combined packing: 1,800-token block plus 6,300 page tokens |
| `t-rerank-off` | `tokenmax` | `search.reranker.enabled: false` |
| `t-limit-10` | `tokenmax` | `search.searchLimit: 10` (from 50) |
| `t-relational-off` | `tokenmax` | `search.relational_retrieval: false`, `search.relational_planner: false` |
| `t-graph-off` | `tokenmax` | `search.graph_signals: false` |
| `t-cr-none` | `tokenmax` | `search.contextual_retrieval: none` |
| `c-rerank-on` | `conservative` | `search.reranker.enabled: true` |

`search.contextual_retrieval` is read only at embed time, and no read path consults it. So `t-cr-none` is expected to match `b`, and it doubles as a same-configuration noise check. `c-rerank-on` separates the reranker on its own from the reranker over tokenmax's larger candidate set.

**Analysis.** One joint blinded re-judge covers all nine arms, with the preregistered judge. For each arm, the analysis reports:
- the paired difference from `b`;
- the paired difference from `d`;
- the share of (d − b) that the arm recovers.

The intervals are paired bootstrap 95% intervals over questions, 9,999 draws, seed `20261010`. Results are broken out by question type, with multi-session and temporal reasoning first. Nothing here is a gate.

**Budget.** The cells run on their own ledger, capped at $23: the store about $9.50, plus eight reads at about $1.30. The re-judge is capped at $2.50. Both come out of the dev release. Ledgers are mirrored to the integrator's primary machine with SHA-256 checked, and the VM is recorded in `iso/VMS.md` and destroyed afterwards.

## Isolation finding, and a two-way `tokenBudget` test (October 11, 2026)

**Finding.** None of the five tokenmax components accounts for the mode gap when it is switched off on its own. The default that does is a sixth one, which the isolation did not switch: the mode bundle's `tokenBudget`, which is 4,000 in `conservative` and unset in `tokenmax`. The in-cell judge (`gemini-3.5-flash`, complete on all 900 answers) gives these scores on the isolation store. The comparisons are paired 95% intervals against `b`.

| Arm | Correct | Change vs `b` | Multi-session (22) | Temporal reasoning (27) |
|---|---:|---|---:|---:|
| `b` tokenmax | 83 | — | 11 | 22 |
| `d` conservative | 91 | +8 (0 to +16) | 19 | 22 |
| `comb` | 82 | −1 (−4 to +2) | 12 | 21 |
| `t-rerank-off` | 82 | −1 (−3 to 0) | 11 | 22 |
| `t-limit-10` | 83 | 0 (−3 to +3) | 11 | 22 |
| `t-relational-off` | 83 | 0 | 11 | 22 |
| `t-graph-off` | 83 | 0 | 11 | 22 |
| `t-cr-none` | 84 | +1 (0 to +3) | 12 | 22 |
| `c-rerank-on` | 87 | +4 (−1 to +10) | 15 | 22 |

**Mechanism, from the code at `8d4f6ab6e` and the retrieval receipts.**

- The harness asks for `return_unit: "page"`. With an evidence plan like that, `query` does not pass the call's `token_budget` down to ranking (`src/core/ops/search.ts:981`: `tokenBudget: !plan && … ? p.token_budget : undefined`). The call's budget applies only later, when pages are packed for delivery.
- So ranking cuts its hits to the mode's own `tokenBudget` (`src/core/search/hybrid/rank.ts:487`, `enforceTokenBudget(sliced, resolvedMode.tokenBudget)`). That cut decides how many pages reach delivery.
- Under `conservative`, the cut is 4,000 tokens of hits, and 8.4 pages per question reach delivery on average. Each page is delivered whole within the 8,100-token budget; one session ran to 19,199 characters.
- Under `tokenmax`, nothing is cut, and 47.6 pages per question compete for the same 8,100 tokens. About 16 are delivered as fragments of roughly 600 tokens each, and 31.6 are dropped.
- So `tokenmax` gives the answer model slivers of many sessions instead of whole sessions. Multi-session questions lose the most: 11 against 19 of 22.
- The receipts agree on every arm. `d` and `c-rerank-on` deliver 8.4 and 8.2 pages per question. `b` and every tokenmax single-flip arm deliver 47.6 candidates.
- The harness sends `limit: 50` on every call, so `search.searchLimit` cannot change the candidate count. That is why `t-limit-10` was a no-op.
- Graph signals, relational retrieval and the contextual-retrieval read knob leave 85 to 92 of 100 contexts identical to `b`. A known no-op (`t-cr-none`) leaves 86, so those three are within noise. Turning the reranker off changes all 100 contexts but not the score.
- Within `conservative`, adding the reranker changes which 8 pages survive the cut and costs about 4 points: `c-rerank-on` −4 against `d`, interval −10 to +2.

**Two-way test (Garry, through the integrator, October 11).** The claim is tested in both directions on one rebuilt store of the same identity, `gbrain-longmemeval-s-e1c9dfc782e7`, at `8d4f6ab6e`.

| Arm | Mode | Change | Expected |
|---|---|---|---|
| `b` | `tokenmax` | none (builds the store) | reference |
| `d` | `conservative` | none | reference |
| `t-tb-4000` | `tokenmax` | `search.tokenBudget: 4000` | recovers toward `d` |
| `c-tb-unset` | `conservative` | `search.tokenBudget: 10000000` | falls toward `b` |

`search.tokenBudget` accepts only a positive integer. So "unset" is a budget that no ranked list reaches, which matches `tokenmax`'s undefined budget.

The four arms get their own joint blinded re-judge. The scope is LongMemEval-S dev only, and the result is exploratory. The cells run on their own ledger, capped at $16: the store about $11, plus three reads at about $1.30. The re-judge cap is $2.00, sized for the $0.59 per-call reservation; its actual spend is about $1.10. Specs are in `cells/mpw2/iso2/`, written by `mpw2-iso-specs.py`. Ledgers are mirrored, and the VM is recorded in `iso2/VMS.md` and destroyed afterwards.

**Isolation re-judge cap.** The isolation's joint re-judge refused 107 of its 900 answers at $1.91 committed of its $2.50 cap. Each judge call reserves a worst case of $0.59, against an actual cost of about $0.003. With Garry's approval, the cap was raised to $3.00 for reservation headroom only. The reason is recorded in that ledger's cap change. Actual spend stays near $2.21.

## Two-way `tokenBudget` result: the ranking cut explains the mode gap (October 11, 2026)

**The mode's `tokenBudget` cut explains the gap in both directions.** Giving `tokenmax` the 4,000-token cut recovers 6 of the 10 points. Removing the cut from `conservative` loses 8 of them. Multi-session follows the cut exactly when it is removed. The result is exploratory, LongMemEval-S dev only, on one rebuilt store at `8d4f6ab6e`.

The scores come from the joint blinded re-judge of the four arms. Intervals are paired bootstrap 95% intervals over questions, 9,999 draws, seed `20261010`.

| Arm | Score | vs `b` | vs `d` | Multi-session (22) | Temporal reasoning (27) | Pages reaching delivery per question |
|---|---:|---|---|---:|---:|---:|
| `b` tokenmax | 80 | — | −10 (−19 to −2) | 11 | 20 | 47.6 (16.0 delivered, 31.6 dropped) |
| `d` conservative | 90 | +10 (+2 to +19) | — | 18 | 22 | 8.3 |
| `t-tb-4000` tokenmax, cut 4,000 | 86 | +6 (0 to +13) | −4 (−10 to +1) | 14 | 22 | 8.2 |
| `c-tb-unset` conservative, no cut | 82 | +2 (0 to +5) | −8 (−16 to 0) | 11 | 21 | 47.6 (16.2 delivered, 31.4 dropped) |

- **The knob alone sets how many pages reach delivery.** `t-tb-4000` delivers the same 8.2 pages per question as `d`. `c-tb-unset` has the same 47.6 candidates as `b`. Everything else about each mode is unchanged.
- **Removing the cut from `conservative` drops multi-session to exactly `b`'s 11 of 22.** Adding the cut to `tokenmax` lifts it from 11 to 14.
- **The rest of the gap is the reranker.** Under the cut, the reranker picks which 8 pages survive, and that costs about 4 points. `t-tb-4000` scores −4 against `d`, and in the isolation `c-rerank-on` also scored −4 against `d` (87 against 91).
- **The isolation's joint re-judge, now complete on all 900 answers, gives the same picture as its in-cell judge.** `b` 83, `d` 91, `c-rerank-on` 87, and every single tokenmax flip 80 to 83.

**Spend on the wave-2 ledgers (dev release).**

| Item | Spend |
|---|---:|
| Isolation cells | $21.57 |
| Isolation re-judge | $2.23 |
| Two-way cells (store $11.0) | $14.73 |
| Two-way re-judge | $1.05 |
| **Total** | **$39.58** |

Receipts are under `2026-10-10-memory-proof-wave-2/iso/` and `iso2/`. Ledgers are mirrored to the integrator's primary machine with matching SHA-256: `iso.sqlite` `206d2e2f…`, `iso-rejudge.sqlite` `1a5057b5…`, `iso2.sqlite` `ddb723f9…`, `iso2-rejudge.sqlite` `3f37128a…`. Both VMs are destroyed and recorded.

## Re-scope: W5 honors the caller's budget in page mode (October 11, 2026)

**Decision (Garry, through the integrator, October 11).** Step 0's mode-dominates rule fired, and the wave paused for re-scope. The isolation and the two-way test (both above) traced the 10-point mode gap to one cause. Under `return_unit: "page"`, ranking cuts candidates to the mode's `tokenBudget` instead of the caller's budget. Garry chose option 1: make page-mode ranking honor the caller's budget.

**W5** is that change. It is built on gbrain#6445's branch beside W3. It adds one `search.*` key, off by default. When the key is on, page-unit ranking candidates are capped at `min(mode cut, ratio × caller token_budget)`, and the applied cut is reported in `_meta`. The wave now covers:

- W1, shipped in v0.60.169.0;
- W3, the rerank gate, stage 1, with its shadow probe pending;
- W5.

The dev pin moves to the head of #6445 once W5 is on it. The next addendum records the SHA and the W5 key's exact name before any W5 cell runs.

### W5 dev tuning (exploratory, LongMemEval-S dev only)

**Store.** One measured-default LongMemEval-S dev store at the new pin, with the explicit knobs below.

**Arms.** Six arms, all `filler-removed` (no facts block, 8,100 page tokens):

| Arm | Mode | W5 | `search.tokenBudget` |
|---|---|---|---|
| `b` | `tokenmax` | off | unset (`10000000`) |
| `d` | `conservative` | off | `4000` |
| `w5-0.40` | `tokenmax` | on, ratio 0.40 (cap 3,240 tokens) | unset |
| `w5-0.50` | `tokenmax` | on, ratio 0.50 (cap 4,050) | unset |
| `w5-0.75` | `tokenmax` | on, ratio 0.75 (cap 6,075) | unset |
| `w5-1.00` | `tokenmax` | on, ratio 1.00 (cap 8,100) | unset |

`b` builds the store. All six arms get one joint blinded re-judge with the preregistered judge.

**Ratio rule, fixed before the run.** Among the four W5 arms, pick the one with the most multi-session questions correct (of 22) on the joint re-judge. The choice is subject to all of the following:

1. its overall score is at least `b`'s;
2. in every other question type, it is within 1 question of `b`;
3. it beats `b` on multi-session by at least 2 questions.

Ties go to the higher overall score, then to the larger ratio, which is the smaller change from the caller's budget. If no ratio passes, W5 does not go to the counted gates, and Garry decides. The chosen ratio is recorded here before any counted W5 cell runs.

**Budget.** About $20: the store about $11, five reads at about $1.30, and the re-judge about $1.60 (cap $2.50, sized for the $0.59 per-call reservation).

### W5 gate on BEAM

The BEAM data is the 72 non-dev conversations. Under GBRA-49's ruling, it is regression and descriptive evidence, reused, not held-out confirmation.

- **Lanes.** `combined-v2` with W5 off, and `combined-v2+w5` with W5 on at the dev-chosen ratio. Both use the same pin and the same store; only the read differs.
- **Statistic.** Gate 2's: wave 1's restricted wild cluster bootstrap-t, stratified by size, with conversations as clusters (Webb six-point weights, 9,999 draws, seed `20261010`), on the joint BEAM re-judge.
- **Pass.** Both conditions must hold:
  - the one-sided 95% lower bound of (W5-on − W5-off), pooled, is above −3 points;
  - no question kind's two-sided 95% interval lies entirely below −3 points (TC6), across multi-session, contradiction, temporal, event ordering and abstention.
- **A pass flips the default.** The W5 key ships on, at the dev-chosen ratio. A failure keeps it off, and the result is reported as measured.
- The pooled point estimate and the multi-session difference are reported beside the gate, whichever way it lands.

### Knob table for every stage-2 and stage-3 arm

Every arm sets these keys explicitly in `search_config`, on top of the ingest keys in the explicit-knob addendum. This replaces that addendum's read-time table.

| Key | Value |
|---|---|
| `search.mode` | `tokenmax` on facts-store lanes; `conservative` on `raw@pin` |
| `search.tokenBudget` | `10000000` with `tokenmax` (the bundle's unset budget; the key takes only a positive integer); `4000` with `conservative` |
| W5's key | off, except on `combined-v2+w5` and the W5 tuning arms |
| `search.reranker.enabled`, `search.reranker.model` | `true` with `tokenmax` and `false` with `conservative`; `voyage:rerank-2.5` |
| `search.reranker.gate`, `search.reranker.gate_min_gap` | `off`, `0.05` (`shadow` only on the A15 replay, `on` only on `combined-v2+gate`) |
| `search.query_facts_arm`, `search.temporal_fact_reserve` | `true`, `false` |
| `search.evidence_date_header`, `search.entity_anchoring` | `false`, `false` |
| `recall.question_admission` | `reserve`, except dev's `facts_arm` tuning lane |

`tests/test_mpw2_dev_specs.py` is extended to require `search.tokenBudget` and W5's key once the pin addendum names it. The dev specs are regenerated at the new pin.

### Dev and confirmation, re-planned

**Dev changes from the dev-cells addendum.**

- The dev groups run at the new pin with the table above.
- The LongMemEval-S dev group reuses the W5 tuning store, so it does not build a store of its own.
- The gpt-6-luna continuity rows on BEAM and LoCoMo10 are dropped. Step 0's arm comb remains the gpt-6-luna continuity row.
- A `combined-v2+w5` lane runs on each BEAM dev split at the chosen ratio, as a dev check before the BEAM gate.
- The A15 shadow probe runs on the rebuilt BEAM dev stores, as before.

**Confirmation changes.**

- `filler-removed@pin` is dropped: step 0 showed that removing the facts block changes nothing at this budget (a − comb −1, b − a 0).
- LoCoMo10's `raw@pin` is dropped. Gate 1 reads LongMemEval-S only, so LoCoMo10's raw lane was descriptive.
- `combined-v2+w5` is added on BEAM non-dev for the W5 gate.

**Budget within the $650 cap.**

| Line | Status | USD |
|---|---|---:|
| Step 0, five arms and re-judge | spent | 16.44 |
| Mode isolation, nine arms and re-judge | spent | 23.80 |
| Two-way `tokenBudget` test, four arms and re-judge | spent | 15.78 |
| W5 dev tuning, LongMemEval-S | next, released by this amendment | 20 |
| Dev at the new pin: BEAM 100k / 500k / 1M and LoCoMo10 groups, the LongMemEval-S group on the tuning store, `combined-v2+w5` BEAM dev checks, A15 probe | released after the W5 pick | 92 |
| Confirmation: LongMemEval-S (ingest, `combined-v1@pin`, `combined-v2`, `raw@pin`) | behind Garry's go | 50 |
| Confirmation: LoCoMo10 (ingest, `combined-v1@pin`, `combined-v2`) | behind Garry's go | 33 |
| Confirmation: BEAM non-dev (ingest, `combined-v1@pin`, `combined-v2`) | behind Garry's go | 120 |
| Confirmation: BEAM `combined-v2+w5` | behind Garry's go | 45 |
| Confirmation: the comparator's BEAM regeneration | behind Garry's go | 105 |
| Confirmation: joint re-judges (BEAM $89 with the W5 lane, LoCoMo10 $12, LongMemEval-S $6) | behind Garry's go | 107 |
| **Subtotal** | | **628** |
| Reserve | | 22 |
| W3 `combined-v2+gate` replay, only if A15 shows a would-skip rate of at least 25% | contingent | 35 |

The contingent W3 replay exceeds the reserve by $13. If A15 calls for it, it needs either a trim recorded here or Garry's decision on the cap before it runs. Confirmation stays behind Garry's explicit go.

## W5 pin, key and receipt check (October 11, 2026)

**Pin.** W5 dev tuning runs at gbrain `fe9e0397b7e523b8db3b83e1202fb297337e71b3`, the head of #6445's branch. Its parent is the previous dev pin `8d4f6ab6e`, so the pin is that tree plus W5 and nothing else. Every W5 tuning cell runs with `GBRAIN_SHA` set to this SHA, and the pin does not change mid-run.

**Key.** `search.page_rank_budget_ratio`, registered in `KNOWN_CONFIG_KEYS` and read by `src/core/search/page-rank-cut.ts`. It is off when unset, empty, zero, negative, non-numeric or not finite (`Infinity` included); the specs write `0` for off.

**Where it applies.** Only page-unit calls that carry a caller `token_budget`: `query`, `search` and recall's hybrid page arm. Chunk-unit calls and calls without a caller budget never engage it. When on, ranking cuts its hits to `min(mode search.tokenBudget, max(1, floor(ratio × caller budget)))`, using the caller budget after any remote clamp. Under `tokenmax` with `search.tokenBudget` `10000000`, the ratio sets the cut.

**What it reports.** `page_rank_cut {ratio, caller_budget, mode_cut, applied_cut, candidates, kept}`, in `_meta` on `query` and `search`, and top level on `recall`. It is absent when the key is off.

**Tests at the pin.** A local smoke run against the pin, through the wave-2 provider with `token_budget` 1,500, reported `{ratio 0.5, caller_budget 1500, mode_cut 10000000, applied_cut 750}` with the ratio at `0.5`, and no `page_rank_cut` with it at `0`. The provider suites (`test_gbrain_facts`, `test_page_rank_cut`, `test_mpw2_dev_specs`) pass against the pin. GitHub Test run 38189090777 was dispatched by hand, because #6445 conflicts with master while it is held as the pin. Its shard 4 fails one gbrain test: `test/config-search-registry.test.ts`, "every registered search.* key has a reader", which expects the new key in that test's own list of directly read keys. It reproduces locally. The missing entry is in the test, not the code path, so the measurement is unaffected. The fix is a one-line test change on #6445, and it does not move the W5 tuning pin.

**Receipt check.** On every query-path row, the provider checks the reported cut against the arm's spec before keeping the row:

- with the ratio off, a reported `page_rank_cut` fails the row;
- with it on, `ratio` must equal the spec's ratio, `caller_budget` must equal the spec's `token_budget`, and `applied_cut` must equal `min(search.tokenBudget, floor(ratio × token_budget))`; a missing or different cut fails the row.

The checked object is kept in each row's metadata as `page_rank_cut`. The one-call recall path records the object but does not check it, and no W5 tuning arm uses that path.

**Specs.** Six arms in `eval/harness-provider/cells/mpw2/w5/` (`lme-b`, `lme-d`, `lme-w5-0.40`, `lme-w5-0.50`, `lme-w5-0.75`, `lme-w5-1.00`), with `order.json` putting `b` first to build the store. The stage cap is $18, `b`'s cell cap is $12 and the other cells' caps are $2 each. All six are `filler-removed` at `token_budget` 8,100 and set every key in the re-scope knob table, including `search.tokenBudget` and `search.page_rank_budget_ratio`. `mpw2-iso-specs.py` generates them, and `tests/test_mpw2_dev_specs.py` checks each arm's mode and ratio. The dev specs are regenerated with both new keys, with the ratio `0` (off), and with `search.tokenBudget` `4000` on `raw` and `10000000` elsewhere.

## W5 dev tuning result: ratio 0.40 is picked (October 12, 2026)

**The preregistered ratio rule picks `w5-0.40`.** All four W5 ratios pass the rule's three conditions. `w5-0.40` has the most multi-session questions correct, 16 of 22 against `b`'s 11, and scores 90 against `b`'s 82. The result is exploratory, LongMemEval-S dev only, on one store at `fe9e0397b`. The rule is applied with the full six-arm set, as preregistered.

The scores come from the joint blinded re-judge of the six arms. Intervals are paired bootstrap 95% intervals over questions, 9,999 draws, seed `20261010`.

| Arm | Score | vs `b` | vs `d` | Multi-session (22) | Temporal reasoning (27) | Pages kept by the W5 cut per question |
|---|---:|---|---|---:|---:|---:|
| `b` tokenmax, W5 off | 82 | — | −9 (−17 to −2) | 11 | 22 | — |
| `d` conservative, W5 off | 91 | +9 (+2 to +17) | — | 19 | 22 | — |
| `w5-0.40`, cut 3,240 | 90 | +8 (+2 to +14) | −1 (−7 to +5) | 16 | 24 | 5.9 |
| `w5-0.50`, cut 4,050 | 88 | +6 (+1 to +12) | −3 (−9 to +3) | 15 | 22 | 7.2 |
| `w5-0.75`, cut 6,075 | 88 | +6 (+2 to +11) | −3 (−10 to +3) | 14 | 23 | 10.3 |
| `w5-1.00`, cut 8,100 | 88 | +6 (+2 to +11) | −3 (−9 to +3) | 14 | 23 | 13.5 |

**Rule check, question counts against `b`.**

| Arm | Overall ≥ `b` | Multi-session vs `b` (needs +2) | Other types vs `b` (each needs ≥ −1) | Passes |
|---|---|---:|---|---|
| `w5-0.40` | yes, 90 | +5 | temporal reasoning +2, single-session user +1, all others 0 | yes |
| `w5-0.50` | yes, 88 | +4 | single-session preference +1, single-session user +1, all others 0 | yes |
| `w5-0.75` | yes, 88 | +3 | temporal reasoning +1, single-session preference +1, single-session user +1, all others 0 | yes |
| `w5-1.00` | yes, 88 | +3 | temporal reasoning +1, single-session preference +1, single-session user +1, all others 0 | yes |

Condition 2, "within 1 question of `b`", is read as a floor: no other type loses more than one question. No arm loses a question in any type. A two-sided reading would exclude `w5-0.40`, which gains two temporal-reasoning questions, and would pick `w5-0.50` instead. The floor reading is applied because the condition guards against regressions. `analysis.json` records both readings for each arm.

- **The cut closes most of the mode gap.** `w5-0.40` recovers 89% of `d − b` (8 of 9 points) and sits 1 point below `d`, with an interval that includes zero. The other ratios recover 67%.
- **Multi-session rises as the cut tightens.** 14, 14, 15 and 16 of 22 from ratio 1.00 down to 0.40, against `b`'s 11 and `d`'s 19. `d` still leads on multi-session by 3. That matches the two-way finding that the reranker's choice of surviving pages costs some multi-session questions under `tokenmax`.
- **Abstentions fall.** `b` abstains on 19 questions. The W5 arms abstain on 11 to 14, and `d` on 10.
- **The receipt check holds on every row.** All 100 rows of each W5 arm report `applied_cut` 3,240, 4,050, 6,075 and 8,100 respectively. The ratio-off arms report no cut. Every cell passes all four gates, with no answer or retrieval failures.

**Stage cap raise.** Arm `w5-1.00` was refused before it spent anything, because its $2.00 run budget exceeded the $1.80 left under the $18.00 stage cap. With Garry's approval, the stage cap was raised to $19.50, inside the re-scope's roughly $20 W5 tuning line. The reason is recorded in the stage ledger's cap change.

**Spend.**

| Item | Spend |
|---|---:|
| Store and arm `b` | $10.92 |
| Arms `d`, `w5-0.40`, `w5-0.50`, `w5-0.75`, `w5-1.00` | $6.66 |
| Joint re-judge (cap $2.50) | $1.53 |
| **Total** | **$19.10** |

Wave-2 spend to date is $75.12.

**Next.** `combined-v2+w5` uses `search.page_rank_budget_ratio` `0.40` in the dev checks and the W5 BEAM gate. Dev at the new pin is released under the re-scope amendment. Confirmation stays behind Garry's go.

Receipts are under `2026-10-10-memory-proof-wave-2/w5/`, with the re-judge in `w5/rejudge/`. Ledgers are mirrored to the integrator's primary machine with matching SHA-256: `w5.sqlite` `362e22ff…`, `w5-rejudge.sqlite` `39f7e345…`. A compressed copy of the store, `gbrain-longmemeval-s-165df707838f` (sha256 `0a136a61…`), is kept beside them, so the dev group can reuse it. The VM is destroyed and recorded.
