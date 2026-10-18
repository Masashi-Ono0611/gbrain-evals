# gbrain-evals

[gbrain](https://github.com/garrytan/gbrain) is a memory system for AI agents. gbrain-evals is its public test
suite: the data, the comparison systems, the scoring code and every published result. Use it to see what gbrain
does well, check any claim against its saved records, or run the same tests on another system.

This page has three parts: [what gbrain does](#what-gbrain-does), [its current results](#current-results) and
[how it compares with other memory systems](#how-gbrain-compares). Everything above [Changelog](#changelog)
describes gbrain as this repository pins it today; the changelog at the bottom records how this page changed.

## The gbrain under test

| Item | Value |
|---|---|
| Pinned product | gbrain [`77cf8e111`](https://github.com/garrytan/gbrain/tree/77cf8e1116e9af67c1983adcbb3223b96f0991a5), release v0.60.169.0, declared as `gbrain` in `package.json` |
| Fixed-purpose aliases | `gbrain-cues` (`939232f`) and `gbrain-reader` (`e78f1c3`), used only by the experiments that name them |
| This repository | gbrain-evals v0.10.120 (`VERSION`) |

This repository installs gbrain v0.60.169.0 (`77cf8e111`). Some results below were measured at earlier commits; each
names its commit, and every commit named below is in the release's history except three: the Cat 40 Hard row's, which shipped after it
(v0.60.174.0), the wave 2 BEAM row's `71b6d85`, the head of gbrain #6445, which ships in gbrain v0.60.202.0 (#6445) with W5 on by default at factor 1.50 and the W1 `question` guidance deferred, and the Cat 40 next-wave row's `4e10136b4`, the Part 1 branch head measured for the confirmation (Part 1 ships without F5). The search modes have been identical since v0.48.4.0, so retrieval results from those commits describe
the installed modes.

## What gbrain does

gbrain keeps your notes, conversations and documents as Markdown files you own, and builds a database index over
them (Postgres or embedded PGLite). An agent such as Claude Code or Codex uses it through a CLI or an MCP server to
save, find, update and forget what it knows. The parts that matter for an agent:

- **Hybrid retrieval.** Every search combines word matching (for exact names and phrases), meaning-based vector
  search (for vague recollections and synonyms) and an optional reranker that rereads the candidates against the
  question. [How the pieces work together](docs/retrieval-lessons.md).
- **Relationships as evidence.** gbrain stores typed links between pages ("works at", "invested in", "attended") and
  follows them for questions like "who invested in Acme?", where the answer page may never mention the question's
  words.
- **Whole conversations for the reader.** Search ranks short passages, then hands the agent the whole conversation
  behind each hit, within a token budget, so a question that needs two old chats gets both.
- **Memory that stays correct.** An updated value replaces the old one everywhere and keeps it as history; `forget`
  removes a claim from every recall surface; private pages stay out of what agent callers can read.
- **Memory that says where it came from.** Everything an agent reads back is labelled by its source: your notes,
  something you told your agent, something an agent wrote, or outside content such as an email. A write gate flags
  instruction-like text, and a purge removes a claim from every store, with a record of what was removed.
  [What the labels change](docs/benchmarks/2026-10-08-memory-trust-results-paid.md).
- **Built to be run by an agent.** Every error and notice tells the agent what to do next and whether it must ask
  the user first, so agents do not spend money or repair data without consent.
- **A write path you can measure.** Agent sessions become readable memory pages, and timeline events are extracted
  from meetings and chats.

## Current results

| What we measure | Result | gbrain | Report |
|---|---|---|---|
| Finding every conversation a question needs (LongMemEval, strict `recall_all@5`) | **451 of 470 (95.96%)** | `109b992` | [Recount](docs/benchmarks/2026-10-04-longmemeval-opaque-followups.md) |
| Answer accuracy on LongMemEval, release retrieval, benchmark notes reader (`claude-sonnet-5-5`, official `gpt-4o` judge) | **468 of 500 (93.6%)** | `c5fb0201` | [Current pin](docs/benchmarks/2026-10-07-longmemeval-w10a-current-pin.md) |
| Best reader on the same retrieval (`claude-opus-5-5`, frozen 2026-09-29 retrieval) | **474 of 500 (94.8%)**, above Sonnet 4.6's 453 after Holm | `a7cb37b` retrieval | [Reader replay](docs/benchmarks/2026-10-07-longmemeval-w10b-reader-replay.md) |
| Whole-conversation delivery against bare chunks, sealed held-out set | **192 vs 132 of 200** (+60/−0) | `d44296c` | [Sealed decision](docs/benchmarks/2026-10-02-sealed-v2-decision-1.md) |
| Concept questions in different words, target ranked first (with reranker) | **130 of 181** | `d44296c` | [Matched comparison](docs/benchmarks/2026-10-02-concept-vector-rerank.md) |
| Relationship retrieval on reworded one-hop questions, recall at five | **0.411 → 0.537**, 19 better, 0 worse | `3a284ae` | [N9](docs/benchmarks/2026-10-01-n9-multi-hop.md) |
| Questions chaining two or three relations (multi-relation planner) | **24 better, 0 worse** held-out; +27 points strict all-hit@10 | v0.60.60.0 | [Held-out program](docs/benchmarks/2026-10-05-heldout-program.md) |
| Meeting attendance from a documented `## Attendees` list | **132 of 132** attendees stored, 0 false; "who attended" recall at five 32% → 80% | `c5fb0201` | [Attendance world](docs/benchmarks/2026-10-06-attendance-world.md) |
| Answers on 72 BEAM conversations, question-ranked facts plus pages at 8,000 tokens, against a memory-bank server at the same budget | **70.5 vs 66.5** points (+4.0, lower bound +2.6, ahead at the 3.5-point margin); 0.75× its cost per correct answer at 20 reads | `71b6d85` (gbrain #6445) | [Wave 2 results](docs/benchmarks/2026-10-13-memory-proof-wave-2-results.md) |
| A query that quotes a saved turn word for word (LongMemEval-S, 500 questions) | **500 of 500** return the conversation as a clean read (was 429; the rest lacked a rerank score or lost a search arm); strict recall@10 unchanged at 496 | `fecc7827` (#6391, merged as `f05943e65`) | [Verbatim probe](docs/benchmarks/2026-10-09-verbatim-probe-preregistration.md) |
| Vector search inside a 10% source or visibility scope, 1M to 2M chunks on Postgres | recall@50 **0.96 to 0.99** (was 0.52 to 0.77); a topic-coherent 10% source scope still reaches only 0.78 | `2e84d234e` (#6380) | [Scoped vector search](docs/benchmarks/2026-10-09-hnsw-scale.md) |
| Returning only the right facts (PrecisionMemBench, tight adaptive + reranker) | **0.586 precision**, 0.825 recall | `2efaaf8f` | [Refresh](docs/benchmarks/2026-09-09-retrieval-refresh.md) |
| Serving the new value after an update | **388 of 388** probes, never stale, on PGLite and Postgres through the CLI and MCP | `77cf8e111` | [N1](docs/benchmarks/2026-10-01-n1-knowledge-update.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md) |
| Nothing left behind after `forget` | **0** prohibited outputs, 6 of 6 reinstatements | `77cf8e111` | [N5](docs/benchmarks/2026-10-01-n5-forget-residue.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md) |
| Private pages reaching agent callers or remote callers | **0**, in process and on Postgres over real HTTP (155 of 155 cells, 5 kinds of caller); proactive recall gated in CI | `77cf8e111` | [N6 on Postgres](docs/benchmarks/2026-10-06-n6-postgres-http.md), [N8 gate](docs/benchmarks/2026-10-06-n8-privacy-gate.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md) |
| An attacker's false claim from an email or a relayed tool result, adopted in a later session (Opus 5.5, Sonnet 5.5, GPT-6.1 Sol) | **1.5% to 5%** of sessions with trust labels shown, 5.1% to 10.6% with them stripped; **0 of 360** instruction-worded injections followed per model; Cats 37 to 39 pass every keyless contract at the pin | `c2f10ee8` to `5b9c814b` (shipped as `d4dc2d4d8`); keyless at `77cf8e111` | [Memory trust](docs/benchmarks/2026-10-08-memory-trust-results-paid.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md) |
| Keeping speaker and time across chat export formats | **29 of 29** formats | `77cf8e111` | [N12](docs/benchmarks/2026-10-01-n12-format-fidelity.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md) |
| Finding contradicting notes | **146 of 150** conflicts with the default judge model (`claude-haiku-4-5`), 0 of 40 dated changes and 4 of 51 compatible pairs flagged; 149 at `48ed5e8` with the same prompt, the difference is sampling | `77cf8e111` | [N2](docs/benchmarks/2026-10-01-n2-contradiction-surfacing.md), [re-pin](docs/benchmarks/2026-10-11-wave14-repin.md#the-paid-n2-judge-arm) |
| Contradiction judge on current models | **150 of 150** conflicts and **0 of 251** compatible pairs flagged, for each of four current models (Opus 5.5 the top Anthropic one); cheapest passing model $0.21 per 1,000 pairs | `c5fb0201` | [N2 judges](docs/benchmarks/2026-10-06-n2-judges.md) |
| Attributing someone else's claim to the page holder (takes classifier) | **0 of 123** cases on Sonnet 5.5, GPT-6.1 Sol and Opus 5.5 (3 with Claude Haiku 4.5); the classifier is not yet graduated | `c5fb0201` | [Takes-bootstrap](docs/benchmarks/2026-10-06-takes-bootstrap-frontier.md) |
| Real agents (Claude Code, Codex) spending or destroying data without consent | **0** violations in 66 safety sessions; 96 of 102 tasks finished | v0.60.46.0 | [Cat 41](docs/benchmarks/2026-10-03-agent-operator.md) |
| Hard company questions answered by agents, against plain files with `grep` (Cat 40 Hard confirmation: two 50,000-document worlds, Opus 5.5, Sonnet 5.5, GPT-6.1 Sol, reranking verified in every gbrain slot) | gbrain ahead by **+7.7 points** (95% CI +2.7 to +12.7) on a fresh world and **+13.0** (+7.7 to +18.3) on a sealed one, for every model; behind on the fresh world's conflicting-source family (47 against 56 of 60) | `3e4ff61ce` (shipped as v0.60.174.0, `0df9f2ee7`) | [Cat 40 Hard confirmation](docs/benchmarks/2026-10-10-model-ladder-hard-confirmation.md) |
| Hard company questions after the Cat 40 next wave (four new 50,000-document worlds, two generators; Opus 5.5, Sonnet 5.5, GPT-6.1 Sol) | What ships, Part 1 without F5: gbrain ahead of plain files by **+10.67 points** (95% CI +7.00 to +14.50) on two sealed worlds. The pre-wave baseline is also ahead: **+8.50** (+4.83 to +12.33) on two public worlds and **+11.83** (+8.00 to +15.83) on the sealed ones. Against that baseline, the shipped configuration is level on sealed (−1.17, −4.33 to +2.00) and was level with control in development. The public build with F5 measured +12.50 (+9.17 to +15.83) against files and +4.00 against the baseline. That build is **not shipped (F5 failed its precision ship condition)**, and its gain came from F5 | `4e10136b4` (F5 off on sealed), baseline `09d21554d` | [Cat 40 next-wave confirmation](docs/benchmarks/2026-10-15-cat40-next-confirm/README.md) |
| Finance-only text reaching an agent's context in permission runs (Cat 40, five frontier models) | **0 of 100** (plain files 100, plain Postgres 97 with 4 leaked answers); the world's 95.6% success figure is retired ([why](docs/benchmarks/2026-10-02-model-ladder.md#retired-2026-10-12)) | `51f865d78` | [Cat 40](docs/benchmarks/2026-10-02-model-ladder.md) |
| Timeline events extracted from meetings and chats | **37 and 38 of 38**, 0.04 wrong per page | `b9ee931` | [`auto_chronicle`](docs/benchmarks/2026-10-04-auto-chronicle-rerun.md) |
| Managed Postgres catch-up 57 ms from the database (10,000-file backlog) | **367.9 pages/min** steady, **33.6 min** for the backlog (was 174.8 pages/min and 74.5 min on the same rig); a page save 2.5 s instead of 8.6 s | v0.60.111.0 (#6279) | [Lanes and foreground](docs/benchmarks/2026-10-07-managed-sync-lanes-foreground.md) |
| A managed Postgres catch-up when one write cannot finish preparing (15,000 entries, heavy fact adoption, 57 ms, transaction-mode pooler) | Drains in **2 passes (91 min, pool 10)** and 3 passes (pool 3), with **0** failed fence receipts and **0** watchdog stops; v0.60.105.0 never drained (102 pages in 47.6 min). A stuck write is held in **240 s**; a table lock still pins 9 of 10 connections | v0.60.112.0 (#6298; 15,000-entry runs at `846bea442`) | [Preparation stall](docs/benchmarks/2026-10-08-managed-sync-preparation-stall.md) |
| A managed Postgres sync behind a transaction-mode pooler whose round trip never completes | Wedges with **one process and no lanes** (backend `ClientRead`, consumer parked 135 s, zero commits) on v0.60.110.0 and on #6298's head; **0 wedges in 2 h 49 min** of the two-consumer shape (4,951 pages); fixed by the bounded settle in v0.60.114.0 | v0.60.110.0 → v0.60.117.0 | [ClientRead wedge](docs/benchmarks/2026-10-08-managed-sync-clientread-wedge.md) |
| Malformed facts/takes tables repaired by a model without a wrong cell (held-out set, model tier only) | **96.0%** repaired, **0** wrong cells (gpt-6.1-sol and claude-opus-5-5, the measured defaults); every other case held | v0.60.102.0 ([`5b58910`](https://github.com/garrytan/gbrain/commit/5b5891069)) | [Fence repair Tier 3](docs/benchmarks/2026-10-06-fence-repair-tier3.md) |
| A file whose frontmatter `slug:` names another page: duplicate to merge, stray line to delete, or a case for a person (model judgment) | **0** harmful answers in 432 pair runs (no duplicate split, no merge of two different things); true duplicates recognised **92.0%** (Opus 5.5), 85.3% (gpt-6.1-sol), 80.0% (Sonnet 5.5), the rest deferred to a person | gbrain #6377 (`ac6e0868`) | [Slug-conflict judgment](docs/benchmarks/2026-10-09-content-repair-judgment.md) |
| A forecasting take graded by a model, among verdicts confident enough to apply (≥ 0.95) | **0** wrong in 496 applied verdicts by gpt-6.1-sol (upper bound 0.6%, bar 1%), which resolved 99.2% of resolvable takes and held back on all 250 unresolvable ones; Opus 5.5 and Sonnet 5.5 rarely reach 0.95 (2 and 121 applied, Sonnet 1 wrong) | gbrain #6882 (`d99b84694`) | [Take grading](docs/benchmarks/2026-10-16-take-grading.md) |
| A forecast journal over synthetic holders of known skill (private, trusted local only) | Shrunk accuracy ranks holders in their true order, median Spearman ρ **0.905** (bar 0.80); who-was-right set-F1 **1.000**; every open, overdue and undated prediction counted exactly; **8/8** remote probes see none of it | gbrain #6886 (`65ed40ec6`), v0.60.286.0 | [Forecast journal](docs/benchmarks/2026-10-17-forecast-journal.md) |
| Graph walks (`traverseGraph`, `traversePathsDetailed`) on fictional graphs of 10,000 to 1,000,000 pages: Postgres with breadth-first walks against HydraDB as the walk engine | Postgres faster at every size, same answer on all 54,842 compared calls: warm p95 **1.44 s vs 6.28 s** at 100,000 pages and **3.45 s vs 6.28 s** at 1,000,000; HydraDB faster only on deep `both` walks (2.7x at depth 3); production HydraDB routing not built | gbrain #6934 (`fc1121cae58`) | [Graph backend](docs/benchmarks/2026-10-17-graph-backend.md) |
| Useful material kept when a session becomes a memory page | **88.1%** judged (judge calibration awaiting a person's review); 74.9% with quoted evidence | Cat 35 run | [Cat 35](docs/benchmarks/2026-08-16-brainbench-cat35-transcript-distill.md) |

All 29 reproductions in the [bug ledger](docs/benchmarks/2026-10-01-wave-bugs.md) pass at `77cf8e111`, including
N1-7's (fixed by gbrain #6265) and Cat7-1's, whose entry stays open under its stricter closure rule (see known limits).
The memory trust findings with keyless repros (37-1, 37-2 and 37-5 in the
[memory trust ledger](docs/benchmarks/2026-10-07-memory-trust-bugs.md)) pass too
([re-pin report](docs/benchmarks/2026-10-11-wave14-repin.md)). Rows marked `c5fb0201` were measured in the October
round at an earlier pin (the paid runs and the attendance world). The correctness rows come from keyless checks on
synthetic worlds with generated answer keys, rerun at every pin.

Settings that change these numbers are in [settings by workload](docs/settings.md). Two matter most: keep autocut off
for questions that need several conversations (451 against 384 of 470), and leave query expansion off, since it adds
a model call without a measured gain.

## How gbrain compares

Other systems publish different metrics on different protocols, so these comparisons use only numbers we can put on
the same footing, and say so where we cannot. This page describes the other systems by kind; their names, versions,
sources and every row we could not match are in [comparisons and their protocols](docs/comparison-systems.md).

**Finding all the evidence: gbrain leads every system we can score strictly.** A question counts only if every
required session is in the top five.

| System | Strict `recall_all@5` on LongMemEval | Source |
|---|---|---|
| **gbrain**, `balanced` with Voyage reranker | **95.96% (451/470)** | our run, opaque session ids |
| gbrain, same without the reranker | 92.34% (434/470) | our run, opaque session ids |
| A verbatim-session memory system, hybrid search + LLM rerank | 90.0% (423/470) | our strict recount of its saved rankings |
| A token-native retrieval system + embedding fusion | 87.45% (411/470) | self-reported, its own harness |
| The same verbatim-session system, raw vector search | 85.7% (403/470) | our strict recount of its saved rankings |

Many headline LongMemEval "R@5" scores of 95% to 100% count a question as found when any one required session
appears; on that looser metric gbrain finds at least one for 470 of 470. Limits: gbrain returns five chunks while
the verbatim-session system returns five whole sessions, the configuration was chosen on these 470 questions, and embedders and
chunking differ, so this compares pipelines, not components.

**Retrieval or the whole history: within 7 points at a seventh of the recurring cost.** On 150 LongMemEval-S questions with the same reader, gbrain's retrieval answered 139 against 144 with the whole ~115,000-token history pasted in (Sonnet 5.5), and 137 against 141 (GPT-6.1 Sol). Both stay within the preregistered 7-point margin, which is not the same as equal: the gap is in questions that need several conversations. gbrain's recurring cost per question is $0.024 against $0.173 with Sonnet 5.5, plus a one-time $0.015 to index each history. [Full-context comparison](docs/benchmarks/2026-10-07-longmemeval-w10c-full-context.md).

**Answer accuracy: close to the published systems that use the same reader.** With `gpt-5.4` as the reader,
gbrain's retrieval answers 89.4%; a temporal knowledge-graph service publishes 90.2% and a database-backed memory
system 84.97% with the same reader model. Judges,
prompts and retrieval budgets differ, so this is context, not a ranking. Published results across systems range from
81.6% to 96.1%.

**A memory-bank server on sealed BEAM: gbrain ahead by 2.6 points, cheaper only at low read volume.** In a matched,
preregistered test with the same reader, judge and context budget on sealed BEAM conversations (1,080 questions at
100k, 500k and 1M tokens), gbrain's pages plus extracted facts answered 67.0% against 64.4% for a memory-bank server
with background extraction and reflection (+2.64 points, one-sided 95% bounds +0.90 and +4.41). Its cost per correct
answer was 0.63 of the server's at 20 reads per stored conversation and level at 200. The server keeps an edge on
event ordering and temporal reasoning, and on LongMemEval-S (84.5% against 80.3% for gbrain's pages alone). gbrain
ran its freeze build `d7467d1cf`, whose retrieval was checked equivalent at `d7d7686de`; both are in the pin's
history. [Sealed results](docs/benchmarks/2026-10-09-memory-proof-wave-sealed-results.md).

**Returning only what matters: gbrain's tight mode is more precise than every memory product in the
PrecisionMemBench table except the benchmark author's own belief store.** Its mean precision is 0.586, against 0.22,
0.09 and 0.06 for three hosted memory products listed upstream; the author's belief store scores 1.00. Upstream rows may use different
denominators and machines.

**Memory over long conversations: ahead of a memory-bank server on BEAM, behind its earlier answers on LongMemEval-S.**
On 72 BEAM conversations (1,440 questions), gbrain's question-ranked facts-plus-pages lane scores 70.5 against 66.5 for
a memory-bank server with background extraction, both at 8,000 tokens of context and judged jointly and blind. The gap is
+4.0 points, with a lower bound of +2.6. gbrain costs 0.75 times as much per correct answer at 20 reads per stored
conversation. On LongMemEval-S, gbrain trails that server's earlier answers by 3.25 points, but those answers were
scored on more context than the budget (p95 9,373 tokens), so the row decides nothing.
[Wave 2 results](docs/benchmarks/2026-10-13-memory-proof-wave-2-results.md).

**Concept search: level with a vector store, when both are reranked.** gbrain 130 of 181, vectors with the same
reranker 128.

**Agent tasks: ahead of plain files on hard company questions, and safer with restricted data.** In Cat 40 Hard's
preregistered confirmation (two 50,000-document worlds, a 16-turn cap, Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol, with
reranking verified in every gbrain slot), agents using gbrain answered more questions correctly than the same agents
with plain Markdown files and `grep`: +7.7 points (95% CI +2.7 to +12.7) on a fresh world and +13.0 (+7.7 to +18.3)
on a sealed one, for every model. gbrain trails files on the fresh world's conflicting-source family and gives more
confidently wrong answers. On the earlier, easier Cat 40 world, gbrain puts finance-only text into the agent's context
in 0 of 100 permission runs; files do in 100, and plain Postgres in 97 (with 4 leaked answers). That world's success
figures are retired: gbrain ran without its reranker in those cells and the world sits at its ceiling, so the frontier
tie (95.6% each) and the older six-model lead no longer describe gbrain
([why](docs/benchmarks/2026-10-02-model-ladder.md#retired-2026-10-12)).

## Known limits

- At the pin, a timeline read on a 1,000-page brain takes about 0.075 ms against 0.045 ms before the Foundations 1
  release (ledger entry Cat7-1, open; 0.075 and 0.078 ms on the two hosts measured at `77cf8e111`).
- At the pin, `auto_chronicle` (on by default) writes planned follow-ups as events on their future dates; turn it
  off there, or use v0.60.49.0 or later.
- Open loops cover Gmail only, and a commitment fulfilled by reply does not close.
- There is no corpus-wide contradiction scanner; the judge compares notes that search returns together.
- Associative recall, which gbrain does not claim, scores 0 of 240.
- Several retrieval settings were chosen on the same LongMemEval questions they are scored on; held-out
  confirmation exists for evidence delivery, not yet for the retrieval configuration.

## Where to read next

| Question | Where to start |
|---|---|
| When do words, vectors or relationships find the right answer? | [Retrieval lessons](docs/retrieval-lessons.md) |
| Which configuration should I try? | [Settings by workload](docs/settings.md) |
| Every report, grouped by the question it answers | [Documentation index](docs/README.md) |
| How do retrieval scores differ from answer accuracy? | [What the scores mean](docs/retrieval-lessons.md#what-the-scores-mean) |
| How are new gbrain defaults decided? | [Held-out program](docs/benchmarks/2026-10-05-heldout-program.md), [decision kit](docs/decisions.md) |
| Can I reproduce a result or test my own system? | [Run the suite](eval/README.md), [contribute an adapter or a category](eval/CONTRIBUTING.md) |
| What is still unfinished? | [Open work](TODOS.md) |

## Try a small experiment

Install [Bun](https://bun.sh/) and clone this repository:

```sh
git clone https://github.com/garrytan/gbrain-evals.git
cd gbrain-evals
bun install --frozen-lockfile

# No provider calls: rank the committed documents by matching words.
BRAINBENCH_N=1 bun eval/runner/multi-adapter.ts --adapter grep-only

# Check the committed corpus and question files.
bun eval/runner/validate-data.ts
bun run eval:query:validate
```

To compare all four retrieval adapters, set `OPENAI_API_KEY` in your environment:

```sh
BRAINBENCH_N=1 bun eval/runner/multi-adapter.ts --queries all
```

The run writes a scorecard and individual rankings to `eval/reports/multi-adapter/receipt.json`, using the fictional
corpus already in the repository. Vector and hybrid adapters make paid embedding calls; this runner does not ship a
warm embedding cache.

To run gbrain on the public agent-memory benchmark harness (LongMemEval-S, LoCoMo10, PersonaMem, LifeBench, BEAM and
PrecisionMemBench) under an audited protocol, follow the [harness quickstart](docs/benchmarks/harness-quickstart.md). Its
first step is a keyless plumbing check through the real gbrain adapter.

The agent benchmarks run like this:

**Cat 40 Hard** asks the same agents harder questions about a larger, messier
company: sets and counts over 10 to 40 accounts, values that changed several
times with backdated corrections, customers with look-alike names, documents
that disagree by authority, and facts that must survive five conversations.
It is tuned on plain files until frontier models finish about half, then
measured on a held-out world at about 4,000 and about 50,000 documents.
[Operator guide](docs/benchmarks/cat40-hard/RUNBOOK.md),
[world and scoring contract](docs/benchmarks/cat40-hard/WORLD_SCHEMA.md).

```sh
# Cat 41: a candidate gbrain commit, its gate, and the Cat 40 instruction check
# (Docker, ANTHROPIC_API_KEY, OPENAI_API_KEY; about $80 for both)
eval/runner/cat41/after-pass.sh <gbrain checkout> <commit>

# Cat 40 v1 without spending: the scripted, hermetic arms
bun eval/runner/cat40-model-ladder.ts --scripted --arms fs,memory,oracle --out $(mktemp -d)

# Cat 40 Hard without spending: every family through the scripted arms, plus the freeze-rule table
scripts/cat40-hard.sh hello
```

For the full pinned configuration matrix, prerequisites, output paths and spending controls, follow the
[refresh report](docs/benchmarks/2026-09-09-retrieval-refresh.md). To evaluate your own application, choose
representative questions and their relevant documents before comparing systems; the
[contributor guide](eval/CONTRIBUTING.md) explains the question and adapter formats.

## Corrections

These published numbers are invalid or overstated. Each affected report keeps its original figures, labeled,
beside a dated correction (audit of September 28, 2026, plus later follow-ups):

- **LongMemEval answer accuracy 433/500 (86.6%) is invalid:** the answer model saw `answer_` session ids that mark
  the evidence. With the leak removed, the same configuration scores 432/500 (+15/−16 paired), so the leak made no
  measurable difference, but 433 stays invalid. Retrieval numbers recounted with opaque ids are confirmed.
  [Report](docs/benchmarks/2026-09-29-longmemeval-opaque-qa.md),
  [recount](docs/benchmarks/2026-10-04-longmemeval-opaque-followups.md).
- **The reading-notes gain 308/361 to 324/361** was measured with the same leak; with opaque ids it is 304/361 to
  320/361 (+25/−9). [Report](docs/benchmarks/2026-09-25-reading-notes.md).
- **Query expansion "hurts retrieval"** described the September 6 code (255/470); at current gbrain it scores
  436/470 against 434/470 without it, so that finding no longer describes gbrain.
- **The May calibration result (75% wins) is invalid:** the judge saw the expected behavior and knew which answer
  was which. [Report](docs/benchmarks/2026-05-18-brainbench-cat14-cat15-calibration.md).
- **The April relationship precision at five (39.2% to 44.7%)** used a lenient denominator; divided by five slots it
  is 29.9% to 35.4%. Its alias recall falls from 31.0% to 13.75%, and with attendance edges pointed the right way
  link type accuracy is 74.7% (109/146).
  [Report](docs/benchmarks/2026-04-18-brainbench-v1.md),
  [September 29 re-run](docs/benchmarks/2026-09-29-repin-cats-1-2-6.md).
- **The April and May relationship tables' `gbrain` row (49.1% precision)** came from a regular-expression parser of
  the four question templates, now named `graph-oracle-parse`; it is not a product score.
  [Report](docs/benchmarks/2026-04-19-brainbench-multi-adapter.md).
- **Cat 35's 88.1%** is judge-only; evidence-verified retention is 74.9%.
  [Report](docs/benchmarks/2026-08-16-brainbench-cat35-transcript-distill.md).
- **Cat 40 agent-task results from October 2 to 7 measured gbrain without its reranker.** Restored harness slots
  kept a closed metering-proxy port for Voyage, so every rerank request failed and gbrain returned unreranked results.
  That covers the frontier tie with plain files (0 of 500 gbrain cells reranked), the six-model cost-wave set, the
  entity-recall rounds, the fix-wave development ladders, the 52,000-document tier, most of the release ladder, the
  F1/F10 instruction A/B in the Cat 41 report, the registration-surface cell, the P8 surface development runs and the
  fix wave 11 and 12 smokes. Comparisons between gbrain builds that shared the condition stay internally valid. The
  F1/F10 same-window pair for `b3f4e8b` reranked on one side only and does not support its conclusion as stated. The
  fix wave's held-out check reranked (1691 of 1800 cells) and is unaffected. Fixed in gbrain-evals #76 and #109.
  [Cat 40 correction](docs/benchmarks/2026-10-02-model-ladder.md#correction-2026-10-09),
  [Cat 41 correction](docs/benchmarks/2026-10-03-agent-operator.md#correction-2026-10-09),
  [audit](docs/benchmarks/2026-10-08-program-primary-hard/root-cause/restore-audit.json).
- **The May snapshot's Category 18b to 29 rows** came from runners written before the August audit; Cat 29's +4.00
  synthesis lift also scored the same single-answer call twice.
  [Report](docs/benchmarks/2026-05-23-v0.40.6.0-snapshot.md).

## Inspect or extend the work

- `eval/data/` contains public fixtures and answer keys. The adapter boundary strips answer-key fields before passing
  content to the system being tested.
- `eval/runner/` contains runners and the shared scoring functions; `eval/registry.ts` lists every category with its
  gate rules.
- `eval/reports/` holds temporary output. Published records live beside their reports in `docs/benchmarks/`.
- `test/eval/` contains tests for the harness; `.github/workflows/ci.yml` runs the checks that do not need provider
  credentials.

External adapters and independently written questions are welcome. The
[August audit](docs/audit/2026-08-31-eval-audit.md) explains earlier scoring and harness errors. The
[receipt manifest](docs/receipts-manifest.json) maps published claims to saved records and records missing evidence
explicitly. [CHANGELOG.md](CHANGELOG.md) records each release of this repository.

Code is MIT licensed. Dataset and vendored benchmark attribution is recorded in [the credits](eval/CREDITS.md) and
[PrecisionMemBench attribution](eval/precisionmembench/ATTRIBUTION.md).

## Changelog

### 2026-10-18: Graph backend row (HydraDB vs Postgres)

Current results gains a graph-walk row from the [graph backend benchmark](docs/benchmarks/2026-10-17-graph-backend.md)
(GBRA-123, preregistered): gbrain's breadth-first walks on Postgres (#6934, `fc1121cae58`) answer faster than HydraDB
at 10,000, 100,000 and 1,000,000 pages with identical answers, so production HydraDB routing is not built. No existing
number changed. The repository version is stamped when this change merges.

### 2026-10-17: W11 sealed-confirmation preregistration for gbrain W4; repository row names v0.10.120

gbrain-evals v0.10.120 preregisters W11, the sealed confirmation of gbrain W4's weekly belief diff on a fresh seed and
fresh wording minted in custody, with a $0 harness that ports W4's own probe. The repository row names v0.10.120 (was
v0.10.119).

### 2026-10-17: Living pages decided on prior; repository row names v0.10.119

gbrain-evals v0.10.119 records the living-pages verdict for gbrain W9: with no owner data, W9 is not built in V1 and W10
is dropped with it, because the build threshold (1,387 reads per changed page-day) is far above any known personal-brain
read rate. The repository row names v0.10.119 (was v0.10.118).

### 2026-10-17: Living-pages preregistration; repository row names v0.10.118

gbrain-evals v0.10.118 preregisters the living-pages build decision for gbrain W9: a refreshed page beats anchored
retrieval only above about 1,387 reads per change once review time is priced, and the owner's ratio is read from two
aggregate queries. The repository row names v0.10.118 (was v0.10.117).

### 2026-10-17: Forecast-journal row; repository row names v0.10.117

gbrain-evals v0.10.117 mirrors the $0 forecast-journal gate for gbrain #6886 (wave 4b W7, shipped in v0.60.286.0): on
synthetic holders of known skill the journal ranks them in their true order (median ρ 0.905), counts every open
prediction exactly, and stays invisible to remote callers. New row after the take-grading row. The repository row names
v0.10.117 (was v0.10.116).

### 2026-10-17: P1 E2 rerun on gbrain W5; repository row names v0.10.116

gbrain-evals v0.10.116 records the custodian's P1 E2 rerun on gbrain v0.60.273.0 (W5): every late closure is disclosed
as an upper bound, and Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol keep `apply` (0 wrong and 0 undated closures, as-of
exact 0.392 to 0.397). The repository row names v0.10.116 (was v0.10.115).

### 2026-10-17: Take grading shipped in gbrain v0.60.282.0; repository row names v0.10.115

gbrain #6882 merged as `4e698e9d9` (v0.60.282.0), so gpt-6.1-sol is gbrain's measured take-grading judge for prompt
`hybrid-evidence-v2`; the take-grading report and its `verdict.json` name the release. The report also records the
auto-resolve follow-ups decided on October 16. The repository row names v0.10.115 (was v0.10.114).

### 2026-10-17: Take-grading row; repository row names v0.10.114

gbrain-evals v0.10.114 records the take-grading eval for gbrain #6882 (wave 4b W6, `d99b84694`): among the verdicts the
auto-resolve rule would apply, gpt-6.1-sol applied 496 with none wrong (one-sided 95% upper bound 0.6%, under the
preregistered 1%), so it is gbrain's measured take-grading judge; Opus 5.5 and Sonnet 5.5 do not qualify. New row
after the slug-conflict row. The repository row names v0.10.114 (was v0.10.113).

### 2026-10-16: Repository row names v0.10.113

gbrain-evals v0.10.113 records N6 on gbrain's weekly belief diff (`delta {beliefs: true}`) at the v0.60.273.0 release
(`6c3e6fe0`, #6866): 0 leaks and 0 oracles in process and over Postgres HTTP, with real-history signal on both
(measured through `--gbrain`; the pin is unchanged), and adds the P1 E2 rerun preregistration for gbrain W5. No result
row on this page changes. The repository row names v0.10.113 (was v0.10.112).

### 2026-10-16: Repository row names v0.10.112

gbrain-evals v0.10.112 records N6 on gbrain's recorded-time reads (`known_as_of`) at the v0.60.267.0 release (`933a7677`,
#6850): 0 leaks and 0 oracles in process and over Postgres HTTP, with real-history signal on both (measured through
`--gbrain`; the pin is unchanged). No result row on this page changes. The repository row names v0.10.112 (was v0.10.111).

### 2026-10-16: Repository row names v0.10.111

gbrain-evals v0.10.111 records N1 with gbrain's belief ledger on, at the v0.60.265.0 release (`09943580e`, #6806):
388 of 388 current values and 0 stale with the ledger off and on (measured through `--gbrain`; the pin is unchanged). No
result row on this page changes. The repository row names v0.10.111 (was v0.10.110).

### 2026-10-16: Repository row names v0.10.110

gbrain-evals v0.10.110 records the LHF wave 2 plan, its reviews and measured verdicts (gbrain v0.60.259.0, #6822), and
the preregistered attendance paraphrase gate, which failed (measured through `--gbrain`; the pin is unchanged). No
result row on this page changes. The repository row names v0.10.110 (was v0.10.109).

### 2026-10-15: Repository row names v0.10.109

gbrain-evals v0.10.109 records an exploratory N14 run of segmented page storage (large pages Wave B PR 1, gbrain
v0.60.252.0, measured through `--gbrain`; the pin is unchanged). No result row on this page changes. The repository row
names v0.10.109 (was v0.10.108).

### 2026-10-15: Repository row names v0.10.108

gbrain-evals v0.10.108 records the D9 check of remote `find_contradictions` on gbrain v0.60.250.0: N6 now seeds a
stored contradiction report and finds 0 leaks, and N2's compatible-pair rule still holds, so its wave 14 number carries
forward. No result row on this page changes. The repository row names v0.10.108 (was v0.10.107).

### 2026-10-15: Repository row names v0.10.107

gbrain-evals v0.10.107 records the D7 Cat 41 brief scenarios. In 48 native Claude Code and Codex sessions on gbrain
v0.60.247.0, the pushed brief cut time to the first correct output by 6% against a preregistered 20%. So it shows no
time-saved signal, and the brief stays off by default; this is development evidence only. No result row on this page
changes. The repository row names v0.10.107 (was v0.10.106).

### 2026-10-15: Repository row names v0.10.106

gbrain-evals v0.10.106 records the D6 proactive-brief development v2 run. On the T0 carrier with gbrain v0.60.247.0,
with session-1 facts aged or crowded out of hot memory, the brief cut session-2 tool calls by 6% against a
preregistered 20%, so it shows no time-saved signal; success held at 72 of 72 in both arms. This is development
evidence only. No result row on this page changes. The repository row names v0.10.106 (was v0.10.105).

### 2026-10-15: Cat 40 next-wave confirmation; repository row names v0.10.105

gbrain-evals v0.10.105 adds the Cat 40 next-wave development record, preregistration and confirmation. A new row under
Current results reports what ships: Part 1 without F5 ahead of plain files by +10.67 points on two sealed worlds, the
pre-wave baseline ahead on both generators, and the public build with F5 marked not shipped because F5 failed its
precision ship condition. The repository row names v0.10.105 (was v0.10.104).

### 2026-10-15: Repository row names v0.10.104

gbrain-evals v0.10.104 adds the N14 large-page fidelity rerun after large pages Wave A (gbrain `44eb049`, measured
through `--gbrain`; the pin is unchanged). No result row on this page changes. The repository row names v0.10.104 (was
v0.10.103).

### 2026-10-14: Repository row names v0.10.103

gbrain-evals v0.10.103 records the D6 proactive-brief development run. On the T0 carrier with gbrain v0.60.240.0,
brief-on and brief-off both finished 70 of 72 paired tasks, so it shows no improvement signal; this is development
evidence only. No result row on this page changes. The repository row names v0.10.103 (was v0.10.102).

### 2026-10-14: Repository row names v0.10.102

gbrain-evals v0.10.102 records the D5 brief re-smoke on gbrain #6703, which passes, and makes the Cat 40 runner scrub