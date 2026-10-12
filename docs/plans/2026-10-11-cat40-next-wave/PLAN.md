# Cat 40 next wave: stale-value answers, the H4 gap, the v1 headline, and withdrawn facts

Status: reviewed by /autoplan 2026-10-12 (CEO, DX, Eng; gate pending Garry, see the Review record). Drafted 2026-10-11. Owner: GBRA-39. Merge queue: GBRA-40. Garry asked for a plan covering three items: (1) gbrain's two weak spots from the Cat 40 Hard confirmation, (2) the rerun recommendations in gbrain-evals #110, and (3) whether `remember` should restore a withdrawn fact.

## ELI10

When gbrain loses to plain files, it is almost always for one reason. It finds the customer's original contract, but the later amendment that changed the number never reaches the model, so the model confidently answers with the old number. Plain files lose less this way because grep shows every line that mentions the term. The fix is to make gbrain point at the record that currently governs: list a customer's signed contracts and amendments with their effective dates on the customer's card, return the sentence that sets the value when a long document matches, and label drafts and call summaries as not binding. Separately, one old headline claim was measured with gbrain's reranker silently off and needs to be retired or remeasured. And a fact you told gbrain to forget should stay forgotten unless you deliberately restore it.

## What happened

The Cat 40 Hard confirmation (gbrain-evals #93 RESULTS.md) put gbrain ahead of plain files by +7.7 points on a fresh world (M) and +13.0 on a sealed world (S), pooled over Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol. The release shipped as gbrain v0.60.174.0. The report names two weak spots:

- **More wrong answers.** gbrain answered wrong more often than fs: 22 vs 14 cells on M, 16 vs 2 on S.
- **H4 trails.** On M's H4 family (current contract terms) gbrain scored 47 vs fs 56 of 60.

## Root cause (free analysis, `RCA.md` and `rca_next.py` beside this plan)

Inputs: world M (300 cells per arm) and the development world (150 per arm). No S cells or transcripts were opened. `rca_next.py` prints every number below.

- **One mechanism behind both.** gbrain's 22 wrong-value cells on M hold 22 class (a) items (the account's own superseded or older value): 18 cells are class (a) only, 2 mix (a) with a lower-authority source (g), 1 is (e) and 1 is (g). `search` was the first tool result carrying the wrong value in 16 of 22, and in 20 of 22 that result named the stale source document. The governing document appeared anywhere in the cell in only 12 of 22. Entity confusion and invented values are 0 on both worlds.
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

- Review (CEO, both voices, verified on master): gbrain's `effective_date` is the page's own date (`event_date` > `date` > `published` > filename > created), which for an amendment is the day it was signed (`src/core/effective-date.ts`; `src/core/search/date-labels.ts` already says "never a contract's effective or validity date"). In "later effective wins" the governing amendment is signed earlier, so "newest effective first" would put the non-governing record on top. Gate d2 decides whether F1 keeps this ordering; draft direction stands until the owner decides (d2).
- Review (CEO, both voices): the full single-name `entity` card already lists referring pages grouped by type with `date`, `date_source`, totals and a `get_backlinks` continuation (`referenced_by`, `src/core/verbs/entity-card.ts`, `src/core/mentions/referrers.ts`). All 47 `entity` calls in M's gbrain H4 cells used the compact `names` mode, which carries no references. Both voices recommend moving F1 to the compact rows and `context_pack`, derived from the existing referrer path. Gate uc1; draft direction stands until the owner decides (uc1).
- Accepted (CEO): whatever F1's placement, record rows show the page date labeled as a page date (`date`, `date_source`) and list order is never presented as "this record governs"; a page with draft status is never listed without its status.
- Review (DX, native voice, new evidence for the F1 placement question): gbrain's own served instruction 7 (`src/mcp/instructions.ts:74-76`) tells agents to batch names with `entity` `names` and, in the same sentence, to walk `referenced_by`, which `names` rows do not carry. That is why 47 of 47 H4 entity calls missed the full card. The native voice recommends that, wherever F1 lands, each compact row carries a lean record list or at least `referenced_by_count` plus an executable `next` to the full card, and that instruction 7 stops recommending a walk the recommended mode cannot do. Gate d5; draft direction stands until the owner decides (d5).
- Accepted (DX, both voices): F1 reads an explicit, documented enrollment. A pack-level record-type declaration (empty by default, so F1 is off on brains that do not opt in) names which canonical page types are records; "amends" is the existing `supersedes` link through a frontmatter mapping rule, never a body parser. Ship a copy-paste pack example, a generic Markdown example with its expected tool result, and a read-only check that lists which pages count as records. Unrecognized types stay discoverable in ordinary references. The benchmark world opts in through the same documented declaration before any dev cell runs, and the plan states that F1's benchmark points come from that opt-in.
- Accepted (DX): records are an additional view; `referenced_by` membership and its `get_backlinks` parity are unchanged, and record rows reuse the `referenced_by` row shape without previews or per-row constant fields (`status` only where set, `supersedes` only where linked).
- Accepted (DX, both voices): one continuation shape. F1 uses the entity card's executable `next: {tool, arguments, requires_surface?}`; its continuation returns exactly the remaining records (either `types[]` on `get_backlinks` or one `next` per type); a capped or withheld list keeps its `total` and `next` with a reason; an undeclared type says so instead of returning an empty list; mention-coverage and degraded notices propagate wherever records appear.
- Accepted (DX): in `context_pack`, F1 carries `referenced_by_count` (the existing name) or no count, and the field description says what `backlink_count` excludes.
- Accepted (Eng, both voices; replaces the DX clause "\"amends\" is the existing `supersedes` link"): `supersedes` is a ranking input, not metadata. Hybrid search multiplies a superseded page's score by 0.5 and exact lookup will not promote it (`src/core/search/hybrid.ts:669-797`), so mapping amendments to it would down-rank the contract that still governs unchanged terms and future-effective items. "Amends" is a separate, non-ranking link type declared in the pack and fed by a frontmatter mapping rule; `supersedes` stays for whole-record replacement. Tests cover unchanged terms, future-effective amendments and genuine replacement through final search scores and labels. Gate d8 asks the same question.
- Accepted (Eng, both voices): the schema-pack manifest is strict (`src/core/schema-pack/manifest-v1.ts`), so a new pack-level key would not load on the baseline arm or any older gbrain. Record-type enrollment is a config key the harness applies per arm (older builds ignore it); the pack carries only the link mapping. Baseline-compatible and wave-compatible pack variants are frozen, shown to resolve identically apart from the declaration, and both hashes are recorded before paid cells. Enrollment and relationship-rule lookup agree on canonical aliases.
- Accepted (Eng, both voices): records are filtered by enrolled type inside the shared referrer membership query, before ordering, LIMIT and hydration, with record-only totals and keysets, so the existing all-type caps cannot starve them. `names` rows use one batched multi-target query (no per-name N+1), the per-call cap is enforced before hydration and stated as a number (starting point: 3 per name, 24 per call), and a names-mode perf test joins the existing card p99 test. Records get an explicit ORDER BY and cursor whatever d2 decides, and their continuation is one executable `next` per record type (no new `types[]` parameter on `get_backlinks`, whose description has 4 characters of budget left).
- Accepted (Eng, native voice): records are computed only in the `context_pack` pull verb, never in the shared assembler that also feeds the ambient push path (`src/mcp/context-pack-handler.ts:186`, 600 ms deadline); a test pins the push output unchanged.
- Accepted (Eng, native voice): before compact rows carry records, the security follow-up owner confirms `names` rows apply the same read options as the single-card path (flagged urgent outside this plan; details stay with that owner); F1's names-mode tests include such an entity.

**F2. Return the deciding passage of long documents.** When a search hit is a long page (above a configurable size) and the hit chunk doesn't contain the query's term tokens, also return the best-matching passage from that page (the sentence or short span with the highest term overlap, e.g. lines stating "effective … change to …" when the query names a term), and mark the row `long_page: true, open_with: get_page`. This is a retrieval-side change. It doesn't depend on the model choosing to open the page, which it didn't do in any of the 13 failed items. Expected effect: the 5 "returned without the deciding sentence" items and part of the 7 misses.

- Review (CEO, both voices): gbrain already has evidence delivery (`return_unit` chunk | window | section | page | auto, `src/core/search/evidence-delivery.ts`); F2 belongs in that seam, not in a parallel picker. On M's lost cells a max-term-overlap sentence ranked the deciding sentence below another sentence in 9 of 12 parsed long-page hits (outside voice's probe), and F2 cannot reach the 4 short-document misses, so it reaches at most 3 of the 7 misses. The outside voice recommends replacing the lexical selector with a fixed-hit, fixed-budget comparison of existing delivery units first. Gate d3; draft direction stands until the owner decides (d3).
- Accepted (CEO): any new F2 field is added to the lean-row allowlist (`src/core/search/lean-rows.ts`) or remote agents never see it; F2 is tested on a fixture where the term words recur in non-deciding clauses (the benchmark's boilerplate contains none of them, so benchmark gain overstates real-brain gain); a Sonnet harm check is preregistered for dev, because the 2026-10-08 evidence-brief variant measured −3.0 points on Sonnet.
- Accepted (DX, both voices): F2's activation is reachable on an ordinary remote search over non-conversation pages (today `auto` exits early when no conversation signal is present, `src/core/search/evidence-delivery.ts:305-315`; 573 of 658 M H4 searches omitted both `return_unit` and `token_budget`), without widening unrelated pages. Explicit `snippet_chars` and `token_budget` precedence is specified; any passage is counted in the existing delivery budget; the row reports firing through the existing `delivered` object and snippet marker instead of new `long_page`/`open_with` keys. A named `search.*` config key and default size are documented in `docs/evidence-delivery.md`, and `return_unit: "chunk"` stays the byte-identical off path. Tests assert on the final serialized lean MCP output.
- Accepted (Eng, both voices; refines the DX activation clause): F2 sits behind its own `search.*` config key, default off until confirmation passes. `test/evidence-delivery-golden.test.ts:78` (implied auto is byte-identical to chunk) stays as the off-path contract and a second frozen golden pins the on path; flipping the default later is its own behavior-change decision. Activation is resolved at the `search`/`query` caller and passed into the assembler as an explicit policy, so recall, think and queryless `assemble_evidence` stay byte-identical.
- Accepted (Eng, both voices): the passage leads the delivered text (or replaces the window anchor) so `snippet_chars`, which cuts from the front and was set on 283 of 658 M H4 searches, cannot drop it; lean rows carry a compact `delivered {unit, reason}` when F2 fired (today they keep only `{truncated: true}`); F2 has candidate-page and total-input-byte limits and a cooperative deadline, using a size preflight and a bounded batched fetch without slicing raw protected bodies; F2 adds no text when the query names no term (421 of 658 M H4 searches used `match: "keyword"` and 352 named no term word), and dev results are stratified by match mode and term presence.

**F3. Authority labels in results.** Rows from pages marked as not binding carry `authority: draft` or `authority: secondhand`. That covers pages whose frontmatter or title marks them draft or unsigned, and email pages whose subject or first line identifies them as a summary of a call. This uses only markers gbrain documents first in its frontmatter conventions. If the benchmark's draft and summary markers aren't covered by a convention gbrain would honor on a real brain, F3's expected points on the benchmark are 0, and it ships only if it is right for real brains. Applies to `search`, `context_pack` and `get_backlinks`. Expected effect: the 3 (g) items.

- Review (CEO, both voices): search rows already pass raw `frontmatter.status` and every row carries `trust_tier`/`origin`; F3 would mint a third vocabulary, and "draft", "summary" and "not binding" are not interchangeable on real brains (a call summary can be the only record; a draft can be the thing asked about). Both voices recommend removing the automatic not-binding inference and the subject/first-line heuristics, and limiting F3 to propagating the existing `status` and trust fields to `context_pack` and `get_backlinks` plus a documented `status: draft|unsigned` convention, with expected benchmark points 0. Gate uc2; draft direction stands until the owner decides (uc2).

**F4. Search guidance (description text only).** One sentence in the `search` and `entity` descriptions: when a value can be amended, check the entity's `records` for the latest effective record before answering. Measured on dev like the round-4 guidance A/B, with the same rule: kept only if it doesn't cost points, and reported separately.

- Accepted (CEO): F4's sentence is written after F1's placement is settled and names only fields the model actually receives in the mode it calls.
- Review (DX, native voice): served instruction 7 already carries F4's guidance ("for what is true now, prefer the newest governing source…"), and the M runs served it. "Newest" is the wrong rule in "later effective wins" and "future effective". The native voice recommends replacing F4's two new description sentences with one general edit to instruction 7 (the record whose terms are in effect on the date asked about; a page's date is when it was written; a not-yet-effective change does not apply yet), keeping the A/B rule. Gate d6; draft direction stands until the owner decides (d6).
- Accepted (CEO): every new stage reports whether it fired (records listed, hints stamped, passage returned vs fallback) through explain contributions or debug counters, and the dev record reports firing rates, so a null result can be read.
- Accepted (CEO): payload guard. Records are capped per call (not just per name; `names` takes up to 50), $/task and tool-result tokens are guard metrics in dev, and a deterministic test shows `newer_mentions` still packs under the default `context_pack` budget with records present.
- Accepted (DX): the payload guard is measured on the serialized tool result the agent receives (`context_pack` returns `cards[]` plus `text`; `budget_tokens: 1500` returned about 12,000 characters on M), from the attempts `chars` field, not the transcript (capped at 40,000 characters per result). Notice characters are reported on their own line and notice state is identical across baseline and wave arms. The per-call record cap is a stated number.
- Accepted (Eng, native voice): instruction and tool-description budgets have no headroom (instructions 4,975 of 4,975, search 1,788 of 1,800, entity 546 of 550, get_backlinks 766 of 770 characters in `test/mcp-schema-budget.test.ts`); every text change, F4 and d5/d6 included, names the cut that pays for it or records a budget raise per that test's convention.
- Accepted (Eng, native voice): each F-item ships behind its own config key with a documented default, and dev arms are measured on one build through the harness's per-arm `--gbrain-config` and description overrides, so per-item retention needs no build-vs-build multiplication.
- Considered (CEO, native voice): an entity-scoped exact-term lane (search scoped to an entity's referrers with a sentence-level return unit, the closest analogue of fs's grep). Not added as a planned arm; it is the fallback dev arm if F1 and F2 do not fire or do not move H4.

**Not in this wave.** Turn-cap changes (no gap against fs), model-specific prompting, and owner-phrase resolution (deferred from the last wave).

**Revised expected effect (autoplan review).** The ceilings are unchanged and re-derived: fixing class (a) plus the lower-authority sources is worth at most +6.0 pooled points on M counting only cells fs got right (+7.3 counting all); H4 at most 47 → 58. Per-item expectations are narrower than drafted. F1 reaches the observed workload only on the compact `names` rows or `context_pack` (uc1, d5), and on the benchmark only through the documented opt-in. F2 can reach at most the 5 returned-without-the-sentence items (2 of them uncertain) and 3 of the 7 misses, and adds nothing on keyword queries that name no term. F3's benchmark points are 0 if uc2 is accepted. F4's effect is measured separately under the round-4 rule. No point estimate is made until the zero-provider gate (if d4 is accepted) and the first dev round report firing rates.

### Part 2: the v1 frontier headline (gbrain-evals #110's recommendations)

#110 found that the Cat 40 v1 frontier headline (gbrain `51f865d78` 95.6% vs fs 95.6%) ran with gbrain's reranker off in all 500 cells. Its three recommendations are:
1. Rerun the frontier headline with reranking on today's models.
2. Retire the six-model mid-tier claim (old models), letting recommendation 1 replace it.
3. Rerun Hard's held-out gbrain arm with reranking before treating −11.3 as the shipped gap.

Status: recommendation 3 is superseded. The Cat 40 Hard confirmation ran with reranking verified in every gbrain slot (168/168 and 167/167 hybrid-search cells reranked) and replaces −11.3. Recommendation 2 needs no spend.

**Default.** Retire the v1 frontier row and the mid-tier claim in the README. Replace them with the Hard confirmation result, and keep the old rows in history with their correction notes.

- Accepted (CEO): the README states that the Hard confirmation measures a different workload; it never implies the v1 comparison was remeasured.
- Accepted (DX): every sentence of README.md:141-148 and row 72 gets a disposition (retire, keep with scope, replace), including "gbrain costs about twice as much per task as files", which Hard M contradicts per model (Sonnet $0.59 vs $1.03, Opus $0.86 vs $1.75, Sol $0.28 vs $0.19 per task); the new Hard row states workload, models, reranker state and per-model cost.
- Review (CEO, native voice): README.md:72's v1 row also carries the "0 of 100 finance-only leaks" permission result; the native voice recommends retiring the parity and mid-tier claims but keeping the permission result after a static check that visibility filtering does not depend on reranking. Gate d1; draft direction stands until the owner decides (d1).

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

Two visibility bugs in the withdrawal and card paths, found during this research, were fixed separately in a security PR, which merged as gbrain #6509 (v0.60.176.0, master `2895edb3`) during this review. Details stay in that PR.

- Accepted (CEO): Part 3 step 1 branches after the security PR merges and reuses its visibility predicate; both engines are tested so a caller without visibility gets the plain refusal; the change is listed under behavior changes with its consumer named. The refusal detail is documented as covering the exact normalized claim only: it is not a guarantee about paraphrases, which the existing suggestion already permits.
- Accepted (DX, both voices): the refusal detail is one additive typed object (for example `withdrawn: {at, subject_or_all_entities, visibility}`; not named "scope", which already means OAuth/read scope) carried identically on the immediate refusal, the batch item error and the failed write receipt, through `OperationError`, the agent envelope and batch projections; the legacy message prefix is unchanged; MEMORY_VERBS v1 documents that absence carries no meaning; stdio, HTTP and CLI JSON outputs are tested.
- Accepted (Eng, native voice): the detail comes only from `fact_withdrawals` (never from purge records), with a deterministic rule for which ledger row supplies `at` and the subject when several match; the object persists in the write receipt's outcome so later receipt reads carry it; the second refusal site at commit time (`src/core/facts/write-single.ts:137-140`) applies the same visibility predicate. Part 3 step 1 can start now that #6509 has merged. Whether it ships in the eval-gated Part 1 PR or the next batched gbrain wave PR is gate d7.

### Development and confirmation (no tuning on held-out data)

- **Development.** Use the calibration world (seed 20261005) plus world M as development worlds. M is now spent as a confirmation world, so it can serve as a development world: its H4 has the long-document mix that dev lacks. Use the same three models, gbrain arm only, against recorded fs cells, with repeated rounds as in the last wave. Report each F-item's effect with build-vs-build pairs on the same window.
- **Confirmation.** A new fresh main seed, plus a new sealed seed generated on Garry's Mac (custody as before). Arms: gbrain v0.60.174.0 (baseline), gbrain wave build, fs, and oracle as a check. The baseline arm makes the wrong-answer endpoint a same-window comparison. Preregistered before any confirmation cell runs.
- Accepted (CEO): M results are labeled in-sample and diagnostic, because the F-items were designed from M's failures.
- Review (CEO, outside voice): add a zero-provider transfer and negative-control gate before paid development: independently authored pages (partial overrides, future validity, a decisive paragraph with no lexical overlap, a summary that is the only evidence, long pages with repeated irrelevant term words, missing or conflicting metadata), exercised through both `entity` modes, `context_pack` packed text and structured output. Gate d4; draft direction stands until the owner decides (d4).
- Accepted (CEO; Eng updated: the security PR merged as #6509, so the merge base is at or after `2895edb3`, v0.60.176.0): baseline arm is the wave's merge base (master after the security PR), not v0.60.174.0, so the comparison isolates this wave; confirmation runs on the branch build before merge (as the last wave did), and component retention is frozen on development data before any confirmation cell runs. "Keep only neutral pieces" never selects components using the confirmation worlds.
- Accepted (CEO): the preregistration freezes exact denominators (wrong submitted cells, and cells naming a listed wrong value, reported separately), a paired same-task same-model test for wave vs baseline on wrong-value cells with a stated minimum effect, H4 reported stratified by the `+long` variants (the knobs stay frozen), per-model results (Sol is at 0 wrong-value cells on M, so it is a ceiling for that endpoint), and abstention / non-submission alongside correctness so fewer wrong answers cannot come from more non-answers.
- Accepted (CEO): `bun scripts/model-freshness.ts` runs before preregistration and its output is recorded (project model rules).
- Accepted (Eng, native voice): any opt-in that changes document bytes (frontmatter written by `renderDoc`, which every file-backed arm reads) bumps the generator version, records new world digests and reruns the fs arm on the changed development worlds; "gbrain arm only against recorded fs cells" holds only for config-only opt-ins. The plan keeps the two kinds separate.
- Accepted (Eng, native voice): the preregistration records the measured build SHA and the path set it measured; a later master merge that touches a measured path needs a written no-effect argument in the decision record or a re-confirmation.

### Shipping

One gbrain PR for Part 1 and Part 3 step 1. One gbrain-evals PR for the plan, development record, preregistration, results and README changes. GBRA-40 merges. Stamps and migration numbers are taken at the slot.

- Accepted (DX): the gbrain PR lists, per F-item, the MEMORY_VERBS v1 additive sections (including the line saying `context_pack` computes no references, which F1 changes), verb output schemas and conformance fixtures, the `docs/evidence-delivery.md` change, the `gbrain errors` row for the refusal detail, and the llms.txt regeneration.

### Cost (estimates; actual spend is ledgered)

- **Development:** about $600–900 (the last wave's rounds cost about $1,700 over 5 rounds; this wave has fewer, more targeted items). Revised by review: add about $150 per development world if an opt-in changes document bytes and the fs arm must be rerun (150 cells at about $0.99), so about $750–1,200 in that case. The zero-provider transfer gate (d4) is free.
- **Confirmation:** about $1,450–1,700 for two worlds with a baseline arm added (revised by review). Last wave's two worlds cost about $1,100 real; the ledger showed $1,348 including an overcharge since fixed. The gbrain arm cost $0.58 per task on M against fs's $0.99 (analysis-main.md), so a gbrain baseline arm adds about $175 per world, about $350 or +33%, not +50%.
- **Part 2 rerun, if chosen:** about $150–200.
- **Part 3:** no eval spend.

### Pending Garry (defaults apply until decided)

The autoplan gate in the Review record (uc1, uc2, d1–d8, p1) is pending as well; where it covers the same item, the gate's answer decides.

| Item | Default | Alternative |
|---|---|---|
| Part 2 | retire the v1 headline, no rerun | also rerun v1 (~$150–200, parity at best) |
| Part 3 | (iii): refusal detail now, restore later only on request | (ii) restore when more specific, needs MEMORY_VERBS v2 |
| Dev budget | ~$900 | other |
| Confirmation budget | ~$1,700 with a baseline arm (revised from ~$1,900) | without a baseline arm (~$1,350), which cannot implement the same-window kill criterion |
| F3 authority labels | ship only if a real-brain convention covers them | skip F3 |

## Review record

### Autoplan run

`/autoplan` (gstack 1.91.92.0) ran unattended on 2026-10-11/12 on a Capy cloud machine (`SESSION_KIND: unattended`, ephemeral state root). Run `plan-cat40-next-wave-20261012-010042`. `autoplan guard: not enforced by this host; publication order is unverified (GUARD_NOT_INSTALLED)`. Scope: UI no (0 matches, Design skipped); DX yes (3 term matches plus `--agent-primary`: agents are the primary users of the tool output). Phase order CEO → DX → Eng. Native voice: anthropic/claude-opus-5-5 (Capy host subagent). Outside voice: openai/gpt-6.1-sol (Capy host subagent, runner `host-dispatched review`; the Codex CLI is not installed and was not needed). Model spend for both voices is host-subagent spend, recorded as unknown; no model evals ran.

Evidence checks by the orchestrator (free):
- `rca_next.py` re-run on World M: the world was regenerated with the committed command (4k base digest `84f0614a…`, 50k digest `6f08629e…`, file sha `99c53db0…`, all matching `main-world-manifest.json`) and the committed `main-cells` were used. Every World M line of `rca_next.out`, including every M ceiling, re-derived byte-identically.
- Not re-derived: every development-world number (dev-r5 and dev-r4-fs cells and the r3 world output are on another machine): "class (a) 6 of 8", "search first in 5 of 6", "H4 27 vs 27", "15 vs 36 long amended items", "+2.7 (+4.0) on dev", dev pooled 125 vs 111.
- Code spot-checks on gbrain master `da434385` (0.60.175.0): `effective_date` semantics, the two `entity` modes and `referenced_by`, `context_pack` `newer_mentions`, search `chunk_text` and evidence delivery, Part 3's refusal and ledger. Receipts are in the CEO premise table below. No sealed-world material beyond published aggregates was opened.

### CEO review (Phase 1)

Mode: SELECTIVE EXPANSION per the autoplan override (the native lane recommended SCOPE REDUCTION inside its own review; recorded as a deviation, no scope was cut without the gate).

**Premise table (REALITY rows).** `PLAN_REALITY: phase=ceo rows=7/7 missing=none unverified=1 verdict=complete`.

| # | Premise | Verdict | Receipt |
|---|---|---|---|
| P1 | One mechanism (class (a)) explains the wrong answers | verified on M; 22 items, but 18 pure-(a) cells, 2 (a)+(g), 1 (e), 1 (g) | rca_next.out "gbrain failed cells by cause" |
| P2 | H4 losses: 7 never returned, 5 returned without the sentence, 0 turn cap | verified on M | rca_next.out §2 |
| P3 | `entity` lists no account documents | partly false: only compact `names` rows list none; the full card has `referenced_by`; all 47 H4 entity calls used `names` | gbrain src/core/verbs.ts:224-268; src/core/mentions/referrers.ts:42-55 |
| P4 | F1 can sort newest-effective-first from `effective_date`/`effective_date_source` | false: effective_date is the page's own date (signed date for an amendment) | src/core/effective-date.ts:1-37; src/core/types.ts:195-201 |
| P5 | F2 does not depend on the model opening the page | true for the passage; reaches at most 3 of 7 misses (4 are short documents) | rca_next.out §2 |
| P6 | F3's markers are documented gbrain conventions | false today; search rows already pass raw `frontmatter.status` | src/core/types.ts SearchResult `status`; src/core/search/lean-rows.ts |
| P7 | Dev world reproduces the mechanism | unverified here (dev cells not on this machine) | — |
| P8 | Hard confirmation reranked in every gbrain hybrid-search cell | verified (168/168 M, 167/167 S, published aggregate) | docs/benchmarks/2026-10-10-model-ladder-hard-confirmation.md |
| P9 | `remember` refuses withdrawn claims; ledger has no principal | verified | docs/protocol/MEMORY_VERBS_v1.md:301-305; src/schema.sql:781-788 |
| P10 | Baseline arm adds about 50% to confirmation cost | false: about +33% ($0.58/task gbrain vs $0.99 fs on M) | analysis-main.md per-arm table |
| P11 | The v1 README row is only a reranker-tainted parity claim | partly: the same row carries the 0-of-100 permission result | README.md:72 |

**Consensus (CEO).** Both voices completed. The binder's reconciliation: 6 outside findings, all confirmed against a native finding; 0 disagreements; 11 native-only findings. Semantic note: the binder paired outside F5 (acceptance rule) with native F5 (baseline choice) and outside F6 (transfer gate) with native F7 (M in-sample); the closer native counterpart of outside F5 is native F6 (endpoints cannot detect a few-cell effect). Both pairings agree in direction.

| Dimension | Claude (Opus 5.5) | GPT-6.1 Sol | Consensus |
|---|---|---|---|
| Premises valid? | no: P3, P4, P6, P10 | no: dates, entity route, F3 markers | CONFIRMED (not valid as written) |
| Right problem? | yes (stale record first) | yes, reframed as delivering dated evidence | CONFIRMED |
| Scope calibration? | F1 wrong surface, F3 too broad | F1/F3 overreach, F2 mechanism unproven | CONFIRMED |
| Alternatives explored? | no: entity-scoped exact-term lane | no: delivery-unit comparison | CONFIRMED (different alternatives) |
| Competitive/real-brain risk? | benchmark gain overstates real brains | conventions untested off-generator | CONFIRMED |
| 6-month trajectory? | build on links toward valid-time claims | validity contract before ordering | CONFIRMED |

**Findings (both voices; full prose in the run directory).** Native: 1 Critical, 5 High, 7 Medium, 3 Low, 1 Informational. Outside: 5 High, 1 Medium. Confirmed by both: F1's date semantics; F1 misses the compact `names` route and duplicates `referenced_by`; F2 belongs in evidence delivery and max-term overlap does not reliably pick the deciding sentence (outside probe: below another sentence in 9 of 12 parsed long-page hits in M's lost cells); F3's authority inference; the acceptance rule and baseline; the in-sample / transfer problem. Native only: endpoints cannot detect a few-cell effect, baseline cost +33%, Part 2 README split, entity-scoped exact-term lane, payload crowding of `newer_mentions`, firing counters, Part 3 after the security PR, model freshness check, F4 wording order, item/cell conflation, six-month note.

**NOT in scope.** Turn-cap changes (fs fails 31 of the 32 turn-cap cells gbrain fails), model-specific prompting, owner-phrase resolution, Part 3's `restore: true` (later, owner-requested only), a terms-effective metadata extractor that parses body sentences (fixture-shaped), changing the frozen knobs.

**What already exists.** `referenced_by` on the full card (src/core/verbs/entity-card.ts:110-165); referrer rows with date, date_source and trust fields (src/core/mentions/referrers.ts:42-55); `newer_mentions` on `context_pack` (src/core/mentions/newer-mentions.ts); the search supersession stamp and frontmatter `supersedes` mapping (src/core/search/hybrid.ts:670-797); raw `status` on search rows; trust tiers; evidence delivery (src/core/search/evidence-delivery.ts, docs/evidence-delivery.md); the lean-row allowlist (src/core/search/lean-rows.ts:31-40); the withdrawal refusal (src/core/facts/withdrawal.ts:15-21). The draft plan reused none of them explicitly.

**Error & Rescue Registry.** 13 codepath rows in the native review; 2 GAPs (a draft listed as a governing record; the wrong passage chosen on a real contract) and 1 conditional GAP (protected-body boundary if F2 is built outside evidence delivery).

**Failure Modes Registry.**

```
  CODEPATH            | FAILURE MODE                          | RESCUED? | TEST? | USER SEES?            | LOGGED?
  F1 ordering         | non-governing record listed first     | N        | N     | silent wrong answer   | N   <- CRITICAL GAP
  F1 records          | draft-typed amendment listed          | N        | N     | silent                | N   <- CRITICAL GAP
  F1 compact rows     | 50-name batch payload blowup          | N        | N     | slow, costly call     | N
  F2 passage          | wrong sentence on a real contract     | N        | N     | silent, plausible     | N   <- CRITICAL GAP
  F2/F3 fields        | stripped by lean rows (remote)        | N        | N     | silent no effect      | N   <- CRITICAL GAP
  context_pack budget | records crowd out newer_mentions      | N        | N     | silent regression     | N   <- CRITICAL GAP
  Part 3 detail       | detail shown without visibility       | must     | N     | disclosure            | N
  confirmation        | baseline confounded by master drift   | N        | n/a   | wrong verdict         | n/a
```

**Dream state delta.** After this wave, with the review's fixes, an agent sees that a newer record amends the one in front of it, gets the deciding passage of long records through evidence delivery, and sees drafts labeled by a documented status. Still missing against the 12-month ideal: terms-effective dates as data, typed valid-time claims, and an "as of D" answer that names the governing record.

**Completion summary.** Mode SELECTIVE EXPANSION; 23 findings across both voices (1 Critical); premise table 11 rows, 3 false, 2 partly false, 1 unverified; 5 critical gaps in the failure-modes registry; 2 user challenges and 4 one-voice direction changes go to the gate; Design section skipped (no UI scope).

<!-- autoplan-accepted:ceo -->
- RCA wording: "22 wrong-value cells" is stated as 22 class (a) items in 18 pure-(a) cells, 2 (a)+(g), 1 (e), 1 (g).
- F1 record rows label the page date as a page date (`date`, `date_source`); list order is never presented as governance; a draft-status page is never listed without its status.
- F2's new fields are added to the lean-row allowlist; F2 is tested on a fixture where term words recur in non-deciding clauses; a Sonnet harm check is preregistered for dev.
- F4's sentence is written after F1's placement is settled and names only fields the model receives in the mode it calls.
- Every new stage reports whether it fired (explain contributions or debug counters); the dev record reports firing rates.
- Payload guard: records capped per call; $/task and tool-result tokens are dev guard metrics; a deterministic test shows `newer_mentions` still packs under the default `context_pack` budget with records present.
- The entity-scoped exact-term lane is the fallback dev arm if F1 and F2 do not fire or do not move H4.
- README states that the Hard confirmation is a different workload and never implies the v1 comparison was remeasured.
- Part 3 step 1 branches after the security PR, reuses its visibility predicate, is tested on both engines for the plain refusal, is listed under behavior changes with a named consumer, and is documented as covering the exact normalized claim only.
- M development results are labeled in-sample and diagnostic.
- Baseline arm is the wave's merge base (master after the security PR); confirmation runs on the branch build before merge; component retention is frozen on development data.
- Preregistration freezes exact wrong-answer denominators, a paired wave-vs-baseline test with a minimum effect, H4 stratified by `+long`, per-model results with Sol's ceiling called out, and abstention / non-submission reported with correctness.
- `bun scripts/model-freshness.ts` runs before preregistration and its output is recorded.
- Confirmation cost is ~$1,450–1,700 (baseline arm +~$350, +33%).
<!-- /autoplan-accepted:ceo -->

### DX review (Phase 2.5)

Scope: DX enabled by `--agent-primary` (agents read every tool result) plus 3 developer-facing term matches. Persona: a frontier agent over remote MCP reading lean rows; secondary persona: the human integrator enabling records on their own brain and reading the benchmark claims. Mode POLISH (native lane's recommendation, auto-chosen).

**Consensus (DX).** Both voices completed. The binder's line-level reconciliation found 0 confirmed, 0 disagreements, 5 outside-only and 15 native-only findings. Semantically, four of the five outside findings match native ones: enrollment contract (outside DX1 ≈ native DX3), one continuation shape (outside DX3 ≈ native DX4), capped or incomplete lists must not read as empty (outside DX4 ≈ native DX13), and Part 3's typed refusal object on every surface (outside DX5 ≈ native DX8). Outside DX2 (F2 inert on default non-conversation searches) is new and is the strongest outside finding; native DX12 touches its off switch only. No voice disagreed with another.

| Dimension | Claude (Opus 5.5) | GPT-6.1 Sol | Consensus |
|---|---|---|---|
| Getting started (agent's first useful call) | 4/10: `names` rows carry nothing | F2 inert on default calls | CONFIRMED gap |
| API ergonomics | 4/10: four continuation shapes | continuation must preserve membership | CONFIRMED |
| Errors and refusals | 5/10: Part 3 detail has no location | typed additive object on every transport | CONFIRMED |
| Documentation | 3/10: protocol docs, schemas, spec missing | enrollment example missing | CONFIRMED |
| Upgrade path | 5/10: referenced_by parity at risk | — | native only |
| Dev environment (benchmark loop) | 5/10: transcript-capped token metrics | — | native only |
| Community | 6/10 | — | native only |
| DX measurement | 6/10: guard measures `text`, not `cards[]` | incomplete index shows false totals | CONFIRMED (different gaps) |

**DX scorecard (native).** Getting Started 4→6, API 4→7, Errors 5→7, Docs 3→7, Upgrade 5→7, Dev Environment 5→7, Community 6→7, Measurement 6→8. Overall 4.8/10 → 7.0/10 if the accepted amendments land. TTHW (agent, H4 median on M): 18 calls, 8 turns, 263,173 result characters; target fs-parity correctness at no more than today's calls and characters. TTHW (integrator): unknown today; target one documented pack line plus one read-only check command.

**Developer journey map.**

```
STAGE        | AGENT / INTEGRATOR DOES                       | FRICTION                                              | STATUS
1 Discover   | reads tool schemas + served instructions      | instruction 7: batch via `names`, then "walk           | d5, d6
             |                                               | referenced_by" (absent there); "prefer the newest"     |
2 Install    | integrator wants records on contract pages    | no pack field names record types; no "amends" field   | accepted (enrollment)
3 First call | `entity` names / `context_pack`               | no records, no continuation; backlink_count 0 beside  | uc1, d5, accepted
             |                                               | 17 referrers                                           |
4 Real use   | search, get_backlinks, get_page               | four continuation shapes; long page not signaled      | accepted, d3
5 Debug      | `remember` refused after `forget`             | sub-cause only in a message prefix                    | accepted (typed object)
6 Upgrade    | reads MEMORY_VERBS, schemas, README claims    | docs, schemas, README sentences not in the ship list  | accepted
```

**Empathy narrative (observed, one lost Sonnet H4 cell on M).** The agent batched three account names with `entity` `names` as the served instructions advise and got a CRM record and an account sheet each, with no sign that contracts exist. Its next search returned a 40,000-plus-character result in which one long amendment appeared as a boilerplate chunk, with nothing on the row saying the page was long or partly shown. It concluded the amendments did not touch the asked term and answered the contract's original value. It handled the "later effective wins" and "not yet effective" items correctly by reading body dates itself.

**NOT in scope (DX).** Hoisting per-row constants (`trust_tier`, `origin`, `source_id`, 8.6% of M result characters) into a response header; removing the `cards[]`/`text` duplication in `context_pack`; a `get_page` range or in-page search parameter; `search` `since`/`until` parity; better unknown-parameter suggestions (native DX14). All are follow-up candidates, none is written to TODOS.md by this run.

**What already exists (DX).** `referenced_by` groups with an executable `next`; evidence delivery's `delivered` object and the snippet marker that names the `get_page` recovery; the `supersedes` link type and frontmatter mapping rules (`gbrain-base-v2.yaml:400`, `company-brain.yaml:173-175`); the lean-row allowlist; verb output schemas and conformance fixtures; the agent error envelope's `reason`/`detail`/`fix` slots; `date-labels.ts` wording that a page date is never a contract's validity date.

**DX implementation checklist.** Enrollment declaration + example + read-only check; records as an extra view with `referenced_by` parity; one executable continuation shape with exact-remainder paging; capped/undeclared/degraded states visible; F2 activation on default non-conversation searches with budget accounting and a named off switch; payload guard on serialized results; Part 3 typed refusal object on three surfaces; protocol docs, schemas, fixtures, errors row, llms.txt in the ship list; README sentence-by-sentence dispositions.

<!-- autoplan-accepted:dx -->
- F1 reads a documented pack-level record-type declaration (empty by default, F1 off when absent); "amends" is the existing `supersedes` link via a frontmatter mapping rule, never a body parser; a copy-paste pack example, a generic Markdown example with expected output, and a read-only check ship with it; unrecognized types stay in ordinary references; the benchmark world opts in through the same declaration before dev cells, and F1's benchmark points are attributed to that opt-in.
- Records are an additional view; `referenced_by` membership and `get_backlinks` parity are unchanged; record rows reuse the `referenced_by` row shape without previews or per-row constants.
- One continuation shape: the card's executable `next {tool, arguments, requires_surface?}`; exact-remainder paging across record types (`types[]` on `get_backlinks` or one `next` per type); capped lists keep `total` + `next` + reason; undeclared types say so; coverage/degraded notices propagate.
- In `context_pack`, F1 uses `referenced_by_count` or no count, and `backlink_count`'s description says what it excludes.
- F2 activates on ordinary remote searches over non-conversation pages without widening unrelated pages; `snippet_chars`/`token_budget` precedence is specified; passages count in the delivery budget; firing is reported via `delivered` and the snippet marker; a named `search.*` key and default are documented; `return_unit: "chunk"` stays byte-identical; tests assert on serialized lean MCP output.
- The payload guard uses serialized tool-result characters from attempts `chars`; notice characters are reported separately and notice state is identical across arms; the per-call record cap is a stated number.
- Part 3's refusal detail is one additive typed object (not named "scope") on the immediate refusal, batch item error and failed receipt, through every transport; the legacy prefix is unchanged; absence carries no meaning; stdio/HTTP/CLI JSON tests.
- The gbrain PR lists MEMORY_VERBS sections, output schemas, conformance fixtures, the evidence-delivery spec change, the errors row and llms.txt regeneration.
- Every sentence of README.md:141-148 and row 72 gets a disposition, including the per-task cost sentence; the new Hard row states workload, models, reranker state and per-model cost.
<!-- /autoplan-accepted:dx -->

### Eng review (Phase 3, last)

`PLAN_REALITY: phase=eng rows=7/7 missing=none unverified=3 verdict=complete` (unverified: dev-world figures, the outside voice's 9-of-12 probe, the 168/167 reranked counts, which are published aggregates). Scope accepted as-is; the native lane's smaller arrangement is pending through the gate items.

**Consensus (Eng).** Both voices completed. The binder's line-level reconciliation found 0 confirmed, 0 disagreements, 6 outside-only and 18 native-only findings. Semantically, three outside findings match native ones: amendments as `supersedes` trigger whole-page down-ranking (outside E1 ≈ native E1), the enrollment key cannot load on the baseline (outside E2 ≈ native E2), and F2's default activation must not leak into other surfaces (outside E6 ≈ native E4/E7 in spirit). Outside-only: referrer caps can starve records (E3), F2 input work is unbounded (E4), canonical alias mismatch (E5). Native-only: world-bytes opt-in invalidates recorded fs cells (E3), firing signal stripped by lean rows and head-cut by `snippet_chars` (E5), keyword queries without term words (E6), push path (E7), N+1 on names (E8), zero text budget headroom (E9), per-item config keys (E10), Part 3 receipt and second refusal site (E11), security PR already merged (E12), Part 3 out of the eval-gated PR (E13, gate d7), master-drift rule (E14), names-mode read-option parity (E15, urgent, outside this plan), `types[]` vs per-type `next` (E16), Opus $0.86 (E17), records ORDER BY (E18). No disagreements.

| Dimension | Claude (Opus 5.5) | GPT-6.1 Sol | Consensus |
|---|---|---|---|
| Architecture sound? | no: amends-as-supersedes, strict manifest, push path | no: amends-as-supersedes, strict manifest | CONFIRMED |
| Edge cases covered? | no: keyword queries, snippet head-cut, multi-row ledger | no: cap starvation, alias mismatch | CONFIRMED (different gaps) |
| Tests sufficient? | 9 of 38 paths tested, 29 gaps | final serialized output tests needed | CONFIRMED |
| Security? | names-mode read-option parity (urgent, not owned) | no new surface beyond F2 input bounds | native only (urgent) |
| Hidden complexity? | world-bytes opt-in reruns fs; budgets at zero headroom | F2 whole-page input work | CONFIRMED |
| Performance? | N+1 on 50-name batches | unbounded page fetch | CONFIRMED |

**Architecture (after amendments).**

```
 agent (remote MCP, lean rows)
   |-- entity names:[..] --> one batched referrer query (enrolled types only, cap before hydrate)
   |                          -> per row: records (page date + source, status, amends link) + total + next per type
   |-- entity name -------> full card: referenced_by unchanged (+ records view)
   |-- context_pack (pull) -> cards + newer_mentions, then records last (pull verb only)
   |   ambient push path ---> unchanged (600 ms deadline)
   |-- search -------------> hybrid / keyword ranking (no new supersedes links from amendments)
   |                          -> evidenceOutput: F2 policy resolved at the search caller, config key default off
   |                          -> passage leads delivered text; delivered {unit, reason} kept in lean rows
   |-- remember -----------> refusal (+ typed withdrawn object on refusal, batch item, receipt; both refusal sites)
 pack: "amends" link type (non-ranking) via frontmatter mapping; record types via per-arm config key
 harness: per-item config arms on one build; world opt-in config-only, or new digests + fs rerun if bytes change
```

**Codepath-to-test map (native, abridged).** Tested today: referrer privacy, cursor and groups; `names` resolve/miss/siblings; `newer_mentions` packing; evidence-delivery chunk/implied-auto goldens and protected-body sanitizing; schema budgets; instruction content; refuse-before-accept and the #6509 visibility predicate. Gaps that become required proof: records or count + `next` on names rows on both engines; exact-remainder continuation; 50-name cap and perf; undeclared vs empty; draft status on rows; amends link with no ranking change (critical); push output unchanged (critical); records packing order under budgets 1500/2000; F2 on-path golden, keyword name-only no-fire, `snippet_chars` 300 survival, lean firing signal, recurring-term fixture; Part 3 multi-row ledger, second site, receipt persistence, identical stdio/HTTP/CLI object; generator version and digest record with fs rerun (critical); per-item config arms. Coverage today 9 of 38 paths. Test plan on disk: `~/.gstack/projects/garrytan-gbrain-evals/user-plan-cat40-next-wave-eng-review-test-plan-20261012-013719.md` (machine-local; this section is its durable summary).

**NOT in scope (Eng).** Turn-cap changes; model-specific prompting; owner-phrase resolution; `restore: true`; the v1 rerun (Part 2 alternative); a body parser for "Effective X, the Y change to Z" (fixture-shaped); fixing names-mode read-option parity (security follow-up owner).

**What already exists (Eng).** Referrer CTE and continuation shape; evidence delivery and budgets; lean projection; pack `frontmatter_links`; per-arm config and description overrides in the harness (`eval/runner/cat40/gbrain-arm.ts`); the merged withdrawal visibility predicate (#6509); `OperationError` additive fields. Deliberately not reused: `supersedes` for amendments.

**Failure modes registry (Eng).**

| New path | Failure | Planned handling | User sees |
|---|---|---|---|
| amends as `supersedes` | governing contract halved in search | replaced by a non-ranking link (accepted) | was silent wrong answer: critical gap, now closed by amendment |
| enrollment as strict pack key | baseline cannot load the pack | config key per arm (accepted) | — |
| world opt-in bytes | fs cells compared against another digest | new digests + fs rerun (accepted) | was silent invalid comparison: critical gap, now closed by amendment |
| records in shared assembler | push hook misses its deadline | pull verb only (accepted) | — |
| records on names rows | 100k-character or slow batch | batched query, stated cap, perf test (accepted) | — |
| F2 + `snippet_chars` | passage cut away, firing invisible | passage leads; lean `delivered` (accepted) | — |
| F2 default change | every long-page search changes shape | default off, two goldens (accepted) | — |
| Part 3 second site | detail without visibility check | same predicate at both sites (accepted) | — |
| text budgets | budget test fails | name the cut or record a raise (accepted) | CI |

**URGENT, outside this plan.** One native finding (Eng E15) concerns read-option parity between compact `entity names` rows and the single card. It belongs to the security follow-up owner of #6509; details are withheld here.

**Completion summary (Eng).** 24 findings across both voices (9 High, 12 Medium, 2 Low, 1 Informational); 2 critical gaps in the registry, both closed by accepted amendments; 29 test gaps listed as required proof; 2 direction changes to the gate (d7, d8); the plan's security prerequisite has already merged.

<!-- autoplan-accepted:eng -->
- Replacement of the DX clause "\"amends\" is the existing `supersedes` link": amends is a separate non-ranking link type declared in the pack and fed by a frontmatter mapping rule; `supersedes` stays for whole-record replacement; tests cover unchanged terms, future-effective amendments and genuine replacement through final search scores and labels.
- Record-type enrollment is a per-arm config key (ignored by older builds); the pack carries only the link mapping; baseline- and wave-compatible pack variants are frozen, proven identical apart from the declaration, and hashed before paid cells; enrollment and relationship rules agree on canonical aliases.
- Records are filtered by enrolled type inside the shared membership query before ORDER BY/LIMIT/hydration, with record-only totals and keysets; names rows use one batched multi-target query; the per-call cap is enforced before hydration and stated (start: 3 per name, 24 per call); a names-mode perf test exists; records have an explicit ORDER BY and cursor; continuation is one executable `next` per record type.
- Records are computed only in the `context_pack` pull verb; a test pins the ambient push output unchanged.
- Before compact rows carry records, the security follow-up owner confirms names-mode read-option parity with the single card; F1 names tests include such an entity.
- F2 is behind its own `search.*` config key, default off until confirmation; golden `evidence-delivery-golden.test.ts:78` stays as the off-path contract; a frozen on-path golden is added; activation is resolved at the search/query caller so recall, think and `assemble_evidence` stay byte-identical.
- The F2 passage leads the delivered text; lean rows carry compact `delivered {unit, reason}` when F2 fired; F2 has candidate-page, input-byte and deadline limits with a size preflight and bounded batched fetch; F2 adds no text when the query names no term; dev results are stratified by match mode and term presence.
- Every instruction or description text change names the cut that pays for it or records a budget raise per `test/mcp-schema-budget.test.ts`.
- Each F-item has its own config key and documented default; dev arms run on one build via per-arm config and description overrides.
- Part 3 detail reads only `fact_withdrawals`, with a deterministic row rule; persists in the write receipt outcome; the commit-time refusal site applies the same predicate; Part 3 step 1 can start now (#6509 merged).
- Baseline merge base is at or after `2895edb3` (v0.60.176.0).
- Any opt-in that changes document bytes bumps the generator version, records new digests and reruns fs on changed dev worlds; config-only opt-ins keep recorded fs cells.
- The preregistration records the measured SHA and path set; a later master merge touching a measured path needs a written no-effect argument or re-confirmation.
- Opus gbrain cost on M is $0.86 per task.
- Development cost becomes about $750–1,200 if document bytes change (fs rerun); otherwise $600–900.
<!-- /autoplan-accepted:eng -->

### Final approval gate (pending Garry; gate_rev 1)

The run ended `status=gate_pending`; nothing was approved. Reply grammar: `all`, `<id><option>` tokens (for example `uc1b uc2b`), or `all except <tokens>`; bare yes/no is rejected. Approval items (uc1, uc2, p1) stay pending until answered; auto items (d1–d8) take option a if unanswered.

| Id | Kind | Item | a | b | Native (Opus 5.5) | Outside (GPT-6.1 Sol) |
|---|---|---|---|---|---|---|
| uc1 | approval | F1 placement: compact `names` rows and `context_pack`, built from the existing referrer path, instead of a new section on the full card | keep the plan as reviewed | accept the change both reviewers recommend | b | b |
| uc2 | approval | F3: drop the automatic not-binding inference and heuristics; propagate existing `status`/trust fields plus a documented `status: draft\|unsigned` convention | keep | accept | b | b |
| d1 | auto | Part 2: keep the 0-of-100 permission result when retiring the v1 row | keep | accept | b | not raised |
| d2 | auto | F1 ordering by page date cannot express which record governs; add a validity contract or narrow F1 to candidate evidence | keep | accept | b in substance (rated it Critical; fix: label page dates, no governance by order, optional documented validity key) | b |
| d3 | auto | F2: compare existing delivery units at a fixed budget before committing to a lexical passage picker | keep | accept | b in substance (build F2 inside evidence delivery) | b |
| d4 | auto | Add a zero-provider transfer and negative-control gate before paid dev | keep | accept | partly (label M in-sample, decide on an unseen dev seed) | b |
| d5 | auto | Records or a `next` on compact rows, and fix instruction 7's walk advice | keep | accept | b | not raised |
| d6 | auto | Replace F4's two new description sentences with one general edit to served instruction 7 | keep | accept | b | not raised |
| d7 | auto | Ship Part 3 step 1 in the next batched gbrain wave PR, not the eval-gated Part 1 PR | keep | accept | b | not raised |
| d8 | auto | Do not map amendments to `supersedes` | keep | accept | b in substance (Eng E1, High) | b |
| p1 | approval | Plan approval | a approve as-is · b approve with the overrides above · c interrogate · d revise (every phase reruns, Eng last) · e reject | | — | — |

Note on defaults: the tool's default for every d item is "keep your direction". For d2 and d8 both voices found a factual defect (rated Critical and High), and the accepted amendments already fix d8's mechanism and add page-date labeling for d2. Answering d2a keeps the drafted "newest effective first" ordering.

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|----------|
| 1 | CEO | Correct the "all 22 are class (a)" wording to items vs cells | Mechanical | P1 | Re-derived output shows 18 pure-(a) cells of 22 | leave as is |
| 2 | CEO | Hold F1's effective-first ordering for the gate (d2) and add a page-date labeling requirement now | Mechanical (requirement) + gate | P1 | Both voices: ordering by signed date points at the wrong record | silently rewriting F1's ordering |
| 3 | CEO | F1 placement (compact rows, context_pack, reuse referenced_by) to the gate as uc1 | User Challenge | — | Both voices flagged it as a direction change | auto-deciding |
| 4 | CEO | F2 mechanism to the gate as d3; accept lean-row, recurring-term fixture and Sonnet harm check now | Taste + Mechanical | P4, P1 | Evidence delivery exists; benchmark boilerplate has no term words | parallel passage picker without guards |
| 5 | CEO | F3 scope to the gate as uc2 | User Challenge | — | Both voices flagged it as a direction change | auto-deciding |
| 6 | CEO | Firing counters for every new stage | Mechanical | P1 | Null dev results are unreadable without them | — |
| 7 | CEO | Payload guard and newer_mentions packing test | Mechanical | P2 | context_pack budget is shared | — |
| 8 | CEO | Entity-scoped exact-term lane as fallback arm, not a planned arm | Taste | P3, P6 | Costs a dev arm; only needed if F1/F2 fail | adding it as a planned arm |
| 9 | CEO | README wording: Hard is a different workload | Mechanical | P5 | Avoids implying a remeasure | — |
| 10 | CEO | Part 2 permission-result split to the gate as d1 | Taste | P1 | One voice; the row carries an unrelated result | auto-splitting |
| 11 | CEO | Part 3 step 1 after the security PR, reusing its predicate; exact-claim documentation | Mechanical | P1, P5 | Same path as the security fix | shipping before it |
| 12 | CEO | Label M dev results in-sample | Mechanical | P5 | F-items were designed from M | — |
| 13 | CEO | Transfer / negative-control gate to the gate as d4 | Taste | P1 | One voice flagged it as a direction change | auto-adding |
| 14 | CEO | Baseline = wave merge base; confirm on branch before merge; freeze retention on dev | Taste | P1, P3 | Isolates the wave from master drift and the security PR | v0.60.174.0 baseline |
| 15 | CEO | Freeze endpoints: denominators, paired test, H4 by `+long`, per-model, abstention | Mechanical | P1 | Both voices: current rule passes on a one-cell change | — |
| 16 | CEO | Model freshness check before preregistration | Mechanical | P1 | Project model rules | — |
| 17 | CEO | Confirmation cost corrected to ~$1,450–1,700 | Mechanical | P5 | Per-arm $/task from analysis-main.md | +50% estimate |
| 18 | DX | Instruction 7 / compact-row records to the gate as d5 (new evidence for uc1) | Taste | P1 | One voice flagged a direction change | auto-deciding |
| 19 | DX | F4 moved into instruction 7 to the gate as d6 | Taste | P4 | One voice; duplicates existing served guidance | auto-deciding |
| 20 | DX | Documented record-type enrollment, `supersedes` for amends, read-only check; benchmark opts in | Mechanical | P1, P5 | Both voices: no shipped pack declares record types | keying on benchmark type strings |
| 21 | DX | Records as an extra view; `referenced_by` parity unchanged | Mechanical | P4 | Avoids an unlisted behavior change | moving rows out of `referenced_by` |
| 22 | DX | One executable continuation shape; capped/undeclared/degraded states visible | Mechanical | P5 | Both voices | four shapes |
| 23 | DX | `context_pack` count naming | Mechanical | P5 | Two disagreeing counts on one card | new count field |
| 24 | DX | F2 activation on default searches, budget accounting, named off switch | Mechanical | P1 | Outside voice: `auto` exits early on non-conversation hits | unit-only patch |
| 25 | DX | Payload guard on serialized results; notice state fixed across arms | Mechanical | P1 | `cards[]` doubles payload; transcripts cap at 40k | text-only guard |
| 26 | DX | Part 3 typed refusal object on three surfaces | Mechanical | P5 | Both voices | message-prefix only |
| 27 | DX | Protocol docs, schemas, fixtures, errors row, llms.txt in the ship list | Mechanical | P1 | Additive-field precedent | — |
| 28 | DX | README sentence-by-sentence dispositions incl. per-task cost | Mechanical | P1 | Hard M contradicts the "twice as much" sentence | partial retirement |
| 29 | Eng | Replace "amends = supersedes" with a non-ranking amends link (supersedes the DX clause) | Mechanical | P1, P5 | Both voices: supersedes halves the governing contract's score | keeping the DX clause |
| 30 | Eng | Enrollment via per-arm config key; frozen pack variants | Mechanical | P3 | Strict manifest breaks the baseline arm | pack-level key |
| 31 | Eng | Filter enrolled types in the membership query; batched names query; stated cap; per-type `next` | Mechanical | P5, P3 | Cap starvation and N+1; `types[]` has no budget | `types[]` param |
| 32 | Eng | Records in the pull verb only | Mechanical | P1 | Push path has a 600 ms deadline | shared assembler |
| 33 | Eng | Names-mode read-option parity confirmed by the security follow-up owner first | Mechanical | P1 | Urgent finding outside this plan | — |
| 34 | Eng | F2 behind a config key, default off; two goldens; caller-resolved policy | Mechanical | P5 | Default-on retires a normative golden | default-on |
| 35 | Eng | Passage leads text; lean `delivered`; input limits; no text without a term | Mechanical | P1 | `snippet_chars` head cut; 352 term-less keyword queries | appended passage |
| 36 | Eng | Text changes name their budget cut | Mechanical | P5 | Zero headroom | — |
| 37 | Eng | Per-item config keys, one build | Mechanical | P3 | Harness supports per-arm config | build-vs-build pairs |
| 38 | Eng | Part 3 row rule, receipt persistence, second site; can start now | Mechanical | P1 | #6509 merged | — |
| 39 | Eng | Part 3 out of the eval-gated PR to the gate as d7 | Taste | P6 | One voice; changes shipping structure | auto-splitting |
| 40 | Eng | Baseline at or after `2895edb3` | Mechanical | P5 | Security PR merged | v0.60.174.0 |
| 41 | Eng | World-bytes opt-in reruns fs with new digests | Mechanical | P1 | `renderDoc` feeds every file arm | reusing recorded fs cells |
| 42 | Eng | Preregister measured SHA and path set; drift rule | Mechanical | P1 | Master moves during confirmation | — |
| 43 | Eng | Opus $0.86, dev cost range with fs rerun | Mechanical | P5 | Re-derived from results.jsonl | — |
| 44 | Eng | Revised expected-effect paragraph; ceilings unchanged | Mechanical | P5 | Per-item reach narrower than drafted | per-item point estimates |
