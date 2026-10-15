# Preregistration: N14 large-page fidelity (2026-10-14)

Frozen in the same commit as the N14 registry row (`large-page-fidelity`), the runner and the generator, before any counted run. A later change to a rule, threshold, model list or arm is written into the Amendments section below before the run it affects.

## Question

If I put one very large document in gbrain, can an agent find and read what's deep inside it, and does keeping it up to date stay cheap?

The motivating case is a real one: a 1.79 MB iMessage conversation that gbrain stores but never finds. The large-pages plan (gbrain, approved 2026-10-14, autoplan run `run-20261014163234`) replaces whole-page handling with segmented storage in three waves. N14 is that plan's measuring stick. Its baseline runs against current gbrain master before Wave A merges, so every wave reports a before and an after on the same documents and questions.

## Evidence class

Synthetic production path. The documents are generated with known answers; every arm goes through gbrain's own operation handlers on PGLite. Hermetic results use keyword search only and a counting fake embedder, so they prove findability, read shape, append cost and storage fidelity, not semantic search quality. The paid arm adds real embeddings and reader models.

## Build and data

- Generator: `eval/generators/n14-large-page-gen.ts`, version `n14-large-page-gen/v1`, seed 14.
- Tiers. `2mb` (the CI tier): a 2.0 MB group chat, a 2.0 MB project log and a 1.5 MB novel. `20mb`: the chat at 20 MB. `200mb`: the chat at 200 MB. `1gb`: the chat at 1 GB, listed for manual runs only.
- Shapes. The chat uses the imessage-slack line shape `**Name** (YYYY-MM-DD h:mm AM): text` under `## YYYY-MM-DD` day headers, with four fictional participants and some non-ASCII text (accents, emoji, CJK). The log has one `## YYYY-MM-DD` entry per day with `### Standup` and `### Notes` bullets. The novel has `## Chapter N: Title` sections of prose. Every name and place is invented.
- Needles. Four per decile of the document's bytes: a number, a date, a person's surname and a colour, each in a sentence "the <Anchor> <noun> is <answer>" where the anchor is an invented place name used nowhere else. Every needle has a distractor five deciles away: the same sentence with one detail changed (the place name, which carries its own value).
- Append. Every document has a fixed 1 KB append: a new day or chapter holding one more needle.
- Control page. Every brain also holds a small page (`notes/n14-control`) with one needle per type.
- Oracle. `checkPresence` rescans the raw bytes: each needle, distractor, append and control answer occurs exactly once as a whole token, at its ledger offset, in its decile and section; each anchor occurs once. A failure makes the run an error.

gbrain under test: the pinned dependency (`77cf8e111`, v0.60.169.0) by default; the baseline is master `c71fe7436e673db819c1be4532504b861e14ad50` (v0.60.225.0) through `--gbrain`.

## Capability and entrypoints at the tested commits

Checked at master `c71fe74` (line numbers) and at the pin `77cf8e1` (same behaviour; lines differ by a few).

- Write: `put_page` (`src/core/ops/pages.ts:301`), trusted local caller. A body over `content_sanity.bytes_block` lands with `frontmatter.embed_skip` and zero chunks (`DEFAULT_BYTES_BLOCK = 500_000`, `src/core/content-sanity.ts:66`). Markdown over `MAX_FILE_SIZE = 5_000_000` (`src/core/import-screen.ts:39`) is refused with `Content too large` (`src/core/markdown.ts:480`), surfaced by put_page as `request_too_large`.
- Search: the `search` operation (`src/core/ops/search.ts:666`), keyword only without a provider key. Results carry `chunk_id`; at most two chunks per page survive dedup (`MAX_PER_PAGE = 2`, `src/core/search/dedup.ts:25`); conversation hits deliver an evidence window up to `EVIDENCE_BLOCK_CHAR_CAP = 60_000` characters (`src/core/search/evidence-delivery.ts:60`).
- Read: `get_page` (`src/core/ops/pages.ts:84`) takes `slug`, `fuzzy`, `include_content`, `content_only` and a few flags. There is no `body` mode, window, cursor or response budget.
- Append: no `append_page` operation; an append rewrites the page with `put_page` and `expected_revision`.
- Embedding: `runEmbedCore({ stale: true })` (`src/commands/embed.ts:440`) embeds chunks without a vector through the gateway; a fresh brain is configured for `voyage:voyage-4` at 1024 dimensions.
- Export: `runExport` (`src/commands/export.ts:26`) with `--slug-prefix`; a page payload over 32 MiB aborts the export (`EXPORT_PAYLOAD_LIMIT`, `src/core/export-stage.ts:7`). The body is stored trimmed (`compiled_truth.trim()`, `src/core/markdown.ts:425`) and serialized between a blank line and one newline (`src/core/markdown.ts:961`); the round trip applies that documented framing to the source and compares the rest byte for byte.

Not implemented at either commit, recorded as gaps rather than failures: windowed reads, append_page, upload sessions, any large-page size class. The native arm therefore reports "capability absent".

## Arms

Same documents, same questions, one fresh brain per (document, arm), each in its own child process under an RSS watchdog (6 GiB ceiling).

1. **single-page**: gbrain as it is. The whole document is one `put_page`; a search hit is read with a default `get_page {slug}`; the append rewrites the page.
2. **managed-parts**: the best split design available today, the one the conversation-archive skill and `imessage-daily` pages use. A hub page holds the preamble and a wikilink index; each `## ` section (a day or a chapter) is its own page (`imessage-daily` for the chat, `note` otherwise). A hit is read with `get_page {slug}` of its part. The append writes one new part and updates the hub.
3. **native**: the same gbrain through its large-page API. It runs when a probe of the operation registry finds `get_page` declaring a `body` parameter with a window mode; it then reads hits with `get_page {slug, body: 'window', around_chunk_id}`, appends with `append_page` when that operation exists, and writes documents over 4 MiB through an upload session when one exists. Otherwise the arm is reported as "capability absent".

## Metrics and denominators

Hermetic, per (tier, document, arm):

- Ingest outcome: stored, refused (with the gbrain code) or error; pages, chunks, `embed_skip`.
- Keyword needle recall@10 by decile: the share of the decile's needles (4 per document) whose answer appears, as a whole token, in the stored chunk (`content_chunks.chunk_text` by `chunk_id`) of one of the top 10 `search` results; a passage over 64 KiB never counts. Overall recall pools the 40 needles.
- Delivered recall: the same test on the text the result row delivers to the agent.
- Read correctness: a read made for a hit returns text holding the needle and its frame is at most 1 MiB.
- Largest response frame: the byte length of the JSON-RPC text frame that would carry each operation result over MCP; responses over the 1 MiB egress cap are counted.
- Append cost: embedding inputs and estimated tokens (UTF-8 bytes / 4) that `runEmbedCore({stale: true})` sends after the 1 KB append, counted by a fake embed transport, divided by the appended tokens (same estimate); chunk rows rewritten and deleted. Undefined (null) when the page has no chunks after the append.
- Round trip: export, reassemble (managed parts: hub preamble plus parts in key order, joined by one blank line), compare sha256 with the source body plus the append.
- Ingest wall time, peak RSS and RSS over the post-schema baseline, measured inside the arm's own process.

Paid (not run in the baseline): hybrid (`query`, expansion off) and vector-only (`searchVector` on the query embedding) recall@10 by decile with real `voyage:voyage-4` embeddings at 1024 dimensions; reader QA on the deep needles (deciles 5 to 9) where each model answers from the top 5 hybrid results (2,000 characters each), scored by exact answer token, with the distractor's value counted as a confusion.

## Decision rule

Safety contracts, gating at once (registry `data.safety.*`):

1. Zero crashes or OOM kills at every size run up to 200 MB (`crashes == 0`).
2. Zero response frames over the 1 MiB egress cap (`responses_over_cap == 0`).
3. Zero byte loss on the export round trip for any stored document (`roundtrip_byte_loss == 0`).
4. Presence assertions pass, including every brain finding its control page (`presence_failures == 0`).

Utility floor: native keyword needle recall@10 at the 2 MB tier is at least 0.90 (`data.floor.native_keyword_recall_2mb >= 0.9`). A refuse-everything or skip-large-pages system scores 0 and fails.

Quality thresholds (hermetic receipt):

- Embedding inputs for a 1 KB append are at most 3x the appended tokens on the native arm, worst document (`data.quality.native_append_embed_ratio_max <= 3`).
- Native recall is not worse than the managed-parts arm by more than 2 points on any document and tier (`data.quality.native_recall_gap_points_max <= 2`).

Quality threshold (paid receipt, `data.paid.gates`): hybrid needle recall@10 is at least 0.95 at every decile for the 2 MB and 20 MB tiers, on the managed-parts and native arms.

Exploratory, never gating: ingest time and RSS curves by size, embedding tokens per MB (cost per MB at the provider's price), 200 MB recall, delivered recall, distractor preference, append cost and chunk rewrites on the comparator arms.

Held: the rules are evaluated and reported but do not gate while the native capability is absent at the pinned gbrain. The hold is removed in the commit that re-pins gbrain to a build with the capability; no rule value changes with it.

## Models (paid arm)

`bun scripts/model-freshness.ts` on 2026-10-14 reported the newest models: `claude-opus-5-5`, `claude-sonnet-5-5`, `gpt-6.1-sol` (and `claude-fable-5-1`). The counted readers are `anthropic:claude-opus-5-5`, `anthropic:claude-sonnet-5-5` and `openai:gpt-6.1-sol`. Fable runs only in a smoke test, never in a counted cell. No older generations, no gpt-5.4-mini. Embeddings: `voyage:voyage-4`, 1024 dimensions (gbrain's default for a fresh brain).

## What each outcome changes

- Baseline (master, before Wave A): expected to show the single-page arm stored but unsearchable at 2 MB and refused at 20 MB, an over-cap frame on a default read, and managed parts as the working comparator. These are recorded as scored misses and gbrain feature gaps, not as harness errors.
- After each wave: the same command with `--gbrain <checkout>@<wave head>`. The native arm turns on when the capability probe finds it, and the rules decide whether the wave delivered.
- A safety failure on any arm blocks a promotion of the category to gating even when quality passes.

## Budget

Hermetic: $0, no provider call. Measured 2 MB tier run time under 60 seconds on a 4-core machine is the CI target. Paid: estimated $8 for the 2 MB and 20 MB tiers (embeddings about $0.5; reader QA about 480 short calls), run only with `--paid --budget-run-id <id> --preregistration <this file>` under the wave budget ledger.

## Disclosure

The counting embedder returns hash vectors: it measures how many inputs gbrain sends, never retrieval quality. The hermetic arm does not exercise vector search, Postgres, transports other than in-process operations, sync from a repository or the git layout. The managed-parts arm is a harness implementation of the documented split design, not a gbrain feature; its splitting code is part of this repository.

## Amendments

### Amendment 1 (2026-10-15): Wave A rerun

This amendment was written before any run against gbrain `44eb0493bfd5…` (master, v0.60.242.0). That commit contains large pages Wave A: #6707 (the windowed read contract), #6715 (crash fixes) and #6733 (the 24 MiB ceiling, large-page embedding and `gbrain reindex --oversized`). No rule, threshold, model or arm definition changes.

1. **Scope.** The hermetic arm runs at 2 MB and 20 MB with all three arms. The paid arm does not run, because no budget is approved. The 200 MB chat runs on the single-page and native arms only, to check the refusal over the 24 MiB ceiling (bug N14-4). Managed parts is not rerun at 200 MB.
2. **Native arm.** The capability probe is expected to find `get_page` declaring `body` with a `window` mode and `around_chunk_id` (#6707), and no `append_page` or upload session. As preregistered, the native arm then writes each document with one `put_page`, reads hits with `get_page {slug, body: 'window', around_chunk_id}` and appends with a whole-page `put_page` rewrite.
3. **Upgrade-path case (exploratory, not gating).** For each 2 MB document, the baseline gbrain `c71fe74` seeds a file-backed PGLite brain with the document as a single page, which it stores with `embed_skip: oversized` and no chunks, plus the control page. The gbrain under test then opens the brain, which runs its migrations, and runs `runOversizedBackfill` (the code behind `gbrain reindex --oversized`).
   - Reported: the backfill receipt (candidates, reindexed, held for approval, remaining, failed), whether the marker was removed, and the chunk count.
   - The native arm's probes then run on the upgraded page: keyword recall@10 by decile, windowed-read correctness, largest response, round-trip sha256 and the append.
   - There is no embed pass: the backfill holds pages over 1 MiB for approval, and the hermetic arm spends nothing.
   - Expected: recall equal to the native arm on a fresh brain.
4. **Agent-facing default read (exploratory).** At Wave A, what a default `get_page` returns depends on the caller. A trusted local read stays full. An agent-facing read gets `auto`, which above 256 KB is an outline plus the first window. This harness calls as a trusted local caller, so its default read of a single page returns the whole page. The runner also makes the entry page's default read with `remote: true` and reports that response size beside the trusted one, outside the egress count. The egress safety contract is unchanged: it counts every response of the trusted-local harness, the default read included.
