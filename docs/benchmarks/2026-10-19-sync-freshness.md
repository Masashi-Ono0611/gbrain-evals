# How fast does a commit become searchable? Sync freshness after gbrain's commit notifier (2026-10-19)

**Measured on October 19, 2026 by gbrain lane GBRA-133 (PR 2b.6); mirrored here the same day. This mirror reruns nothing.**

gbrain keeps notes as Markdown files in a git repository and indexes them in a database (PGLite or Postgres). After you commit a note, it is not searchable until a sync copies the change into the index. This report measures how long that takes when something already running (a *resident*: `gbrain serve`, `gbrain jobs work` or the autopilot daemon) notices the commit by itself, with `sync.on_commit` turned on.

gbrain v0.60.316.0 (master `25006f32`, PR [#7079](https://github.com/garrytan/gbrain/pull/7079)) added a *commit notifier* to every resident. It notices a new commit in one of two *detection modes*: **watch** (a filesystem watch on the git directory fires within a fraction of a second) and **poll** (it reads the checkout's HEAD every 3 s; used where file events do not work, such as network filesystems, and forced here with `GBRAIN_NOTIFIER_DETECTION=poll`). Every latency below names its mode.

## The finding

A single-file commit becomes keyword-searchable through a running `gbrain serve` in about 0.6 s at the median on a 10,000-page brain in watch mode, and in about 2 s (p95 3.2 to 3.6 s) in poll mode, on both engines and for both classic and managed sources. Before the notifier the same commit took 3.7 s on a managed brain and was never synced on a classic brain. The vector that hybrid search needs follows 0.3 to 0.5 s later on managed brains, and about 6 s later on classic brains.

Two things fall short:

- **After a 30 s embedding-provider outage, PGLite left about 3% of a 1,000-chunk backlog without vectors** (963 to 973 of 1,000 embedded per rep within 300 s; 318 chunks still missing at the end of the run). Postgres embedded all 1,000 every rep. Without an outage both engines embed every deferred chunk.
- **Several sources committed at once are synced one after another, about 2 to 3 s apart.** No source was starved (every source became visible in every rep), but with five sources on Postgres the last one waited 11.2 s at the median.

Idle cost rose with the notifier: one idle `gbrain serve` on Postgres now runs 31.5 transactions per 30 s on 6 connections, against 25.5 on 3 before.

## The test rig

- **Machine:** Capy cloud machines with 4 vCPUs (AMD EPYC), 16 GB RAM, Linux 6.1, Bun 1.4.3. Postgres cells ran on one machine, PGLite cells on a second of the same class, and the before/after pairs on a third (each pair back to back on that machine).
- **Database:** PGLite in-process, or Postgres 16 (`pgvector/pgvector:pg16`) in Docker on the same machine (loopback, no added latency).
- **Brain:** 10,000 generated notes (about 1 KB each, one wiki link each) in one git repository. Multi-source cells add sources of 1,000 notes each. All names are synthetic (`bench`, `bench2`, ...).
- **Probe:** after each commit the harness polls every 100 ms until `get_page` returns the new text and a keyword search finds the new token. On Postgres it reads through its own connection; on PGLite it reads through the serve's own MCP stdio, so PGLite times include one MCP round trip.
- **Embedding:** a loopback stub that answers like the OpenAI embeddings API (200 ms or 50 ms per call). Real provider keys are removed from every child process, so no paid call is possible.
- **Commits:** serve cells add a random 0 to 3 s to the gap between commits, so commits land at random points of the 3 s poll cycle.
- **Statistics:** p95 is shown only for cells with n ≥ 40; smaller cells show the maximum instead.

Product under test ("after"): gbrain v0.60.316.0, branch `gbra133-pr2b-bench` (product revision `4ba4c36f`; the branch adds only bench scripts). "Before (pre-2a)": gbrain v0.60.315.0 (master `2e9df779`, product revision `20bcf56b`), measured on the same machine as its pair. "Phase 1": GBRA-133's baseline on master v0.60.302.0 (`231a69de`), same machine class.

## Results

Times are seconds from the commit, shown as p50 / p95 / max (p95 only at n ≥ 40). All cells use 10,000 pages and `gbrain serve` (stdio) unless stated.

### Single-file commit, watch against poll (n = 40 each)

| Engine | Source | Watch: keyword-visible | Poll: keyword-visible | Before |
|---|---|---|---|---|
| Postgres | managed | **0.60 / 0.61 / 0.90** | 2.15 / 3.20 / 16.08 | 3.70 / 3.81 / 4.00 (Phase 1, n = 20) |
| Postgres | classic | **0.60 / 0.61 / 0.81** | 2.15 / 3.29 / 15.49 | never synced (Phase 1, 60 s timeout) |
| PGLite | managed | **0.62 / 1.07 / 1.49** | 1.93 / 3.53 / 3.79 | 3.67 / 3.77 / 4.05 (Phase 1, n = 20) |
| PGLite | classic | **1.06 / 1.12 / 1.24** | 2.07 / 3.63 / 3.87 | never synced (Phase 1) |

Targets set by the GBRA-133 plan on this machine class: watch p95 ≤ 2 s managed and ≤ 2.5 s classic, met everywhere; poll p95 ≤ 4 s, met everywhere (3.2 to 3.6 s). Each Postgres poll cell has one outlier, its first rep (16.1 s and 15.5 s): the serve was started 1.5 s after the previous serve was stopped, and it waited about 24 s for the stopped serve's notifier lease to expire before it took ownership. PGLite has no lease and shows no such outlier.

The PR 2a lane reported, on the same 4-core class at 10,000 pages in watch mode (engine and n as recorded by that lane; not re-measured here except the serve rows above): serve on a managed brain 3.7 s to 0.63 and 0.65 s p50, serve on a classic brain never to 0.60 to 1.07 s, a jobs worker alone 5.0 s to 0.64 s, and the autopilot daemon 266 s to 84 s.

### Keyword-visible and embedded (hybrid search), 200 ms embedding stub (n = 20)

"Embedded" means every chunk of the changed page carries a vector; on Postgres the harness also checks that a vector search aimed at that chunk returns the page (it did, at the same moment, in every rep).

| Engine | Source | Keyword-visible | Embedded | Before (pre-2a, same machine) |
|---|---|---|---|---|
| Postgres | managed | 0.62 / - / 0.93 | **0.93 / - / 1.43** | 3.71 / - / 4.21 keyword, 4.02 / - / 4.62 embedded |
| PGLite | managed | 0.65 / - / 1.18 | **1.11 / - / 2.16** | 3.68 / - / 4.14 keyword, 4.15 / - / 5.32 embedded |
| Postgres | classic | 0.62 / - / 0.63 | 6.63 / - / 6.95 | never synced |
| PGLite | classic | 1.08 / - / 1.22 | 6.50 / - / 7.42 | never synced |

A classic source now becomes keyword-searchable before it is embedded and gets its vector about 6 s later. In Phase 1 a classic sync embedded inline before the page was visible (1.31 s for both at 1,000 pages, manual sync), so classic hybrid search is about 5 s later than keyword search, while keyword search is never delayed by the provider.

### Deferred embeds under a backlog (1,000 changed files per commit, 50 ms stub, n = 10)

| Engine | Source | Variant | Keyword-visible | All 1,000 embedded | Reps fully embedded | Chunks without a vector at the end |
|---|---|---|---|---|---|---|
| Postgres | managed | healthy provider | 10.45 / - / 12.81 | 89.3 / - / 91.7 | 10 of 10 | 0 |
| Postgres | classic | healthy provider | 5.58 / - / 7.92 | 78.1 / - / 90.0 | 10 of 10 | 0 |
| PGLite | managed | healthy provider | 6.21 / - / 7.21 | 129.7 / - / 144.3 | 10 of 10 | 0 |
| PGLite | classic | healthy provider | 1.99 / - / 4.56 | 92.4 / - / 95.5 | 10 of 10 | 0 |
| Postgres | managed | 500 errors for 30 s after each commit | 11.60 / - / 15.79 | 113.1 / - / 191.6 | 10 of 10 | 0 |
| PGLite | managed | 500 errors for 30 s after each commit | 6.62 / - / 7.32 | not reached in 300 s | **0 of 10** (963 to 973 per rep) | **318** |
| Postgres | managed | keyless brain | 10.54 / - / 12.39 | not applicable | - | - |
| PGLite | managed | keyless brain | 4.60 / - / 6.97 | not applicable | - | - |

The keyless rows point `OPENAI_BASE_URL` at a counting stub with no key configured: **0 requests** reached it in 10 commits of 1,000 files on either engine. Every embedding run sends one provider request per chunk (10,000 requests for 10,000 chunks), so drain time is close to one call after another.

### Starting `gbrain serve` after a commit (n = 20)

The commit is made while no serve runs; the harness then starts `gbrain serve` (stdio) and times start to keyword-visible. On PGLite that includes the MCP handshake (0.8 s), because the probe reads through the serve.

| Engine | Source | Serve start to visible | Commit to visible | Before (pre-2a, same machine) |
|---|---|---|---|---|
| Postgres | managed | **1.55 / - / 1.77** | 1.85 / - / 2.07 | 7.34 start to visible |
| Postgres | classic | 1.22 / - / 1.39 | 1.52 / - / 1.69 | not measured |
| PGLite | managed | **1.94 / - / 2.38** | 2.24 / - / 2.68 | 7.38 start to visible |
| PGLite | classic | 2.04 / - / 2.25 | 2.34 / - / 2.55 | not measured |

### Several sources at once (one single-file commit to every source at the same moment, n = 10)

| Engine | Sources | Residents | Last source visible | Per-source p50, in sync order | Before (pre-2a) |
|---|---|---|---|---|---|
| Postgres | 3 managed | serve | 5.19 / - / 6.70 | 0.66, 2.33, 5.19 | 8.28 last; 3.85, 5.27, 8.28 |
| Postgres | 5 managed | serve | 11.18 / - / 12.68 | 0.60, 2.36, 5.32, 8.25, 11.18 | not measured |
| Postgres | 3 classic | serve | 5.29 / - / 6.59 | 0.59, 2.43, 5.29 | not measured |
| Postgres | 3 managed | serve, jobs worker, autopilot | 5.30 / - / 10.09 | 0.59, 3.81, 4.64 | not measured |
| PGLite | 3 managed | serve | 5.07 / - / 6.80 | 0.73, 2.30, 5.07 | not measured |
| PGLite | 5 managed | serve | 5.26 / - / 10.68 | 0.72, 1.71, 2.44, 3.32, 5.26 | not measured |
| PGLite | 3 classic | serve | 5.24 / - / 5.46 | 1.13, 2.35, 5.24 | not measured |

All detection was watch. No source was skipped or starved. Sources sync one at a time, and the gap between them (about 2 to 3 s on Postgres) is close to the 3 s poll interval, which suggests the next source waits for the notifier's next poll after the previous sync finishes. The notifier is the right place to look; this report does not prove the cause.

### Idle cost (no commits, `sync.on_commit` on, ten 30 s windows after a 60 s warm-up)

Transactions come from `pg_stat_database` for the brain's database, connections from `pg_stat_activity` sampled each second, and CPU from `/proc` (each resident plus its children).

| Engine | Residents | Sources | Transactions per 30 s, p50 / max | Connections | CPU seconds per minute, p50 | Before (pre-2a) |
|---|---|---|---|---|---|---|
| Postgres | serve | 1 | 31.5 / 45 | 6 | serve 0.9 | 25.5 tx, 3 connections, serve 1.0 |
| Postgres | serve | 3 | 37.5 / 53 | 6 | serve 1.7 | not measured |
| Postgres | jobs worker | 1 | 58 / 66 | 9 | jobs 0.8 | not measured |
| Postgres | serve, jobs worker, autopilot | 3 | 272.5 / 496 | 27 (max 29) | serve 1.6, jobs 0.7, autopilot 1.2 | 180.5 tx, 18 connections |
| PGLite | serve | 1 | - | - | serve 1.2 | not measured |
| PGLite | serve | 3 | - | - | serve 1.8 | not measured |

The before/after pair for three residents was measured on the third machine, where the after side read 245.5 transactions and 29 connections; the table's after row comes from the Postgres machine.

## A nightly regression gate

gbrain gates three of these cells nightly (`.github/workflows/sync-freshness-gate.yml` on the gbrain branch): watch mode, single-file commit, 10,000 pages, through `gbrain serve`, for Postgres managed, PGLite managed and Postgres classic. The gate value is the p50 of 10 reps after one discarded warm-up rep, and a cell fails above its committed baseline plus 25%. It runs on `ubicloud-standard-4` runners, and the baseline was recorded on that runner class.

Before committing it, the gate procedure ran 25 times (5 runs on each of 5 fresh Ubicloud standard-4 VMs, fresh brains every run). Per-run p50s ranged 450 to 530 ms (Postgres managed), 424 to 497 ms (PGLite managed) and 352 to 404 ms (Postgres classic), a largest-to-smallest ratio of 1.18 or less, with coefficients of variation of 0.059, 0.046 and 0.061. Using every run as the baseline for every other run (600 ordered pairs per cell), no pair failed at +25%. A manual managed sync cell was tested the same way and left out of the gate: its p50 moved with the VM (852 to 1,254 ms) and 52 of 600 pairs would have failed. The per-run values are in [`raw/gate-stress/p50-per-run.json`](2026-10-19-sync-freshness/raw/gate-stress/p50-per-run.json).

## What to use and what to avoid

- **Turn on `sync.on_commit` and keep a resident running** if you want notes searchable within a second or two of a commit. Watch mode is the expected case on a local disk.
- **On a network filesystem or a bind mount**, expect poll mode: about 2 s at the median and under 4 s at p95.
- **If you rely on hybrid search on a classic source**, expect the vector about 6 s after keyword search finds the note.
- **On PGLite with an unreliable embedding provider**, check for unembedded chunks after an outage; this run left about 3% of a backlog without vectors.
- **Many sources on one host** are synced one after another, so the last of five may wait about 11 s on Postgres.

## Limits of this result

- Synthetic notes of about 1 KB on a local database; no network latency, no large pages, no production brains.
- One machine class. The before/after pairs were measured back to back on one machine; Phase 1 rows come from earlier runs on the same class.
- The 100 ms probe quantizes Postgres times to about 0.1 s, which also inflates the coefficient of variation of the watch cells (0.14).
- PGLite times include an MCP round trip through the serve.
- The PGLite outage result is "not embedded within 300 s plus a 20 s settle"; the run did not wait longer to see whether a later retry would finish.
- PR 2a's jobs-only and autopilot numbers are quoted from that lane, not re-measured here.

## Reproduce and inspect

In a gbrain checkout of branch `gbra133-pr2b-bench` with Docker on Linux (no keys needed):

```bash
ENGINE=postgres scripts/bench/sync-freshness-matrix.sh pr2b6 <work-dir>
ENGINE=pglite   scripts/bench/sync-freshness-matrix.sh pr2b6 <work-dir>
scripts/bench/sync-freshness-matrix.sh pr2b6-before <work-dir> <checkout of gbrain 2e9df779>
bun scripts/bench/sync-freshness.ts --report <work-dir>/results
bun scripts/bench/sync-freshness-gate.ts --write-baseline <file> --machine-class <class>   # one gate run
```

A full Postgres set takes about 2.5 hours and a PGLite set about 3 hours on a 4-core machine. [`raw/`](2026-10-19-sync-freshness/raw/) holds the cell JSON for every row (`after-pg/`, `after-pglite/`, `before-after/` with `HEAD_20bcf56b` for pre-2a, `gate-stress/`), with machine paths removed; per-rep values are in each file's `reps`.
