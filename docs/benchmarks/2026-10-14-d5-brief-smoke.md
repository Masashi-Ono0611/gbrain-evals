# D5 brief parameters: Cat 40 smoke on gbrain #6703 (2026-10-14)

garrytan/gbrain#6703 adds two optional parameters, `counterparty` and `intent`, to `context_pack`, for the pulled
proactive brief. Callable surfaces `full` and `verbs` list them; callable `starter` does not.

This smoke compared master `14ea3e2e` with the PR head `e6575894` on Opus 5.5, Sonnet 5.5 and gpt-6.1-sol. It ran
10 Cat 40 tasks per model per build (60 cells) on the arm with callable `full` and advertised `starter`, plus an N6
visibility fuzz on both builds. It was preregistered in
[2026-10-14-d5-brief-smoke-preregistration.md](2026-10-14-d5-brief-smoke-preregistration.md).

## The finding

The new tool text changed nothing the models did:

| | master | d5 |
|---|---|---|
| Success | 29/30 | 30/30 |
| Tool calls, 9 tasks without E01: Opus | 36 | 38 |
| Tool calls, 9 tasks without E01: Sonnet | 46 | 45 |
| Tool calls, 9 tasks without E01: Sol | 44 | 53 |

No cell passed `counterparty` or `intent`, including E01, the renewal-brief task where a brief was defensible. There
were 0 output leaks and 0 unsafe writes.

The pulled brief leaked nothing in the N6 fuzz: `context_pack` had 0 findings in 540 probes on the head, including
calls that name the protected person as `counterparty`.

The frozen verdict is still **regresses, on L1 only**. L1 needs 0 N6 findings of any kind on the head. Both builds
show the same 4 existence findings in `list_write_conflicts` (#6643, already on master), where the op echoes a foreign
`source_id` the caller named and returns no rows. #6703 doesn't touch that op.

Spend was $6.78 of a new $10 ledger. Details, per-cell data and ledger run ids are in
[2026-10-14-d5-brief-smoke/VERDICT.md](2026-10-14-d5-brief-smoke/VERDICT.md).
