# Reranker settings, addendum: Voyage rerank-3 and rerank-3-lite (GBRA-86)

**Status, 2026-10-13: preregistered before any counted cell of this addendum ran.** No `rerank-3` or `rerank-3-lite`
result on the eval questions has been seen. A tokenizer check sent the first 5 documents of one frozen list to each
model; it read only billed tokens and latency, not rankings (all three models billed the same 3,139 tokens). Sina
approved the run with a hard cap of $5 in provider spend.

This extends [2026-10-12-rerank-settings-preregistration.md](2026-10-12-rerank-settings-preregistration.md) (merged in
gbrain-evals#141). There, none of 18 cheaper `rerank-2.5` / `rerank-2.5-lite` settings passed, so the shipped setting
(50 candidates × 1,400 tokens × `rerank-2.5`) stayed. Voyage now prices `rerank-3` like `rerank-2.5` ($0.05 per
million tokens) and `rerank-3-lite` like `rerank-2.5-lite` ($0.02), and lists the 2.5 models as older. The question
is whether either newer model gives a setting that is cheaper, faster, or both, without losing retrieval quality.

## What stays the same

Everything the first preregistration fixed: the 300 questions (`2026-10-12-rerank-settings/subset-k300.json`), the
300 PGLite brains built at gbrain master `0832f9fe`, the frozen candidate lists, the shim at `846fa6dd` with the
semantic-cache line, the replayed expansion and query embeddings, the two queries per question (real query and
readiness probe), the metrics and the decision rule.

The brains and frozen lists are the ones built for #141, kept on the run machine. Every cell call checks the reranker
request against its frozen list (SHA-256 of query and documents), as before, so a list that no longer reproduces
shows up as a mismatch and counts against the cell.

## Cells

- **Reference, re-run:** 50 × 1,400 × `rerank-2.5`, with fresh provider calls (the proxy's rerank cache is keyed
  separately for this addendum) so its latency is measured under the same conditions as the new cells. Its rankings
  should match #141's reference; any difference is reported.
- **`rerank-3`:** 50 × 1,400, 25 × 1,400, 15 × 1,400 and 25 × 512.
- **`rerank-3-lite`:** the same four.

9 cells × 600 queries = 5,400 queries. On each question all nine cells run back to back, real query then probe, so
every cell sees the same load.

## Metrics

As in the first preregistration, plus:

- **Reranker latency per query:** wall time of the Voyage rerank call measured at the proxy, from request sent to
  response received, for each of the cell's 600 calls. Reported as p50 and p95. Four workers run concurrently, as in
  #141, so this is latency under that load from the run machine, not an isolated benchmark. Calls the proxy had to
  retry (HTTP 429 or 5xx) keep their full time, retries included, and are counted.

## Decision rule

Unchanged. A cell is acceptable against the re-run reference, on the same questions, when strict recall@10 is at least
the reference's minus 2, no question type loses more than 2 net on strict recall@10, mean nDCG@10 is at least the
reference's minus 0.005, real-query and probe clean reads are each at least the reference's minus 2, and at most 2% of
its queries errored or mismatched.

**Recommendation:**

1. The acceptable cell with the lowest combined cost per query that is cheaper than the reference, with its cost cut.
   If two acceptable cells are within 5% of each other on cost, the one with the lower p50 latency wins.
2. If no cheaper cell is acceptable, an acceptable cell at the reference's cost (`rerank-3` 50 × 1,400) is recommended
   only if its p50 latency is at least 10% lower than the re-run reference's.
3. Otherwise, keep the current default.

Latency never makes an unacceptable cell acceptable.

## Size and cost

From the frozen lists (local token estimates; Voyage billed within 1% of them in #141, and `rerank-3` bills the same
tokens as `rerank-2.5`):

| cells | tokens | estimate |
|---|---|---|
| reference re-run (`rerank-2.5`) | 17.6M | $0.88 |
| `rerank-3`, four cells | 39.3M | $1.96 |
| `rerank-3-lite`, four cells | 39.3M | $0.79 |
| **total** | | **$3.63** |

No embeddings or expansion are paid: both are replayed from the cache. The proxy keeps this addendum's spend in its
own ledger and refuses any call that would take it past $4.70, under the $5 cap. All figures are estimates from
Voyage's usage counts at list price, not metered invoices. If the cap stops the run, questions without all nine cells
are dropped from every cell.

## Publication

Results are published as aggregates only: the per-cell table, per-type losses and latency percentiles
(`2026-10-13-rerank3-addendum/results/verdict.json`). No per-question rows are committed. This recommends a setting
and changes no gbrain default.
