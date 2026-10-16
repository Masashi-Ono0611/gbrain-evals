# N6 with gbrain's weekly belief diff (`delta {beliefs: true}`, belief ledger W4): 12 leaks and 20 oracles found and fixed before review (2026-10-16)

gbrain's wave 4a branch adds `beliefs: true` to `delta`: each belief that changed in the window, with its value before and after, the event that caused the change and a pointer to the evidence, read from the belief ledger. `gbrain beliefs changes` is its CLI twin and calls the same op on a remote brain. N6 asks whether a remote caller can read anything the brain marks as not theirs. This run checks the new param through N6's own fuzz, in process on PGLite and over the real HTTP transport on Postgres.

## What N6 does with the new param

When `delta` exposes `beliefs`, the runner adds a `beliefs` variant that sets `beliefs: true` with a `since` before seeding, so the window holds the whole seeded history. Seeding turns the belief ledger on for every source before any write, so the history probed is real. Each probe records what the trusted local caller and the remote caller got: `history` (at least one change) or `empty`. A probe tests the diff only when the trusted caller read changes and the probe carries signal; the receipt counts these as `real_history_signal`. The HTTP verdict fails when a build exposes `beliefs` and no probe reads real history. The oracle view masks `beliefs.until`, which is the request instant and differs on every call by design.

## Results

| Run | gbrain | Callers | Content leaks | Existence leaks | Oracles | Verdict |
|---|---|---|---|---|---|---|
| N6 in process, PGLite | `41e2900f` | six remote | **12** | 0 | **20** | **fail** |
| N6 Postgres over HTTP | `41e2900f` | none, invalid, expired, scoped, owner | **12** | 0 | **18** | **fail** |
| N6 in process, PGLite | `0ed5ae79` | six remote | 0 | 0 | 0 | pass |
| N6 Postgres over HTTP | `0ed5ae79` | same | 0 | 0 | 0 | pass |

| Run | `beliefs` probes | Real-history signal | Trusted: history / empty | Remote: history / empty |
|---|---|---|---|---|
| PGLite in process | 36 | 28 | 32 / 4 | 16 / 20 |
| Postgres over HTTP | 34 | 28 | 32 / 2 | 16 / 18 |

The `beliefs` counts are the same at both commits. The leaks at `41e2900f` were held Takes: `delta {beliefs: true}` passed every world-visibility Take to remote callers, both as a revised take and in the creation body of a page created in the window, while the Takes surfaces show remote callers only the holders they may read. gbrain `1d7ce5b3` applies that holder rule to the history reader and to the creation body. A unit cell in gbrain fails with either filter reverted. The oracles were `beliefs.until` timestamps alone; the runner now masks it.

The final head `0ed5ae79` also carries the fixes from gstack `/review` of the branch, several of them privacy fixes on the same surface: remote reads page on the rows each history page scanned (a remote page is filtered after its SQL `LIMIT`), a creation or earlier body never shows a claim made private later, remote creation entries no longer carry counts of beliefs the caller cannot read, and relationship-note upper bounds count only the evidence the caller's scope counts. Each has a gbrain unit cell that fails without it.

The Postgres-over-HTTP run at `0ed5ae79` covers all 155 mandatory cells with at most 8 pooled connections. In process, N6 covers 33 of 79 read ops. Both runs read the gbrain tree through `--gbrain`; each receipt records the overlay commit and tree, and the package pin is unchanged. gbrain's branch is not released yet; the rows will be rerun from the release tag.

Hermetic, no provider key, $0. Receipts: [PGLite 41e2900f](2026-10-16-n6-delta-beliefs/n6-pglite-41e2900.json), [Postgres HTTP 41e2900f](2026-10-16-n6-delta-beliefs/n6-postgres-http-41e2900.json), [PGLite 0ed5ae79](2026-10-16-n6-delta-beliefs/n6-pglite-0ed5ae7.json), [Postgres HTTP 0ed5ae79](2026-10-16-n6-delta-beliefs/n6-postgres-http-0ed5ae7.json).

## Reproduce

```bash
bun eval/runner/n6-visibility-fuzz.ts --gbrain <gbrain checkout>@<ref> --output <dir>
bun eval/runner/n6-postgres-http.ts --pg-url <admin url> --gbrain <gbrain checkout>@<ref> --output <dir>
```
