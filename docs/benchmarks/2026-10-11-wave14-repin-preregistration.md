# Preregistration: the regression check for the re-pin from gbrain v0.60.126.0 to the wave 14 release (2026-10-11)

Frozen on October 11, 2026, in its own commit, before any run at the new pin. Nothing below changes after a run; a
later change is a dated amendment at the end.

## The question

gbrain-evals pins gbrain master `8a3eedeacb6e52da5b413502019692db80c5cc5d` (v0.60.126.0). The pin moves to the gbrain
release published after wave 14 lands, v0.60.169.0. That release does not exist yet, so the check runs now against
gbrain master `3001fd9a57e3603f1fd3bee3e5d74e0b7b27cbb2` (v0.60.166.0), 1,010 commits and 40 first-parent merges after
the pin. The range includes memory trust (#6396), the verbatim-probe fixes (#6391), scoped vector search (#6380), the
content-repair lane (#6384), the memory proof wave integration (#6066), efficiency waves 5 to 11, and waves 13 and 14 so
far. The full list is `git log --first-parent 8a3eedeac..3001fd9a5` in gbrain.

Does anything this repository measures get worse, and which merge is responsible when it does? Evidence class:
regression check.

**Before** is gbrain `8a3eedeac`. **After** is gbrain `3001fd9a5`. Both are the installed dependency (`package.json`
pin), on Bun 1.4.2, with the same gbrain-evals tree apart from `package.json` and `bun.lock`. That tree removes `held`
from the memory trust rules (Cats 37 to 39), as `eval/registry.ts` asks the re-pinning commit to do, so those three
categories gate at both pins. The test suite and one N12 run on the Capy machine at `3001fd9a5`, used to bring the
harness up to the new pin (a renderer for gbrain's new `plain-role-no-time` conversation pattern and four tests that
assumed the old pin), are development runs and are not counted.

## What is rerun, and why

README's results table says the correctness rows "come from keyless checks on synthetic worlds with generated answer
keys, rerun at every pin". Those rows, and how each is rerun here:

| README row | Rerun |
|---|---|
| Serving the new value after an update (N1) | full N1, PGLite and Postgres, every interface (step 8); N1-ci in the offline tier |
| Nothing left behind after `forget` (N5) | full N5, PGLite and Postgres, every interface (step 8); N5-ci in the offline tier |
| Private pages reaching agent or remote callers (N6, N8, N6 on Postgres over HTTP) | N6 and N8 in the offline tier and attested against their gate preregistration (step 10); N6 on Postgres over real HTTP with its negative control (step 9) |
| Keeping speaker and time across chat export formats (N12) | N12 at seed 12 in the offline tier and at seed 7 (step 2) |
| The bug-ledger sentence | every ledger repro (step 3), the memory trust repros (step 7) |
| Known limits: Cat7-1 | Cat 7 in the offline tier and the Cat7-1 repro (steps 1, 3, 6) |

The offline tier, the ledger repros and the preregistered checks also run, as at every earlier re-pin. Rows that need
provider calls (LongMemEval, concept search, relationship paraphrases, PrecisionMemBench, the contradiction judge, the
takes classifier, Cat 40, Cat 41, fence repair, slug-conflict judgment, Cat 35, timeline extraction) keep the commits
they were measured at and are not rerun. The N2 row's 149 of 150 comes from a paid judge arm (about $10 at the
default judge model); it is listed for approval, not run.

## What runs

On two identical Ubicloud `standard-16` VMs started together in the same location, one per pin, each with a fresh copy
of the tree, `bun install --frozen-lockfile`, Docker with the digest-pinned `pgvector/pgvector` image of the N6 Postgres
report, and no provider key in the environment (`2026-10-11-wave14-repin/vm/setup.sh`, `vm/run.sh`):

1. The offline tier, `GBRAIN_REPO=node_modules/gbrain bun eval/runner/all.ts --tier offline`.
2. N12 at seed 7.
3. Every command in `2026-10-03-wave8-f1-repin/repros-109b992.txt`, the Cat7-1 repro and the N1-7 repro
   (`2026-10-06-followups-repin/run-repros.ts`).
4. The wave 8 and Foundations 1 checks (`2026-10-03-wave8-f1-repin/checks/run-all.ts`).
5. The 2026-10-04 operator-wave checks and the consented `embed-budget-stop` variant, which is the one that counts.
6. The Cat7-1 repro three more times.
7. The fixed memory trust repros 37-1, 37-2 and 37-5 (`eval/runner/memory-trust/repro.ts`) against the installed
   gbrain.
8. Full N1 and N5 on PGLite and Postgres, every interface, at their default seeds.
9. N6 on Postgres over real HTTP, attested against its preregistration, and its negative control.
10. N8 and N6 attested against the N8 privacy gate preregistration.

No corpus is regenerated. No paid tier, no sealed set.

## What counts as a regression

The rules of the [2026-10-04 regression check](2026-10-04-operator-wave-repin-preregistration.md#what-counts-as-a-regression)
apply unchanged, with `8a3eedeac` as before and `3001fd9a5` as after:

1. A category whose promotion rules pass at `8a3eedeac` fails them at `3001fd9a5`, or a category that completed errors,
   times out or skips.
2. A deterministic keyless metric moves away from gold. A move a gbrain CHANGELOG line for v0.60.127.0 to v0.60.166.0
   describes as intended is still reported, and counts as a regression if it breaks a rule.
3. A repro or check that passed at `8a3eedeac` fails at `3001fd9a5`. For steps 8 to 10: a rule that passes at
   `8a3eedeac` fails at `3001fd9a5`, or a count of leaks, stale values, lost writes or prohibited outputs rises.
4. Latency (Cat 7, Cat 28): a gate failure; a p50 slowdown above 25% with both runs inside the gate is a suspected
   regression and counts only if a paired rerun on fresh identical VMs (`vm/cat7-repeat.sh`) repeats it.

Expected moves named in advance, which are not regressions: Cats 37 to 39 fail at `8a3eedeac`, where the feature they
test does not exist, and must pass at `3001fd9a5`; the memory trust repros cannot pass at `8a3eedeac`; Cat 12 and N6
count new operations; N12 may register new conversation patterns.

## Cat7-1

The ledger entry stays open under its frozen closure rule
([2026-10-04 coverage preregistration](2026-10-04-operator-wave-repin-coverage-preregistration.md)): it closes as fixed
only when Cat 7's `get_timeline` p50 at 1,000 pages on the after VM is within 25% of the 0.045 ms pre-Foundations-1
baseline (at most 0.056 ms), and the repro passes.

## What happens to a regression

A keyless repro under `2026-10-11-wave14-repin/repros/` that exits 1 while it reproduces, a bisection over the
first-parent merges in `8a3eedeac..3001fd9a5`, and a ledger entry naming the merge. No paid arm.

## What changes on README

A row moves to the new pin only when its rerun passes its rules at the new pin. A changed number replaces the old one,
with its reason in the report and the changelog. Rows not rerun keep their commits. A feature merged after `8a3eedeac`
(memory trust, the verbatim-probe fixes, scoped vector search, the memory proof wave) enters "What gbrain does" or
"Current results" only on evidence measured at a recorded commit inside the new pin's history, or on a keyless rerun at
the new pin.

## The final SHA

When v0.60.169.0 is published, an amendment names its commit before any run there. Steps 1 to 10 then run on two
identical VMs started together, one at `3001fd9a5` and one at the release, under the same rules with `3001fd9a5` as
before. The pin, README and the report name the release only if nothing regresses.

## Budget

None: no paid request. The VMs are compute only.

## Amendments
