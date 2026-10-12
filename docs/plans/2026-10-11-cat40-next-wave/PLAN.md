# Cat 40 next wave: stale-value answers, the H4 gap, the v1 headline, and withdrawn facts

Status: draft for autoplan review, 2026-10-11. Owner: GBRA-39. Merge queue: GBRA-40. Garry asked for a plan covering three items: (1) gbrain's two weak spots from the Cat 40 Hard confirmation, (2) the rerun recommendations in gbrain-evals #110, and (3) whether `remember` should restore a withdrawn fact.

## ELI10

When gbrain loses to plain files, it is almost always for one reason. It finds the customer's original contract, but the later amendment that changed the number never reaches the model, so the model confidently answers with the old number. Plain files lose less this way because grep shows every line that mentions the term. The fix is to make gbrain point at the record that currently governs: list a customer's signed contracts and amendments with their effective dates on the customer's card, return the sentence that sets the value when a long document matches, and label drafts and call summaries as not binding. Separately, one old headline claim was measured with gbrain's reranker silently off and needs to be retired or remeasured. And a fact you told gbrain to forget should stay forgotten unless you deliberately restore it.

## What happened

The Cat 40 Hard confirmation (gbrain-evals #93 RESULTS.md) put gbrain ahead of plain files by +7.7 points on a fresh world (M) and +13.0 on a sealed world (S), pooled over Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol. The release shipped as gbrain v0.60.174.0. The report names two weak spots:

- **More wrong answers.** gbrain answered wrong more often than fs: 22 vs 14 cells on M, 16 vs 2 on S.
- **H4 trails.** On M's H4 family (current contract terms) gbrain scored 47 vs fs 56 of 60.

## Root cause (free analysis, `RCA.md` and `rca_next.py` beside this plan)

Inputs: world M (300 cells per arm) and the development world (150 per arm). No S cells or transcripts were opened. `rca_next.py` prints every number below.

- **One mechanism behind both.** Among gbrain's 22 wrong-value cells on M, all are class (a): the account's own superseded or older value. `search` was the first tool result carrying the wrong value in 16 of 22, and in 20 of 22 that result named the stale source document. The governing document appeared anywhere in the cell in only 12 of 22. Entity confusion and invented values are 0 on both worlds.
- **H4.** fs won 11 H4 cells and gbrain won 2. Of the 13 failed items in those cells, the deciding document was never returned in 7, and in 5 it was returned only as a chunk without the deciding sentence (2 uncertain because transcripts clip at 40,000 characters). In 1 it was shown and still answered stale. 0 hit the turn cap. The gap concentrates in long executed documents ("amended + long": gbrain 16/21, fs 20/21; "later effective wins + long": 11/15 vs 14/15).
- **`get_page` works but isn't used.** All 52 `get_page` calls on long H4 documents returned the deciding sentence. In none of the 13 failed items did the model open the deciding document. gbrain stops early: median 19 tool calls and 8 turns on these tasks against fs's 28 and 10.
- **The account views don't point at the governing record.** A median H4 account has 29 documents. `context_pack` listed about 4 of them and included the deciding document in 8 of 88 results. `entity` lists none.
- **Lower-authority sources.** 3 gbrain wrong items (all H4) came from an unsigned draft or a call-summary email, via `context_pack` and `get_backlinks`. 1 came from an agent note via `search`.
- **Not the cause.** The turn cap. Only 4 of gbrain's 32 wrong cells were submitted at turns 14–16, and gbrain's median wrong submit is turn 8 (fs 12). Turn-cap losses are gbrain's largest failure bucket (32 cells), but fs fails 31 of the same cells.
- **Dev world.** The mechanism holds: class (a) is 6 of 8 gbrain wrong items, `search` carries the stale value first in 5 of 6, and the card gap is the same. The H4 deficit does not reproduce (27 vs 27) because dev draws fewer long amended items (15 vs 36). So the mechanism is systematic, and the size of the H4 gap depends on the world's long-document mix.
- **Ceiling.** Fixing class (a) plus the lower-authority sources has a ceiling of +6.0 pooled points on M counting only cells fs got right (+7.3 counting all), and +2.7 on dev (+4.0). On H4 alone, flipping the 11 fs-won cells would move gbrain from 47 to 58. These are ceilings, not promises.

## Goal and kill criterion

- **Goal.** Lower gbrain's wrong-answer rate below fs's on a fresh world, and close the H4 gap, without losing the confirmed lead.
- **Primary endpoint (preregistered before confirmation).** Pooled gbrain − fs on a new fresh main seed and a new sealed seed (S is spent; SEALED.md says so), same three models, same rule as #93's PREREG: both Δ ≥ 0 to keep the claim, "ahead" only when the lower bound is above 0.
- **Secondary endpoints that decide whether this wave shipped its goal.** The wrong-answer count, gbrain vs fs, per world, and H4 gbrain − fs per world.
- **Kill criterion for the wave.** If the confirmation shows the wrong-answer count is not lower than v0.60.174.0's on the same worlds, measured by a same-window baseline arm, the wave's changes are reverted or kept only where they are neutral. The headline claim from #93 is not re-litigated by this wave unless Δ falls below 0, in which case the existing publish-and-stop rule applies.

## Implementation plan

### Part 1: point the agent at the governing record (gbrain product changes, one batched PR)

All changes are general to any brain with dated documents that supersede each other. No task-, family- or fixture-specific code. They rely on gbrain-owned fields (`effective_date`, `effective_date_source`, page type, existing timeline and fact supersession) and on conventions documented in gbrain before the benchmark uses them.

**F1. Governing records on the entity card and in `context_pack`.** For an entity, add a `records` section listing the documents that state terms for it (pages of a contract-like type, and amendments, per the brain's schema pack types), newest effective first, each with page type, signed date, effective date and its source (`effective_date_source`), plus which earlier record it amends when the page says so. Cap the list (default 8) with a total and a `next` cursor, the same paging words `get_backlinks` uses. Emails and notes stay in `referenced_by`. Expected effect: closes the card gap, where the deciding document was absent from every `entity`/`context_pack` result in the 11 lost H4 cells.

**F2. Return the deciding passage of long documents.** When a search hit is a long page (above a configurable size) and the hit chunk doesn't contain the query's term tokens, also return the best-matching passage from that page (the sentence or short span with the highest term overlap, e.g. lines stating "effective … change to …" when the query names a term), and mark the row `long_page: true, open_with: get_page`. This is a retrieval-side change. It doesn't depend on the model choosing to open the page, which it didn't do in any of the 13 failed items. Expected effect: the 5 "returned without the deciding sentence" items and part of the 7 misses.

**F3. Authority labels in results.** Rows from pages marked as not binding carry `authority: draft` or `authority: secondhand`. That covers pages whose frontmatter or title marks them draft or unsigned, and email pages whose subject or first line identifies them as a summary of a call. This uses only markers gbrain documents first in its frontmatter conventions. If the benchmark's draft and summary markers aren't covered by a convention gbrain would honor on a real brain, F3's expected points on the benchmark are 0, and it ships only if it is right for real brains. Applies to `search`, `context_pack` and `get_backlinks`. Expected effect: the 3 (g) items.

**F4. Search guidance (description text only).** One sentence in the `search` and `entity` descriptions: when a value can be amended, check the entity's `records` for the latest effective record before answering. Measured on dev like the round-4 guidance A/B, with the same rule: kept only if it doesn't cost points, and reported separately.

**Not in this wave.** Turn-cap changes (no gap against fs), model-specific prompting, and owner-phrase resolution (deferred from the last wave).

### Part 2: the v1 frontier headline (gbrain-evals #110's recommendations)

#110 found that the Cat 40 v1 frontier headline (gbrain `51f865d78` 95.6% vs fs 95.6%) ran with gbrain's reranker off in all 500 cells. Its three recommendations are:
1. Rerun the frontier headline with reranking on today's models.
2. Retire the six-model mid-tier claim (old models), letting recommendation 1 replace it.
3. Rerun Hard's held-out gbrain arm with reranking before treating −11.3 as the shipped gap.

Status: recommendation 3 is superseded. The Cat 40 Hard confirmation ran with reranking verified in every gbrain slot (168/168 and 167/167 hybrid-search cells reranked) and replaces −11.3. Recommendation 2 needs no spend.

**Default.** Retire the v1 frontier row and the mid-tier claim in the README. Replace them with the Hard confirmation result, and keep the old rows in history with their correction notes.

**Alternative (Garry decides).** Also rerun v1 gbrain and fs in one window on Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol: 50 tasks × 2 repeats × 2 arms = 600 cells, about $150–200 including the judge (the v1 gbrain arm cost $119 for 500 cells). Caveat: the v1 world is at its third use and near ceiling (oracle 97.6%, fs 95.6%), so a rerun can at best confirm parity there; it can't show a lead.

### Part 3: withdrawn facts (`remember` after `forget`)

**Today (traced on master and tested on both engines).** `remember` refuses a claim that is withdrawn for the subject it names, before anything is written, with `invalid_params` / `fact_withdrawn`. That holds for every caller, including the owner. No withdrawn row is reactivated, and dedup never matches a withdrawn row. Supersession and TTL expiry write no withdrawal, so re-saving those creates a new fact.

**Options considered.**
- (i) Always restore.
- (ii) Restore when the new call is more specific.
- (iii) Never restore implicitly.

(i) and (ii) reverse documented MEMORY_VERBS v1 semantics ("does not restore"), need a v2 document, and let any writer undo the owner's forget, because the withdrawal ledger records no principal.

**Recommendation: (iii), in two steps.**
1. **This wave.** The refusal gains optional detail: `withdrawn_at` and `withdrawn_scope`, omitted when the caller can't see the rows that back the withdrawal. No semantics change.
2. **Later, only if the owner wants un-forget.** A `restore: true` parameter, trusted local callers first, kept off the starter tool list. It needs principal columns on the withdrawal ledger and a test that a restored fact survives the next sync.

Two visibility bugs in the withdrawal and card paths, found during this research, are being fixed separately as a security PR ahead of this wave. They aren't described here until that PR merges.

### Development and confirmation (no tuning on held-out data)

- **Development.** Use the calibration world (seed 20261005) plus world M as development worlds. M is now spent as a confirmation world, so it can serve as a development world: its H4 has the long-document mix that dev lacks. Use the same three models, gbrain arm only, against recorded fs cells, with repeated rounds as in the last wave. Report each F-item's effect with build-vs-build pairs on the same window.
- **Confirmation.** A new fresh main seed, plus a new sealed seed generated on Garry's Mac (custody as before). Arms: gbrain v0.60.174.0 (baseline), gbrain wave build, fs, and oracle as a check. The baseline arm makes the wrong-answer endpoint a same-window comparison. Preregistered before any confirmation cell runs.

### Shipping

One gbrain PR for Part 1 and Part 3 step 1. One gbrain-evals PR for the plan, development record, preregistration, results and README changes. GBRA-40 merges. Stamps and migration numbers are taken at the slot.

### Cost (estimates; actual spend is ledgered)

- **Development:** about $600–900 (the last wave's rounds cost about $1,700 over 5 rounds; this wave has fewer, more targeted items).
- **Confirmation:** about $1,600–1,900 for two worlds with a baseline arm added. Last wave's two worlds cost about $1,100 real; the ledger showed $1,348 including an overcharge since fixed. The added baseline arm adds about 50%.
- **Part 2 rerun, if chosen:** about $150–200.
- **Part 3:** no eval spend.

### Pending Garry (defaults apply until decided)

| Item | Default | Alternative |
|---|---|---|
| Part 2 | retire the v1 headline, no rerun | also rerun v1 (~$150–200, parity at best) |
| Part 3 | (iii): refusal detail now, restore later only on request | (ii) restore when more specific, needs MEMORY_VERBS v2 |
| Dev budget | ~$900 | other |
| Confirmation budget | ~$1,900 with a baseline arm | without a baseline arm (~$1,300), wrong-answer endpoint compared across windows |
| F3 authority labels | ship only if a real-brain convention covers them | skip F3 |

## Review record
