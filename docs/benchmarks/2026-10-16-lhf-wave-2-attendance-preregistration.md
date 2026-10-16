# Preregistration: paraphrased attendance questions (gbrain LHF wave 2, item 9, 2026-10-15)

Frozen on October 15, 2026, in its own commit, before gbrain's attendance lexicon change is committed and before any scored run of it. Nothing below changes after a run; a later change is a dated amendment at the end. Plan: [LHF wave 2](../plans/2026-10-15-lhf-wave-2/PLAN.md), item 9 and its round-2 disposition ("Item 9 narrowed").

## Question

Attendance retrieval in gbrain fires only on "attended" / "attendees" (`src/core/search/relational-intent.ts` at gbrain master `7f3c9f5f`), so the 150 paraphrased attendance questions of the relational paraphrase split fired 0 times on world-v1-attendees (2026-10-06). The change adds exactly these forms: "were present at", "was in the room for", "took part in", "participated in", "sat in on", and the "participants" noun frame. No broader verbs ("joined", "was at", "went to") and no resolver guard. Do paraphrased attendance questions that a user would write, and that the lexicon author never saw, now reach attendance retrieval, without routing employment, education or location questions to it?

## Evidence class

- **Held-out (counted):** 30 attendance questions written on 2026-10-15 by an author other than the lexicon author, who did not read gbrain's lexicon. The file stays off every shared surface until the lexicon change is committed; only its hash is published here. Each record names its meeting by its exact title and carries `meeting_slug`; gold is the meeting's `## Attendees` list in `eval/data/world-v1-attendees`. Records `h-att-001` to `h-att-030`, 30 different meetings (14 Demo Days, 8 board meetings, 8 1:1s).
  - `attendance-heldout-30.jsonl` sha256 `41f5a7f99a52de31d5ec0f227d43a82e8c38394cfccf4e6e9345a2ffa70b57a4`
- **Competing intent (counted, not sealed):** 30 questions by the same independent author that must not route to attendance: employment (8), investment (5), advising (3), founding (3), education (5), location (6), some deliberately sharing attendance vocabulary ("participated in the ... funding round", "attended" a school).
  - `competing-intent-30.jsonl` sha256 `ef3a69c02bc7fb50138ad766c1752ceb3bcde7f83b3087082d6cd3e7409b399b`
- **Development (report only):** the existing relational paraphrase split (150 runs) and the "Who attended X?" template split (150 runs) of N9 on world-v1-attendees. Their frames informed the lexicon, so they cannot count.

## Build

- Base: gbrain `origin/master` at the wave's merge base (`7f3c9f5f`, v0.60.252.0). Branch: the LHF wave 2 integration head that contains item 9; its SHA is recorded in the result before scoring.
- Corpus `world-v1-attendees` as committed (`bun eval/generators/world-v1-attendees.ts --check`).
- Hermetic: keyword search, provider and TypeSafe keys stripped, fresh `GBRAIN_HOME`, ingestion seeds 1, 2, 3 (held-out and competing questions run once per seed: 90 runs each).

## Arms

1. **N9 hermetic, base and branch** (`bun eval/runner/n9-multi-hop-paraphrase.ts --corpus eval/data/world-v1-attendees`), with relational retrieval off and on over one index per seed. A small loader adds the held-out and competing files as two further one-hop splits; it reads only those files and maps each record to its meeting through `meeting_slug`, never by parsing text. The loader is written after the lexicon change is committed, by someone other than the lexicon author.
2. **N9 paid, branch only** (`--paid --budget-run-id`): hybrid search with OpenAI embeddings on the composed splits, report only. Cap **$2** for this item; the wave's program cap is $5. No cell is rerun to change a verdict.

## Metrics

Scored by `eval/runner/attendance-world-score.ts` (extended to the two new splits) from the receipts and the corpus:

- **Fire rate**: runs where attendance retrieval fired, over all runs of the split, errors in the denominator.
- **recall@5** of the listed attendees, base and branch, relational on.
- **False route (competing intent)**: a run where gbrain chose the attendance relation, or returned attendance evidence (a person returned because a meeting lists them). Measured on the chosen relation and the returned evidence, not on the answer.
- Stage funnel (parsed, meeting resolved, fired) as N9 reports it.

## Decision rule

Item 9 ships only when all of these hold on the branch, held-out first:

1. Held-out fire rate is at least **80%** of its 90 runs (24 of 30 questions on every seed).
2. Held-out recall@5 is not lower than base.
3. Competing intent has **zero** false routes across its 90 runs.
4. The template split is unchanged from base (fire rate and recall@5), and the relational paraphrase split has zero false attendance routes.

If any fails, item 9 is dropped from the wave and filed with the funnel (not parsed, not resolved, resolved but not fired). The development split's fire rate is reported beside the held-out one either way. Deterministic counts over fixed seeds; no statistics.

## Expectation stated before the run

The held-out author deliberately avoided the development frames, and the narrowed lexicon adds only five verb forms and one noun frame, so a held-out fire rate below 80% is a likely outcome. That outcome drops the item; it is not a reason to widen the lexicon inside this wave.
