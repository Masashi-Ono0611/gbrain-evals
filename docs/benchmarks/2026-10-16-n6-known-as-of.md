# N6 with gbrain's recorded-time reads (`known_as_of`, belief ledger W2): no leaks or oracles after one fix (2026-10-16)

gbrain [#6850](https://github.com/garrytan/gbrain/pull/6850) (W2, draft) adds `known_as_of` to `get_page` and `get_versions`: the page as the brain had recorded it at an instant, read from the belief ledger. N6 asks whether a remote caller can read anything the brain marks as not theirs. This run checks the new params through N6's own fuzz, in process on PGLite and over the real HTTP transport on Postgres.

## What N6 does with the new params

When an op has an optional `known_as_of` param, the runner adds two variants: `known_as_of` and `known_as_of+source_id=beta`. Each passes an instant taken after seeding, sets `diff` and `include_body`, and leaves out the widening flags except `include_deleted`. On a build with recorded-time reads, `seed` turns on the belief ledger for every source before any write, so the history being probed is real.

## Results

| Run | gbrain | Callers | Content leaks | Existence leaks | Oracles | Verdict |
|---|---|---|---|---|---|---|
| N6 in process, PGLite | `cbaad1f0` | six remote | 0 | 0 | 0 | pass |
| N6 Postgres over HTTP | `d722ddf0` | none, invalid, expired, scoped, owner | 0 | 0 | **16** | **fail** |
| N6 Postgres over HTTP | `4911c463` | same | 0 | 0 | 0 | pass |
| N6 in process, PGLite | `4911c463` | six remote | 0 | 0 | 0 | pass |

All 16 oracles at `d722ddf0` were `known_as_of` variants of `get_page` and `get_versions` for the owner principal, a remote OAuth client federated over two sources. A private page refused `page_not_found`, but a slug that was never written refused `coverage_from`. The read picked its source from the ledger rows that name the slug, so a private page's rows changed which source was chosen, and with it the error. gbrain `4911c463` fixes this: a remote caller's source lookup counts only world-visible events of pages it can see now, and a coverage or proof refusal about a page it cannot see becomes `page_not_found`. A unit cell in gbrain fails without the fix.

In process on PGLite, 90 of the 180 `known_as_of` probes carry signal. The sampled probes without signal are `source_id=beta` variants, refused `permission_denied` as intended. The Postgres-over-HTTP run covers all 155 mandatory cells, with 3,024 probes carrying signal in both runs and at most 9 pooled connections.

Hermetic, no provider key, $0. Receipts: [PGLite cbaad1f0](2026-10-16-n6-known-as-of/n6-pglite-cbaad1f.json), [Postgres HTTP d722ddf0](2026-10-16-n6-known-as-of/n6-postgres-http-d722ddf.json), [Postgres HTTP 4911c463](2026-10-16-n6-known-as-of/n6-postgres-http-4911c46.json), [PGLite 4911c463](2026-10-16-n6-known-as-of/n6-pglite-4911c46.json).

## Reproduce

```bash
bun eval/runner/n6-visibility-fuzz.ts --gbrain <gbrain checkout>@<ref> --output <dir>
bun eval/runner/n6-postgres-http.ts --pg-url <admin url> --gbrain <gbrain checkout>@<ref> --output <dir>
```
