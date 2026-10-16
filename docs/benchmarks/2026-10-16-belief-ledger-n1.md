# N1 knowledge update with gbrain's belief ledger on: unchanged at 388/388, 0 stale (2026-10-16)

gbrain's belief ledger ([#6806](https://github.com/garrytan/gbrain/pull/6806), W1, not yet released) records every change to what a brain asserts: a fact added, revised or withdrawn, a take, a link. It is off per source until `gbrain beliefs enable` runs. The ledger records changes and nothing reads it to answer a query, so turning it on must not change any answer gbrain gives. Probe 40 of the ledger design checks this: N1 must stay at 388/388 current values and 0 stale values served with the ledger on.

It does. On the lane C build `b3db5af98` of #6806, N1 gives the same result with the ledger off and on, on both engines and all three transports, with nothing failing, leaking or lost.

## The concrete case

N1 writes a fictional fact, for example a company's head count, then updates it. It then asks for the value after the update, after a server restart, after a full reimport from the Markdown vault and while writes run in parallel. A correct answer is the newest value. A stale answer is an older value served as current. N1 also asks for the history, which should keep the earlier value; for private values that a scoped caller must not see; and for negative controls, facts that were never written.

With the ledger on, every one of those writes also appends ledger events in the same transaction. A ledger bug that broke or slowed a write, changed what gets stored, or let a publication fail would show up as a wrong, stale or missing answer, a lost write or a system error.

## The experiment and results

- **gbrain:** the lane C build of #6806 at [`b3db5af98`](https://github.com/garrytan/gbrain/commit/b3db5af98737d25d4e5f9bd0da1287b14b57a9c9) (CLI 0.60.253.0), loaded as a `--gbrain` overlay. The declared pin in `package.json` was `77cf8e1116e9`; both receipts record the pin and the loaded head (`execution.product.loaded_git_head`).
- **Benchmark:** N1 0.5.0, generator `n1-knowledge-update-gen@1`, seed 11, 897 scored tasks per arm. Hermetic: no provider key, no embedding model, System One off, $0.
- **Cells:** PGLite and Postgres, each over the trusted local CLI, stdio MCP and HTTP MCP: three cells per engine, six per arm.
- **Arms:** ledger off (the default) and ledger on (`EVAL_BELIEF_LEDGER=1`). In the on arm each cell runs `gbrain beliefs enable --source vault` right after the vault becomes the default source and before any page is written. It exits 0 in all six cells ("0 page(s) baselined; certified (managed source)"), so the ledger records every write the cell makes. The off receipt has no `beliefs-enable` step.

| Measure (per engine, 3 cells) | Ledger off, PGLite | Ledger off, Postgres | Ledger on, PGLite | Ledger on, Postgres |
|---|---|---|---|---|
| Current value correct | 388 / 388 | 388 / 388 | 388 / 388 | 388 / 388 |
| Stale values served | 0 | 0 | 0 | 0 |
| History retained | 385 / 385 | 385 / 385 | 385 / 385 | 385 / 385 |
| Negative controls passed | 124 / 124 | 124 / 124 | 124 / 124 | 124 / 124 |
| Private value leaks | 0 | 0 | 0 | 0 |
| Acknowledged writes lost | 0 | 0 | 0 | 0 |
| System errors | 0 | 0 | 0 | 0 |

Both arms pass every preregistered N1 rule. Per-cell and per-checkpoint counts (updated, restart, reimport, concurrent) are identical between the arms.

Each arm ran once, one after the other on one 4-core machine. The ledger-on cells took 0.7 to 5% longer, for example 299.8 s against 292.5 s on the PGLite CLI cell, and the PGLite call latency was p50 66 ms / p95 1,427 ms against 65 / 1,412 ms. One run per arm can't separate a difference that small from run-to-run noise, so this is not a cost measurement. The ledger's write cost is measured in the ledger design, section 9.

## What to use and what to avoid

Turning the ledger on for a source does not change what N1 measures: current values, history, privacy and write durability. N1 doesn't test what the ledger adds (event history, coverage and drift). gbrain's own ledger tests cover those. This result is for the W1 head named above. Rerun it when the release build of #6806 is pinned.

## Reproduce and inspect

From the repository root, with Postgres at `--pg-url` and a gbrain checkout at `b3db5af98`:

```bash
bun eval/runner/n1-knowledge-update.ts --gbrain <gbrain checkout>@b3db5af98 --engines pglite,postgres --output off
EVAL_BELIEF_LEDGER=1 bun eval/runner/n1-knowledge-update.ts --gbrain <gbrain checkout>@b3db5af98 --engines pglite,postgres --output on
```

Each arm writes `<dir>/receipt.json`, takes about 5 minutes and costs $0. The hook is in `eval/runner/lifecycle/slice.ts`, and `test/eval/lifecycle-belief-ledger-arm.test.ts` checks it.

Receipts: [ledger off](2026-10-16-belief-ledger-n1/n1-receipt-ledger-off-b3db5af.json), [ledger on](2026-10-16-belief-ledger-n1/n1-receipt-ledger-on-b3db5af.json).

The receipts were scrubbed with `bun eval/runner/receipt.ts scrub <receipt.json>`. The only change is the cells' scratch paths: `/tmp/` became `<tmp>/` in 21 strings per receipt (each cell's database path, vault path and `gbrain init` output). The sha256 of the receipts as the runner wrote them were `eefa6616d2809cd3f8fb16e6675bf07371c479d28ee978c74d6aa7d4fe05bf22` (ledger off) and `c92fdbe5e70a103c24a3bdb3e7059361442e04bf1acc32168f8bf53033060876` (ledger on). The N1 runner now scrubs home and temp paths itself before writing a receipt, as the N14 runner does.
